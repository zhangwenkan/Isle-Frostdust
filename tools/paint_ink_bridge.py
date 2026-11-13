"""Original sparse wood brushwork at an explicit pixel scale. No model code."""
from pathlib import Path
import math,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
R=Path(__file__).resolve().parents[1];O=R/'assets/ink_bridge';O.mkdir(exist_ok=True)
W,H=32,128;PAD=4;SCALE=4
atlas=Image.new('RGB',((W+PAD*2)*4,(H+PAD*2)*2))
brush_atlas=Image.new('RGBA',atlas.size)
bases=[(112,99,77),(119,104,81),(108,98,77),(122,107,84),(115,100,78),(110,98,80),(118,105,84),(113,100,79)]
for k,base in enumerate(bases):
    yy,xx=np.mgrid[0:H,0:W].astype(float)
    wash=2.7*np.cos((xx/W-.27)*math.pi)*np.sin((yy/H+.13*k)*math.pi)
    side=3.5*np.clip((abs(xx/W-.5)-.33)/.17,0,1)
    rgb=np.array(base)+wash[:,:,None]-side[:,:,None]
    im=Image.fromarray(np.uint8(np.clip(rgb,0,255))).convert('RGBA')
    layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
    # Each board has a few long, tapered grain groups, with quiet intervals.
    # The broad diluted sweep is distinct from the short dark structural stroke.
    main=7+(k%3)*3;sign=1 if k%2 else -1
    d.polygon([(main-1,10),(main+3,23),(main+4+sign,47),(main+1+sign,67),(main-2,55),(main-3,29)],fill=(61,61,49,78))
    d.line([(main+1,17),(main+2,36),(main+sign,53)],fill=(54,62,52,76),width=1)
    d.polygon([(21,45),(26,59),(26,85),(23,111),(20,99),(22,76)],fill=(164,142,102,64))
    d.line([(22,74),(23,88),(22,106)],fill=(62,67,55,48),width=1)
    if k in [1,4,6]:
        # A small tapered split begins at the end, never a repeated crack web.
        d.line([(15+k%4,0),(14+k%4,12),(15+k%4,21)],fill=(49,57,47,90),width=1)
    if k==3:
        d.arc((10,72,19,100),83,261,fill=(66,69,55,65),width=1)
    im=Image.alpha_composite(im,layer).convert('RGB')
    # Extend edge texels into an explicit gutter for mip filtering.
    tile=Image.new('RGB',(W+PAD*2,H+PAD*2));tile.paste(im,(PAD,PAD))
    tile.paste(im.crop((0,0,1,H)).resize((PAD,H)),(0,PAD));tile.paste(im.crop((W-1,0,W,H)).resize((PAD,H)),(PAD+W,PAD))
    tile.paste(tile.crop((0,PAD,W+PAD*2,PAD+1)).resize((W+PAD*2,PAD)),(0,0))
    tile.paste(tile.crop((0,PAD+H-1,W+PAD*2,PAD+H)).resize((W+PAD*2,PAD)),(0,PAD+H))
    origin=((k%4)*(W+PAD*2),(k//4)*(H+PAD*2));atlas.paste(tile,origin)
    brush_atlas.paste(layer,(origin[0]+PAD,origin[1]+PAD))
atlas.save(O/'wood-brush-native.png')
atlas.resize((atlas.width*SCALE,atlas.height*SCALE),Image.Resampling.NEAREST).save(O/'wood-brush.png')
brush_atlas.resize((atlas.width*SCALE,atlas.height*SCALE),Image.Resampling.NEAREST).save(O/'wood-strokes.png')
# Bindings use large quiet strand bands. There is no modeled micro-fibre spiral.
rw,rh=24,96;im=Image.new('RGB',(rw,rh),(110,106,84));d=ImageDraw.Draw(im)
for y in range(-24,120,24):
    d.polygon([(0,y+8),(24,y-2),(24,y+3),(0,y+13)],fill=(101,98,77))
    d.polygon([(0,y+14),(24,y+4),(24,y+6),(0,y+16)],fill=(118,112,87))
im.resize((96,384),Image.Resampling.NEAREST).save(O/'rope-brush.png')
(O/'palette-and-layout.json').write_text(json.dumps({'wood_native_tile':[W,H],'gutter':PAD,'atlas_grid':[4,2],'upscale':SCALE,'base_srgb':bases,
 'rope_base_srgb':[110,106,84],'source':'Original sparse authored brush polygons; no granular noise, normal map, or external pixels.'},indent=2),encoding='utf-8')
print('Painted bridge wood and rope brush maps',atlas.size)
