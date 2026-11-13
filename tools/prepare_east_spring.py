"""Prepare the supplied Louis illustration as attributed surface paint and region guides.
This file makes only 2D images. All mesh authoring is in Blender via MCP.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,cv2,json
R=Path(__file__).resolve().parents[1];A=R/'assets/east_spring';A.mkdir(exist_ok=True)
im=Image.open(R/'artifacts/east-spring-review/reference/reference-480.png').convert('RGB')
# Remove the reference actor and English prompt, retaining the game's own hero.
arr=np.array(im);mask=np.zeros((360,480),np.uint8)
cv2.fillPoly(mask,[np.array([(198,237),(216,237),(225,248),(226,260),(232,275),(225,283),(226,300),(216,306),(205,302),(203,289),(191,281),(191,258)])],255)
mask=cv2.dilate(mask,np.ones((5,5),np.uint8))
original=arr.copy()
yy,xx=np.where(mask>0);arr[yy,xx]=original[yy,np.maximum(0,xx-63)]
# Replace the prompt with irregular nearby grass/road paint, never retain text.
patch=arr[272:318,10:216].copy()
arr=cv2.seamlessClone(patch,arr,np.full((46,206),255,np.uint8),(245,337),cv2.NORMAL_CLONE)
clean=Image.fromarray(arr)
clean.save(A/'spring_core.png')
# Extend the illustration through edge paint. Core occupies x=80..559, y=20..379.
# Extensions sit beyond the intended composition; no original actor is repeated.
paint=Image.new('RGB',(640,400));paint.paste(clean,(80,20))
paint.paste(clean.crop((0,0,80,360)).transpose(Image.Transpose.FLIP_LEFT_RIGHT),(0,20))
paint.paste(clean.crop((400,0,480,360)).transpose(Image.Transpose.FLIP_LEFT_RIGHT),(560,20))
edge=clean.crop((399,137,479,237)).resize((80,300),Image.Resampling.NEAREST)
paint.paste(edge,(560,20));paint.paste(clean.crop((370,300,450,360)),(560,320))
paint.paste(paint.crop((0,20,640,40)).transpose(Image.Transpose.FLIP_TOP_BOTTOM),(0,0))
paint.paste(paint.crop((0,360,640,380)).transpose(Image.Transpose.FLIP_TOP_BOTTOM),(0,380))
paint.save(A/'spring_paint.png')
regions=Image.new('L',(480,360),0);d=ImageDraw.Draw(regions)
shapes={
 'terrace':(1,[(0,0),(480,0),(480,129),(425,125),(395,88),(340,78),(282,72),(237,74),(197,83),(164,102),(139,107),(99,133),(74,165),(0,180)]),
 'wall':(2,[(99,132),(135,113),(179,94),(230,79),(280,76),(337,77),(389,84),(425,116),(421,166),(380,175),(339,166),(294,161),(255,176),(214,188),(175,206),(142,219),(119,211),(104,188)]),
 'pool':(3,[(137,216),(170,197),(219,185),(264,169),(299,161),(339,162),(375,172),(404,201),(417,229),(394,253),(366,278),(356,297),(332,291),(313,272),(284,260),(255,249),(215,239),(186,230),(157,234)]),
 'far_right_tree':(7,[(370,0),(456,0),(444,24),(428,49),(412,64),(390,64),(383,48)]),
 'middle_trunk':(6,[(177,0),(202,0),(202,30),(195,51),(190,66),(200,76),(209,80),(211,92),(204,104),(198,122),(201,141),(193,156),(187,175),(181,166),(177,144),(181,116),(188,99),(176,90),(165,74),(163,58),(171,32)]),
 'left_tree':(5,[(0,59),(40,60),(40,92),(43,125),(53,142),(71,147),(77,168),(83,184),(107,199),(128,211),(131,220),(119,233),(91,237),(80,259),(58,260),(52,241),(42,228),(27,211),(19,210),(10,231),(0,230)]),
 'right_foliage':(4,[(480,108),(441,116),(422,123),(414,137),(400,139),(402,158),(381,166),(387,180),(375,186),(365,200),(374,215),(387,226),(396,240),(413,245),(428,269),(444,280),(480,281)]),
 'front_tree':(8,[(480,260),(458,269),(449,281),(434,286),(421,295),(405,303),(401,316),(418,315),(438,308),(449,308),(457,319),(480,326)]),
 'trough':(9,[(326,126),(338,119),(392,97),(403,102),(402,122),(375,132),(382,151),(373,169),(364,162),(359,142),(350,145),(336,158),(332,145)]),
 'fall':(10,[(337,143),(346,143),(347,158),(344,181),(345,197),(352,207),(344,216),(332,216),(323,210),(326,202),(330,193),(330,168),(326,158),(329,150)]),
 'rim':(11,[(416,235),(430,241),(419,253),(402,262),(381,278),(362,285),(352,273),(357,267),(378,260),(394,249)])}
for k,(n,p) in shapes.items():
 d.polygon(p,fill=n)
 if k=='pool':base_regions=regions.copy()
# Isolate actual green reed pixels, with root weights authored later in Blender.
a=np.array(clean);r=np.array(regions)
for n,box in [(12,(144,179,190,228)),(13,(207,192,244,233)),(14,(246,128,300,172)),(15,(314,250,357,288))]:
 x0,y0,x1,y1=box;v=a[y0:y1,x0:x1].astype(float)
 green=(v[:,:,1]>v[:,:,0]*1.08)&(v[:,:,1]>v[:,:,2]*1.2)&(v[:,:,1]>75)
 patch=r[y0:y1,x0:x1];patch[green]=n
regions=Image.fromarray(r)
reg=Image.new('L',(640,400));reg.paste(regions,(80,20))
reg.paste(regions.crop((0,0,80,360)).transpose(Image.Transpose.FLIP_LEFT_RIGHT),(0,20))
reg.paste(regions.crop((400,0,480,360)).transpose(Image.Transpose.FLIP_LEFT_RIGHT),(560,20))
reg.paste(reg.crop((0,20,640,40)).transpose(Image.Transpose.FLIP_TOP_BOTTOM),(0,0))
reg.paste(reg.crop((0,360,640,380)).transpose(Image.Transpose.FLIP_TOP_BOTTOM),(0,380))
reg.save(A/'regions.png')
base=Image.new('L',(640,400));base.paste(base_regions,(80,20))
base.paste(base_regions.crop((0,0,80,360)).transpose(Image.Transpose.FLIP_LEFT_RIGHT),(0,20))
base.paste(base_regions.crop((400,0,480,360)).transpose(Image.Transpose.FLIP_LEFT_RIGHT),(560,20))
base.paste(base.crop((0,20,640,40)).transpose(Image.Transpose.FLIP_TOP_BOTTOM),(0,0))
base.paste(base.crop((0,360,640,380)).transpose(Image.Transpose.FLIP_TOP_BOTTOM),(0,380))
base.save(A/'base_regions.png')
backmask=(np.array(base)!=np.array(reg)).astype('uint8')*255
back=cv2.inpaint(np.array(paint),backmask,8,cv2.INPAINT_TELEA)
Image.fromarray(back).save(A/'spring_backfill.png')
debug=np.array(paint).astype(float)
colors=np.array([(124,190,100),(63,100,76),(150,136,194),(40,220,229),(244,80,100),(199,130,54),(255,150,30),(210,150,90),(178,101,10),(255,90,12),(220,230,255),(125,125,255),(180,255,50),(180,255,50),(180,255,50),(180,255,50)])
debug=.55*debug+.45*colors[np.array(reg)]
Image.fromarray(debug.astype('uint8')).resize((1280,800),Image.Resampling.NEAREST).save(R/'artifacts/east-spring-review/region-guide.png')
(A/'SOURCE.md').write_text('''# Source and adaptation

Visual reference and surface-paint pixels: Louis (@LouisPretends), “You hear rushing water in the distance ~”, 2026-11-09.
https://x.com/LouisPretends/status/2119792131929739595

The supplied public illustration is used directly as attributed surface paint in this local reconstruction at the user's request. This is not original artwork by Codex. No license grant was supplied. Source remains in artifacts/east-spring-review/reference/. The original actor and English prompt were removed; edge paint was extended. The model, segmentation, reconstructed relief, connector and runtime water/wind were authored for this project. The original animation file could not be downloaded; runtime motion is recreated, not extracted frames.
''',encoding='utf8')
print('2D reference paint and region guides prepared')
