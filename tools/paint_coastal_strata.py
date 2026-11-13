"""Hand-directed mineral colour groups and broken bedding strokes; no noise fill."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFilter

OUT=Path(__file__).resolve().parents[1]/'assets/coastal_strata'
OUT.mkdir(parents=True,exist_ok=True)
W,H=3072,256
image=Image.new('RGB',(W,H));px=image.load()
for y in range(H):
    t=y/(H-1)
    for x in range(W):
        u=x/W
        broad=3.5*math.sin(u*math.tau*6)+2*math.cos(u*math.tau*13)
        shade=1-.15*t
        base=(164,161,142)
        px[x,y]=tuple(round(v*shade+broad) for v in base)
paint=Image.new('RGBA',(W,H));d=ImageDraw.Draw(paint)
# Wide translucent mineral washes, intentional large connected shapes.
for index,(a,b,shift) in enumerate([(0,190,5),(215,447,-4),(505,680,8),(730,940,-3),(1010,1270,6),(1320,1480,-5),(1550,1830,4),(1900,2170,-4),(2240,2450,6),(2520,2750,-3),(2830,3072,4)]):
    d.polygon([(a,0),(b,0),(b-20,70),(b+18,147),(b-40,256),(a+18,256),(a+40,160),(a-12,74)],fill=(191,183,154,24) if shift>0 else (85,109,105,23))
# Texture bedding follows the author's normalized strata boundaries.
for index,y in enumerate([31,70,125,188]):
    for a,b in [(35,145),(265,351),(430,575),(680,760),(840,955),(1080,1205),(1350,1430),(1600,1750),(1880,2020),(2150,2270),(2390,2520),(2660,2740),(2900,3020)]:
        a+=index*11;b+=index*7
        d.line([(a,y+2),(b,y+2)],fill=(78,92,85,80 if index<2 else 60),width=2)
        d.line([(a,y-1),(b-10,y-1)],fill=(207,207,173,90),width=2)
# Sparse branching fractures have unequal lengths and remain subordinate to bedding.
for index,x in enumerate([30,240,460,700,930,1170,1400,1640,1850,2070,2300,2510,2730,2950]):
    # Broad washed fracture faces, tapering under the grass and widening downward.
    width=[32,48,24,39][index%4];top=[18,32,7,44][index%4]
    d.polygon([(x,top),(x+9,top+25),(x-3,top+51),(x+15,113),(x+width,170),(x+width+9,256),(x+width-11,256),(x+width-20,176),(x-2,120),(x-14,top+57)],fill=(84,102,97,48))
    d.line([(x+11,top+27),(x+2,top+50),(x+19,110)],fill=(214,208,176,65),width=3)
for index,x in enumerate([118,366,591,824,1123,1415,1709,2030,2378,2675,2910]):
    y=[7,36,75,15][index%4];end=[68,120,179,95][index%4]
    path=[(x,y),(x-4,y+16),(x+7,y+29),(x+3,end)]
    d.line(path,fill=(83,98,91,100),width=2)
    d.line([(xx+2,yy) for xx,yy in path],fill=(206,206,175,70),width=1)
    if index%3==0:d.line([(x+4,y+28),(x+16,y+37),(x+30,y+38)],fill=(83,98,91,80),width=1)
# Occasional moss held at the grass lip, without a continuous dark stripe.
for a,b in [(110,220),(530,600),(1040,1160),(1710,1850),(2360,2440),(2840,2910)]:
    d.polygon([(a,0),(b,0),(b-8,5),(b-38,4),(b-43,9),(a+28,6),(a+10,11)],fill=(94,118,67,145))
image=Image.alpha_composite(image.convert('RGBA'),paint).convert('RGB')
image.save(OUT/'coastal_strata_color.png')
print(OUT/'coastal_strata_color.png')
