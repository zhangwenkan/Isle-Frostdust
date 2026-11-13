"""2D line composition studies, not 3D models or in-game screenshots."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/cape-shape-options'
S=3;W=830;H=790
PAPER='#fbfaf6';INK='#293b3d';GRAY='#89948f'
im=Image.new('RGB',(W*S,H*S),PAPER);d=ImageDraw.Draw(im)
font='C:/Windows/Fonts/msyh.ttc'
def txt(x,y,s,size=22,color=INK):d.text((x*S,y*S),s,font=ImageFont.truetype(font,size*S),fill=color)
def stroke(points,color=INK,width=2):d.line([(int(x*S),int(y*S)) for x,y in points],fill=color,width=int(width*S),joint='curve')
def poly(points,fill):d.polygon([(int(x*S),int(y*S)) for x,y in points],fill=fill)
def curve(p0,p1,p2,p3):
 return [tuple((1-t)**3*p0[j]+3*(1-t)**2*t*p1[j]+3*(1-t)*t*t*p2[j]+t**3*p3[j] for j in (0,1)) for t in [i/48 for i in range(1,49)]]
def project(p,offset):return (offset+90+(p[0]-60)*.94-(p[1]-76)*.14,270+(p[1]-76)*.52)

paths={
'C':[(720,76),(326,76),(176,113),(92,180),(122,287),(288,328),(720,328)],
'D':[(720,76),(430,76)]+curve((430,76),(370,76),(360,122),(315,119))+curve((315,119),(277,116),(276,70),(213,67))+curve((213,67),(120,62),(68,118),(73,200))+curve((73,200),(76,287),(162,328),(280,328))+[(720,328)]
}
src=Image.open(ROOT/'assets/characters/green_three_walk/right_idle.png').convert('RGBA')
src=src.crop(src.getbbox());a=src.getchannel('A');a=a.point(lambda x:255 if x>100 else 0)
a=a.resize((28*S,94*S),Image.Resampling.LANCZOS)
outline=a.filter(ImageFilter.MaxFilter(7))
txt(48,32,'C + D · 宽角与后缘凹湾',33)
txt(50,86,'宽斜切岩岸 + 后缘凹湾 + 连续厚实的陆地',23,'#677271')

paths['C']=[(720, 76), (430, 76), (385, 100), (351, 136), (317, 142), (285, 120), (263, 88), (224, 67), (176, 80), (92, 145), (74, 214), (120, 287), (288, 328), (720, 328)]
for i,k in enumerate(['C']):
 off=i*810
 txt(off+50,162,'合并方案',29)
 p=paths[k];near=p[10:]
 screen=[project(q,off) for q in p]
 edge=[project(q,off) for q in near]
 bottom=[(x,y+135) for x,y in edge]
 poly(edge+bottom[::-1],'#edeee9')
 stroke(bottom,INK,2)
 stroke([edge[0],bottom[0]],INK,2)
 # Simple cliff divisions indicate thickness, with no texture/detail study.
 if k=='C':cuts=[(122,287),(288,328)]
 else:cuts=[(104,272),(220,321)]
 for q in cuts:
  x,y=project(q,off);stroke([(x,y),(x+6,y+68),(x,y+135)],GRAY,1.3)
 poly(screen,'#ffffff');stroke(screen,INK,3)
 # The open eastern end denotes continuation into the current island.
 for q in [(660,80),(660,328)]:
  x,y=project(q,off);stroke([(x-4,y-5),(x+4,y+5)],GRAY,1)
 # The lane is horizontal in screen space and starts beside the camp corner.
 start=project((292,262),off);end=project((707,262),off)
 length=end[0]-start[0]
 for j in range(0,int(length),17):stroke([(start[0]+j,start[1]),(start[0]+min(j+9,length),start[1])],GRAY,1.7)
 stroke([(end[0]-11,end[1]-5),end,(end[0]-11,end[1]+5)],GRAY,1.7)
 txt(end[0]-180,end[1]+6,'横向行走',18,'#677271')
 hx,hy=project((351,262),off)
 # Outline taken from the same standing sprite in both compositions.
 px=int((hx-12)*S);py=int((hy-94)*S)
 im.paste(Image.new('RGB',outline.size,INK),(px,py),outline)
 im.paste(Image.new('RGB',a.size,'#ffffff'),(px,py),a)
 txt(hx-12,hy+6,'人',18)
 fx,fy=project((207,172) if k=='C' else (195,165),off)
 ellipse=[(fx+33*math.cos(j*math.pi/48),fy+10*math.sin(j*math.pi/48)) for j in range(97)]
 stroke(ellipse,INK,1.6)
 for angle in [-1.0,.2,1.4,2.8,3.8]:
  x=fx+31*math.cos(angle);y=fy+10*math.sin(angle)
  pts=[(x-5,y-3),(x+3,y-4),(x+6,y+2),(x+2,y+5),(x-5,y+3),(x-5,y-3)]
  poly(pts,PAPER);stroke(pts,INK,1.3)
 for x1,y1,x2,y2 in [(-25,-6,22,2),(-18,5,18,-12),(-7,-15,11,7)]:
  stroke([(fx+x1,fy+y1),(fx+x2,fy+y2)],INK,5)
 txt(fx-24,fy-82,'篝火',20)
 txt(off+615,304,'原岛方向',18,'#677271')
 txt(off+43,425,'海',20,'#677271')
 if k=='C':
  txt(off+50,632,'后缘切出凹湾，角落略有分隔。',22)
  txt(off+50,671,'前侧保持宽实连接，横向路从旁经过。',20,'#677271')
 else:
  txt(off+50,632,'浅凹湾增加一层前后关系。',22)
  txt(off+50,671,'外缘可再加少量切角，避免过圆。',20,'#677271')

stroke([(50,738),(1580,738)],'#d3d7d2',1)
txt(50,754,'仅用于选择轮廓，尚未修改模型。',19,'#677271')
im.resize((W,H),Image.Resampling.LANCZOS).save(OUT/'cape-combined-view.png')
print(OUT/'cape-combined-view.png')
