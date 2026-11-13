"""Auxiliary normal maps and sole metadata; never rewrites source sprite pixels.

Normals use broad alpha silhouettes, not painted RGB brightness/ink strokes.
Contact metadata is only for standing/walking; never normalizes action frames.
"""
from pathlib import Path
import json, hashlib
import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets/characters/green_three_walk'
OUT = ROOT / 'assets/characters/volume_support'
REVIEW = ROOT / 'artifacts/hero-volume-review'
COUNTS = {'right':26,'up':29,'down':24}

def normal_image(image):
    alpha = np.asarray(image)[...,3]
    mask = (alpha > 90).astype(np.uint8)
    distance = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    # Wide, low relief. Saturation prevents a balloon/pillow at the trunk center.
    height = 20.0 * (1.0 - np.exp(-distance/26.0))
    height = cv2.GaussianBlur(height, (0,0), 4.0)
    dy,dx = np.gradient(height)
    n = np.stack([-dx,dy,np.ones_like(dx)],axis=-1)
    n /= np.linalg.norm(n,axis=-1,keepdims=True)
    encoded=np.clip((n*.5+.5)*255,0,255).astype(np.uint8)
    return Image.fromarray(encoded,'RGB')

def sole_points(image):
    a=np.asarray(image)[...,3]>140
    # Extract separate shoe intervals close to the baseline; lifted shoes remain lifted.
    bottom=np.where(a.any(axis=1))[0][-1]
    feet=a.copy(); feet[:max(600,bottom-92)]=False
    count,labels,stats,centers=cv2.connectedComponentsWithStats(feet.astype(np.uint8),8)
    candidates=[]
    for k in range(1,count):
        x,y,w,h,area=stats[k]
        if area<100 or w<9: continue
        ys,xs=np.where(labels==k)
        end=int(ys.max())+1
        near=xs[ys>=end-5]
        candidates.append({'x':float(np.median(near)), 'y':float(end), 'width':int(w), 'area':int(area)})
    candidates=sorted(candidates,key=lambda p:p['area'],reverse=True)[:2]
    candidates.sort(key=lambda p:p['x'])
    # Sole samples across lower outline make the depth check independent of a toe landmark.
    outline=[]
    for x in range(0,image.width,4):
        ys=np.where(a[600:,x:x+4].any(axis=1))[0]
        if len(ys): outline.append([float(x+2),float(600+ys[-1]+1)])
    return {'feet':candidates,'sole':outline}

def import_settings(path):
    # Linear RGB vectors, no normal-channel repacking, no mipmaps or lossy compression.
    res='res://'+path.relative_to(ROOT).as_posix()
    path.with_suffix('.png.import').write_text('[remap]\nimporter="texture"\ntype="CompressedTexture2D"\n\n[deps]\nsource_file="'+res+'"\n\n[params]\ncompress/mode=0\ncompress/normal_map=2\nmipmaps/generate=false\nprocess/fix_alpha_border=false\ndetect_3d/compress_to=0\n',encoding='utf8')

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    contacts={}; hashes={}; rows=[]
    for direction,count in COUNTS.items():
        walk=[]; thumbs=[]
        for page in range(2):
            path=SOURCE/f'{direction}_{page:02}.png'
            atlas=Image.open(path).convert('RGBA'); mapped=Image.new('RGB',atlas.size,(128,128,255))
            hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
            for local in range(min(16,count-page*16)):
                frame=page*16+local; x=local%4*512; y=local//4*768
                im=atlas.crop((x,y,x+512,y+768))
                mapped.paste(normal_image(im),(x,y)); data=sole_points(im);walk.append(data)
                tile=Image.new('RGB',(144,190),(50,57,61)); thumb=im.resize((120,180),Image.Resampling.NEAREST)
                tile.paste(thumb,(12,5),thumb); d=ImageDraw.Draw(tile)
                d.text((3,3),str(frame),fill='white')
                for p in data['feet']:
                    px=12+p['x']*120/512;py=5+p['y']*180/768
                    d.ellipse((px-3,py-3,px+3,py+3),fill='red' if p['y']>=720 else 'cyan')
                thumbs.append(tile)
            target=OUT/f'{direction}_{page:02}_normal.png';mapped.save(target);import_settings(target)
        contacts[f'walk_{direction}']=walk
        path=SOURCE/f'{direction}_idle.png';im=Image.open(path).convert('RGBA')
        hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
        contacts[f'idle_{direction}']=[sole_points(im)]
        target=OUT/f'{direction}_idle_normal.png';normal_image(im).save(target);import_settings(target)
        sheet=Image.new('RGB',(144*10,190*3),(25,29,32))
        for i,t in enumerate(thumbs):sheet.paste(t,((i%10)*144,(i//10)*190))
        sheet.save(REVIEW/f'{direction}-sole-review.png')
    (OUT/'contacts.json').write_text(json.dumps(contacts,indent=2),encoding='utf8')
    (REVIEW/'sprite-source-hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf8')
    print('Prepared 79 walking and 3 idle normal frames; source atlases unchanged.')

if __name__=='__main__':main()
