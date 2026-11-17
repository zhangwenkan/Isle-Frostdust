"""Local material crops from the supplied painting; no model geometry."""
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import numpy as np,json,hashlib
root=Path(__file__).resolve().parents[1]
src=root/'assets/layered_island/textures'
out=root/'assets/layered_island/spatial_textures';out.mkdir(exist_ok=True)
land=Image.open(src/'land.png').convert('RGB')
regions={'sand':(545,1265,765,1305),'rock':(325,977,418,1070),
         'grass':(160,896,302,930),'path':(645,836,745,883),
         'step':(593,958,721,974)}
means={'sand':(.67,.58,.42),'rock':(.42,.41,.34),'grass':(.31,.34,.20),'path':(.54,.50,.38),'step':(.49,.47,.37)}
manifest={}
for name,box in regions.items():
    im=land.crop(box).resize((256,256),Image.Resampling.LANCZOS)
    a=np.asarray(im,dtype=np.float32)/255
    blur=np.asarray(im.filter(ImageFilter.GaussianBlur(20)),dtype=np.float32)/255
    lum=blur.mean(axis=2,keepdims=True)
    # Reduce the source's large baked highlights before applying scene lighting.
    correction=np.clip(lum.mean()/np.maximum(lum,.08),.76,1.28)
    a=np.clip(a*(.15+.85*correction),0,1)
    # Keep brush detail but remove the large fixed highlight which would
    # otherwise be repeated as a medallion across every new face.
    low=np.asarray(Image.fromarray((a*255).astype('uint8')).filter(ImageFilter.GaussianBlur(7)),dtype=np.float32)/255
    detail=(a-low)*(.6 if name=='sand' else .82)
    a=np.clip(np.array(means[name])+(low-low.mean(axis=(0,1)))*(.95 if name=='rock' else .32)+detail,0,1)
    im=Image.fromarray((a*255).astype('uint8'))
    im=ImageEnhance.Color(im).enhance(.84)
    # Blend only the two outer borders. No mirrored/quilted motifs.
    a=np.asarray(im,dtype=np.float32).copy()
    for k in range(20):
        weight=(1-k/20)**2;average=(a[:,k]+a[:,-1-k])*.5
        a[:,k]=a[:,k]*(1-weight)+average*weight;a[:,-1-k]=a[:,-1-k]*(1-weight)+average*weight
    for k in range(20):
        weight=(1-k/20)**2;average=(a[k]+a[-1-k])*.5
        a[k]=a[k]*(1-weight)+average*weight;a[-1-k]=a[-1-k]*(1-weight)+average*weight
    tile=Image.fromarray(np.clip(a,0,255).astype('uint8'))
    tile.save(out/(name+'.png'))
    manifest[name]={'source':'../textures/land.png','crop':box,'processing':'local lighting equalization, controlled color mean, source brush detail, blended borders without mirroring','sha256':hashlib.sha256((out/(name+'.png')).read_bytes()).hexdigest()}
for name in ['bamboo_middle','bamboo_front','bamboo_bridge']:
    im=Image.open(src/(name+'.png')).convert('RGBA')
    rgb=ImageEnhance.Color(im.convert('RGB')).enhance(.86)
    rgb.putalpha(im.getchannel('A'));rgb.save(out/(name+'.png'))
    manifest[name]={'source':'../textures/'+name+'.png','processing':'0.86 saturation, original alpha preserved'}
(out/'SOURCE.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
preview=Image.new('RGB',(1000,200))
for i,name in enumerate(regions):preview.paste(Image.open(out/(name+'.png')).resize((200,200)),(i*200,0))
preview.save(root/'artifacts/spatial-foundation-review/materials.jpg',quality=75)
print('Prepared',len(manifest),'material images')
