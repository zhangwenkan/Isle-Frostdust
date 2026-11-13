"""Edit surface bitmap assets only; all model/UV work runs via Blender MCP.

Jeff source images are pinned and attributed in pixel/surfaces/SOURCES.md.
No image-generation service is used. Palette conversion has no dithering:
connected source features survive instead of becoming a field of speckles.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import random
import math
import shutil

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / 'artifacts/jeff-scene-review'
TERRAIN = REF / 'addons/hd2d_scene_tools/assets/terrain/textures'
OUT = ROOT / 'assets/island_blender/pixel/surfaces'
OUT.mkdir(parents=True, exist_ok=True)

PALETTES = {
    'stone': ['394d4d','4d6260','63756e','78867c','8b9789','9da696','adb3a3','bfc2b0','ced0bc'],
    'grass': ['344b33','3e5c35','4b6d39','597e3e','6a8e47','7d9c50','91aa5f','a6b973','bdc987'],
    'moss': ['304d37','3b603d','4c7242','5d8248','71954f','86a35a','9cb369','b0c17d','c2ce8e'],
    'wood': ['454238','57503f','6a5e47','7d6e52','90825f','a29670','b3a580','c3b693','d0c4a3'],
    'bark': ['343d35','494839','5e553e','766548','8a7653','9f8961','b39b70','c6af82'],
}

def rgb(h):
    return tuple(bytes.fromhex(h))

def palette_map(im, key, size, contrast=1.0, consolidate=False):
    # Box reduction integrates the fine source marks; a discrete, authored ramp
    # then consolidates them into readable blocks. Never add random dithering.
    im = im.convert('RGB').resize(size, Image.Resampling.BOX)
    if consolidate:
        im = im.filter(ImageFilter.MedianFilter(3))
    a = np.asarray(im, dtype=float)
    lum = a @ np.array([.23,.64,.13])
    lo, hi = np.percentile(lum, [2,98])
    t = np.clip(((lum-lo)/(hi-lo)-.5)*contrast+.5, 0, 1)
    pal = np.array([rgb(h) for h in PALETTES[key]], dtype=np.uint8)
    return Image.fromarray(pal[np.minimum((t*len(pal)).astype(int),len(pal)-1)])

rock = palette_map(Image.open(TERRAIN/'gray_rock.png'), 'stone', (128,128), .86, True)
rock.save(OUT/'coastal_granite.png')
# The weathered source is reserved for rock accents; its warmer original is
# remapped to the same coastal stone ramp so geology stays visually coherent.
weathered = palette_map(Image.open(TERRAIN/'weathered_rock.png'), 'stone', (128,128), .80, True)
weathered.save(OUT/'weathered_granite.png')

grass_source = Image.open(TERRAIN/'moss_grass.png').convert('RGB')
grass = palette_map(grass_source, 'grass', (256,256), .80, True)
short = palette_map(Image.open(TERRAIN/'short_grass.png'), 'grass', (256,256), .70, True)
# Keep the moss source's grouped vegetation and exposed soil. Introduce short
# blades only in its brighter, denser grassy areas, at the same pixel scale.
g = np.asarray(grass).copy()
s = np.asarray(short)
lum = np.asarray(grass_source.resize((256,256),Image.Resampling.BOX).convert('L'))
mask = lum > np.percentile(lum,65)
g[mask] = s[mask]
grass = Image.fromarray(g)
grass.save(OUT/'coastal_turf.png')
palette_map(grass_source, 'moss', (128,128), .78).save(OUT/'rock_moss.png')

atlas = Image.open(REF/'addons/hd2d_scene_tools/assets/buildings/v5/jiangnan.png')
tile = atlas.width//4
# One continuous plank interior, excluding all atlas / painted plank borders.
wood_source = atlas.crop((tile+round(tile*.03),round(tile*.18),2*tile-round(tile*.03),round(tile*.37)))
wood_source = wood_source.transpose(Image.Transpose.ROTATE_90)
wood = palette_map(wood_source,'wood',(64,256), .84)
wood.save(OUT/'salt_worn_wood.png')

# Revise our existing bark design into narrow, staggered scales and connected
# fissures. Each plate has a shaded recess, broad face and one broken light lip.
W,H = 128,256
bark = Image.new('RGB',(W,H),rgb(PALETTES['bark'][1]))
d = ImageDraw.Draw(bark)
r = random.Random(9067)
for column in range(-1,20):
    x = column*7
    y = -42+r.randrange(0,30)
    while y < H+35:
        h = r.randrange(12,25)
        w = r.randrange(5,9)
        shift = r.randrange(-3,4)
        poly = [(x+shift+2,y),(x+shift+w-2,y-2),(x+w,y+h//3),
                (x+w-2,y+h-4),(x+3,y+h),(x,y+h//2)]
        idx = r.choice([2,3,4,4,5,5])
        for dy in [-H,0,H]:
            for dx in [-W,0,W]:
                pts=[(px+dx,py+dy) for px,py in poly]
                d.polygon(pts,fill=rgb(PALETTES['bark'][idx]))
                d.line([(x+shift+3+dx,y+3+dy),(x+2+dx,y+h//2+dy),(x+4+dx,y+h-5+dy)],fill=rgb(PALETTES['bark'][min(7,idx+1)]),width=1)
                if h>23:
                    d.line([(x+w-3+dx,y+7+dy),(x+w-4+dx,y+h//2+dy),(x+w-3+dx,y+h-6+dy)],fill=rgb(PALETTES['bark'][max(1,idx-1)]),width=1)
        y += h-2
# Two distinct knots; growth lines wrap around them, without regular oval stamps.
for x,y,rx,ry in [(29,68,7,15),(93,193,5,11)]:
    for k,idx in [(0,1),(2,5),(4,2),(5,0)]:
        if rx-k<1:continue
        points=[]
        for a in range(0,360,20):
            t=math.radians(a)
            points.append((round(x+math.cos(t)*(rx-k)),round(y+math.sin(t)*(ry-k)+math.cos(t)*2)))
        d.polygon(points,fill=rgb(PALETTES['bark'][idx]))
    d.line([(x,y-ry-12),(x+2,y-ry-5),(x,y-ry)],fill=rgb(PALETTES['bark'][1]))
bark.save(OUT/'pine_bark_scales.png')

shutil.copy2(REF/'LICENSE',OUT/'JEFF_LICENSE.txt')
print('Surface bitmap editing complete:',OUT)
for p in sorted(OUT.glob('*.png')):
    im=Image.open(p)
    print(p.name, im.size, len(im.getcolors(100000) or []),'colors')
