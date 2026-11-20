"""Prepare restrained surface colors from the user's own cape reference."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageEnhance,ImageFilter,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/layered_island/reference_cape';OUT.mkdir(parents=True,exist_ok=True)
im=Image.open(ROOT/'artifacts/reference-cape-review/reference/user-cape.png').convert('RGB')
sources={}
def tile(name,box,size,brightness=1.,color=.80):
    crop=im.crop(box).resize(size,Image.Resampling.LANCZOS)
    crop=ImageEnhance.Color(crop).enhance(color)
    crop=ImageEnhance.Contrast(crop).enhance(.66)
    crop=ImageEnhance.Brightness(crop).enhance(brightness)
    crop=crop.filter(ImageFilter.GaussianBlur(.75))
    # Mirrored quadrants keep the outer joins coherent without added noise.
    half=crop.resize((size[0]//2,size[1]//2),Image.Resampling.LANCZOS)
    result=Image.new('RGB',size)
    result.paste(half,(0,0));result.paste(half.transpose(Image.Transpose.FLIP_LEFT_RIGHT),(size[0]//2,0))
    result.paste(half.transpose(Image.Transpose.FLIP_TOP_BOTTOM),(0,size[1]//2))
    result.paste(half.transpose(Image.Transpose.ROTATE_180),(size[0]//2,size[1]//2))
    result.save(OUT/(name+'.png'));sources[name]={'reference_crop':box,'size':size,'processing':'softened contrast, color balance and mirrored tile; no generated noise'}
    return result
rock=tile('rock_side',(1965,1082,2030,1215),(512,512),1.30,.64)
top=tile('rock_top',(1500,865,1648,919),(512,512),.88,.72)
sand=tile('sand',(1720,1560,1870,1664),(512,512),.93,.80)
tile('wood',(1868,891,1940,916),(512,128),.80,.76)
tile('tread',(1767,1080,1822,1110),(256,256),1.02,.60)
for name,target,strength in [('rock_side',(112,105,93),.54),('rock_top',(149,139,119),.28)]:
    p=OUT/(name+'.png');a=np.array(Image.open(p),dtype=float)
    a=a*(1-strength)+np.array(target)*strength
    Image.fromarray(a.clip(0,255).astype('uint8')).save(p)
top=Image.open(OUT/'rock_top.png')
ImageEnhance.Brightness(top.resize((256,256))).enhance(.91).save(OUT/'tread.png')
# Unique platform painting contains just a few structural joints and the
# campfire's contact stain, registered in the actual authored coordinates.
size=(1536,1024);painting=top.resize(size,Image.Resampling.LANCZOS)
overlay=Image.new('RGBA',size,(0,0,0,0));draw=ImageDraw.Draw(overlay)
def uv(x,y):return ((x+84)/17*size[0],(18-y)/13*size[1])
for points in [[(-81.8,12.4),(-79.6,12.05),(-78.8,10.4)], [(-78.8,10.4),(-78.0,8.0)], [(-78.8,10.4),(-75.8,9.8),(-74.8,8.5)], [(-76.4,15.7),(-76.0,14.5),(-74.4,14.0)], [(-71.3,14.5),(-71.8,12.8),(-70.4,10.1)]]:
    draw.line([uv(*p) for p in points],fill=(42,37,31,105),width=5,joint='curve')
for radius,alpha in [(1.12,14),(.90,22),(.64,31),(.39,52)]:
    cx,cy=uv(-76.0,13.1);rx=radius/17*size[0];ry=radius/13*size[1]
    draw.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=(38,30,25,alpha))
painting=Image.alpha_composite(painting.convert('RGBA'),overlay.filter(ImageFilter.GaussianBlur(1.1))).convert('RGB')
painting.save(OUT/'platform.png')
sources['platform']={'derived_from':'rock_top','world_bounds':[-84,5,-67,18],'fire_contact_center':[-76,13.1],'paint':'five selective structural joints and localized charcoal wash'}
# The sand map stays fixed while a separate physical film runs up and recedes.
sand.resize((1024,768),Image.Resampling.LANCZOS).save(OUT/'sand_unique.png')
(OUT/'SOURCE.json').write_text(json.dumps({'reference':'artifacts/reference-cape-review/reference/user-cape.png','ownership':'User supplied generated reference; existing raster edit, no new AI image generation','maps':sources},ensure_ascii=False,indent=2),encoding='utf-8')
print('Prepared cape surface maps from supplied reference.')
