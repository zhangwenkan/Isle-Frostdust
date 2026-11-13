"""Copy attributed reference textures and paint a quiet forest floor; no geometry."""
from pathlib import Path
import json, shutil, hashlib, random, math
from PIL import Image, ImageDraw, ImageFilter
R=Path(__file__).resolve().parents[1]
S=Path('D:/Y 逸jian风yun决 v1.23.26 全DLC xg器/WanderingSword/analysis/12_followup/20261109-bamboo-scene')
A=R/'assets/pixel_bamboo_west';A.mkdir(exist_ok=True)
D=json.loads((S/'scene-manifest.json').read_text(encoding='utf-8'))
records=[]
for name in ['T_jn_zhuzi001.png','T_jn_zhuzi004.png','T_jn_zhuzi005.png']:
    src=S/'exports/JH/MapEditor/Tree/Textures'/name
    shutil.copy2(src,A/name)
    records.append(dict(file=name,source=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest()))
(A/'SOURCE.json').write_text(json.dumps(dict(game='Wandering Sword / 逸剑风云决',purpose='User-authorized local island bamboo study, 2026-11-09',original_art=True,license='Extracted installed-game assets; no redistribution license supplied',textures=records,mesh_source=str(S/'scene-manifest.json')),ensure_ascii=False,indent=2),encoding='utf-8')
# Flat 2D pigment study: broad moss/earth patches, with selective leaf marks.
size=512;rng=random.Random(1911)
im=Image.new('RGB',(size,size),(88,103,56));dr=ImageDraw.Draw(im)
for i in range(55):
    x=rng.randrange(-80,512);y=rng.randrange(-50,512);w=rng.randrange(35,125);h=rng.randrange(20,70)
    c=rng.choice([(81,91,53),(111,113,66),(72,91,51),(99,113,61),(120,113,76)])
    dr.ellipse((x,y,x+w,y+h),fill=c)
im=im.filter(ImageFilter.GaussianBlur(9));dr=ImageDraw.Draw(im)
for i in range(950):
    x=rng.randrange(size);y=rng.randrange(size)
    if math.sin(x*.045+y*.026)<-.55:continue
    c=rng.choice([(95,112,60),(111,122,66),(69,88,46),(115,113,71)])
    dr.line((x,y,x+rng.choice([-2,-1,1,2]),y-rng.randrange(2,5)),fill=c,width=1)
for i in range(110):
    x=rng.randrange(size);y=rng.randrange(size)
    dr.line((x,y,x+3,y-1),fill=(116,115,78),width=1)
im.save(A/'forest_floor.png')
print('REFERENCE_TEXTURES_COPIED',len(records),'FLOOR_PAINTED')
