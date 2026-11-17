"""Rework supplied painting fragments into material-role textures, not scene cards."""
from pathlib import Path
from PIL import Image,ImageEnhance,ImageFilter,ImageDraw
import numpy as np,json,hashlib
root=Path(__file__).resolve().parents[1];out=root/'assets/layered_island/left_finish_textures';out.mkdir(exist_ok=True)
land=Image.open(root/'assets/layered_island/textures/land.png').convert('RGB')
sources={
'rock_a':((280,965,413,1083),(.37,.365,.31)),
'rock_b':((343,977,454,1086),(.35,.35,.305)),
'rock_c':((59,969,137,1068),(.33,.345,.30)),
'rock_d':((803,960,847,1048),(.38,.375,.32)),
'rock_top':((265,920,399,951),(.36,.39,.255)),
'soil':((166,903,303,933),(.34,.345,.245)),
'grass':((228,877,340,917),(.31,.365,.185)),
'sand':((538,1260,774,1303),(.65,.58,.425)),
'paving':((647,837,757,883),(.47,.445,.35)),
'tread':((592,958,721,974),(.47,.455,.38))}
manifest={}
for name,(box,target) in sources.items():
    im=land.crop(box).resize((192,192),Image.Resampling.LANCZOS)
    a=np.array(im,dtype=float)/255.;low=np.array(im.filter(ImageFilter.GaussianBlur(14)),dtype=float)/255.
    # Retain the actual broad painted facets. Limit only outlying source highlights.
    detail=a-low;factor=.80 if name.startswith('rock') else .48
    a=np.clip(np.array(target)+(low-low.mean((0,1)))*factor+detail*.82,.055,.79)
    im=Image.fromarray((a*255).astype('uint8'))
    # Padded standalone maps, no neighbouring atlas cells or mirrored patterns.
    im.save(out/(name+'.png'))
    manifest[name]={'source':'../textures/land.png','crop':box,'processing':'retained brush/facet detail, controlled albedo range; standalone material patch','size':[192,192]}
# Editable culm and leaf surface details. Geometry carries nodes, branches and leaves.
culm=Image.new('RGB',(64,256));draw=ImageDraw.Draw(culm)
for x in range(64):
    q=x/63.;tone=.78+.20*np.sin(q*np.pi)
    draw.line((x,0,x,255),fill=tuple(int(c*tone) for c in (94,116,58)))
for x,y0,y1,c in [(12,21,114,(87,106,53)),(23,53,214,(110,126,65)),(42,6,173,(67,89,43)),(52,120,246,(106,122,65))]:
    draw.line((x,y0,x,y1),fill=c,width=1)
culm.save(out/'culm.png')
leaf=Image.new('RGB',(64,128));draw=ImageDraw.Draw(leaf)
for x in range(64):
    q=abs(x-31.5)/31.5;c=np.array((76,105,47))*(1-.20*q)
    draw.line((x,0,x,127),fill=tuple(c.astype(int)))
draw.line((31,2,31,126),fill=(113,135,64),width=1)
leaf.save(out/'leaf.png')
manifest['culm']={'source':'authored axial brush marks; physical nodes in Blender'}
manifest['leaf']={'source':'authored restrained midrib; physical lanceolate leaves in Blender; no plant photograph'}
for name,item in manifest.items():item['sha256']=hashlib.sha256((out/(name+'.png')).read_bytes()).hexdigest()
(out/'SOURCE.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Prepared',len(manifest),'left-side material roles')
