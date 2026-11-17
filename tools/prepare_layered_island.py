"""Prepare supplied paintings for the new scene. No model geometry is made here."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'artifacts/layered-island-review'
OUT = ROOT / 'assets/layered_island/textures'
OUT.mkdir(parents=True, exist_ok=True)
manifest = {}

def save(name, img, source):
    img = img.convert('RGBA')
    arr = np.array(img)
    arr[:,:,3] = np.where(arr[:,:,3] < 8, 0, np.minimum(arr[:,:,3].astype(float)*255/254,255)).astype('uint8')
    img = Image.fromarray(arr)
    img.save(OUT / (name+'.png'))
    manifest[name] = {'source':str(source),'size':img.size,'sha256':hashlib.sha256((OUT/(name+'.png')).read_bytes()).hexdigest()}
    return img

for name,path in {
    'land':'left-terrain-v1/source.png',
    'sky':'background-v1/source/sky.png',
    'mountain_far':'background-v1/source/far.png',
    'mountain_middle':'background-v1/source/middle.png',
    'mountain_near':'background-v1/source/near.png',
    'bamboo_back':'bamboo-back-v2/source.png',
    'bamboo_middle':'bamboo-v1/source/bamboo-02.png',
    'bamboo_front':'bamboo-v1/source/bamboo-03.png',
    'bamboo_bridge':'bamboo-v1/source/bamboo-04.png',
    'trees_back':'trees-foreground-v1/source/trees-back.png',
    'foreground_bottom':'trees-foreground-v1/source/foreground-bottom.png',
}.items():
    save(name,Image.open(REVIEW/path),path)

def place(img,scale,at):
    output=Image.new('RGBA',(2048,1536))
    output.alpha_composite(img.resize((round(img.width*scale),round(img.height*scale)),Image.Resampling.LANCZOS),at)
    return output

ext=Image.open(REVIEW/'cave-v1/source/exterior.png').convert('RGBA')
inter=Image.open(REVIEW/'cave-v1/source/interior.png').convert('RGBA')
a=np.asarray(ext)[:,:,3]
flood=Image.fromarray(np.where(a<=32,255,0).astype('uint8')).copy()
ImageDraw.floodfill(flood,(1600,800),128,thresh=0)
assert flood.getpixel((1600,800))==128
mask=Image.fromarray(np.where(np.asarray(flood)==128,255,0).astype('uint8')).filter(ImageFilter.MaxFilter(17))
inter.putalpha(Image.fromarray((np.asarray(inter.getchannel('A')).astype('uint16')*np.asarray(mask).astype('uint16')//255).astype('uint8')))
save('cave_outer',place(ext,.565,(838,216)),'cave-v1/source/exterior.png; review alignment')
save('cave_inner',place(inter,.565,(838,216)),'cave-v1/source/interior.png; enclosed-opening mask')
vines=Image.open(REVIEW/'cave-v1/source/foliage.png').convert('RGBA')
save('vine_left',place(vines.crop((1100,455,1510,985)),.35,(1550,484)),'cave-v1/source/foliage.png; left group')
save('vine_right',place(vines.crop((1510,345,2010,1220)),.32,(1760,405)),'cave-v1/source/foliage.png; right group')

# Separate the nearest right leaves from their rock support. The opaque hidden
# rock remains static; the canopy is allowed only small root-weighted motion.
fore=Image.open(REVIEW/'trees-foreground-v1/foreground-right-isolated.png').convert('RGBA')
mask=Image.new('L',fore.size,0)
ImageDraw.Draw(mask).polygon([(1560,780),(2048,780),(2048,1295),(1940,1300),(1840,1280),(1780,1246),(1740,1258),(1720,1230),(1680,1230),(1615,1170),(1580,1120)],fill=255)
leaves=fore.copy(); leaves.putalpha(Image.fromarray((np.asarray(fore.getchannel('A')).astype('uint16')*np.asarray(mask).astype('uint16')//255).astype('uint8')))
save('foreground_right_leaves',leaves,'trees-foreground-v1/right-isolated; canopy mask')
rock=fore.copy(); rock.putalpha(Image.fromarray((np.asarray(fore.getchannel('A')).astype('uint16')*(255-np.asarray(mask).astype('uint16'))//255).astype('uint8')))
save('foreground_right_rock',rock,'trees-foreground-v1/right-isolated; complementary static rock mask')

bridge=Image.open(REVIEW/'bridge-v1/source.png').convert('RGBA')
# Timber samples from the provided bridge, not third-party assets.
plank=bridge.transform((64,192),Image.Transform.QUAD,(1200,918,1207,960,1220,961,1213,919),Image.Resampling.BICUBIC)
plank.putalpha(255)
save('wood_plank',plank,'bridge-v1/source.png; corrected 64x192 plank quadrilateral; opaque timber')
save('wood_post',bridge.crop((1020,869,1045,943)).resize((64,192),Image.Resampling.BICUBIC),'bridge-v1/source.png; post shaft')

(OUT.parent/'SOURCE.json').write_text(json.dumps({'source':'User-supplied layered paintings; no third-party game assets','operations':'Alpha floor 8/255; source files preserved. Local crops/alignment listed per texture.','textures':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
print('Prepared',len(manifest),'textures')
