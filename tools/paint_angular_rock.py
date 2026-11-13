"""Original restrained face washes and selected structure strokes; texture only.
Geometry, face assignments and UVs are authored inside Blender via MCP.
"""
from pathlib import Path
import math,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/colored_ink_sample'
S=512;atlas=Image.new('RGB',(S*4,S*4))
palette=[(147,159,151),(124,140,134),(133,147,139),(142,154,146),
         (119,135,129),(137,151,144),(145,157,149),(128,144,137),
         (139,153,146),(148,161,154),(156,169,161),(144,156,148),
         (136,150,143),(148,160,152),(141,155,148),(143,157,150)]
for k,base in enumerate(palette):
    y,x=np.mgrid[0:S,0:S].astype(float)/S
    wash=np.exp(-((x-.28)**2/.16+(y-.35)**2/.23))*3.6-np.exp(-((x-.78)**2/.12+(y-.75)**2/.13))*3
    rgb=np.clip(np.array(base)+wash[:,:,None],0,255).astype('uint8')
    tile=Image.fromarray(rgb).convert('RGBA')
    marks=Image.new('RGBA',(S,S));d=ImageDraw.Draw(marks)
    # Top boundary follows a real plane change. Leave the side boundary and
    # portions of the top uninked, avoiding a black wireframe on every face.
    if k in [0,1,2,3,4,5,7,8]:
        d.line([(30,26),(140,28),(273,26),(397,29),(481,26)],fill=(48,67,61,145),width=7)
        d.line([(34,30),(176,32),(283,30)],fill=(187,193,175,60),width=3)
    if k in [0,2,5,7]:
        d.line([(27,31),(29,115),(26,214),(30,322),(27,437)],fill=(47,65,59,135),width=6)
    # Few sparse short strokes at a corner, never tiled crack networks.
    if k in [2,4,8]:
        d.line([(360,168),(329,193),(310,225)],fill=(65,82,75,100),width=4)
    if k==3:
        d.line([(366,27),(352,151),(361,251)],fill=(55,73,65,125),width=5)
        d.line([(361,251),(349,333),(354,391)],fill=(55,73,65,85),width=3)
    tile=Image.alpha_composite(tile,marks)
    atlas.paste(tile.convert('RGB'),((k%4)*S,(k//4)*S))
atlas.save(OUT/'angular_rock_planes.png')
(OUT/'angular_rock_palette.json').write_text(json.dumps({'tile_size':S,'grid':[4,4],'palette':palette,'source':'Original face washes and selective structure strokes; no reference pixels copied'},indent=2),encoding='utf-8')
print(OUT/'angular_rock_planes.png')
