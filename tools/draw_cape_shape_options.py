"""Flat shoreline proposal drawings only; does not modify scene assets."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import html

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/cape-shape-options'
OUT.mkdir(parents=True, exist_ok=True)
W, H, S = 1660, 1210, 2
PAPER, INK, SOFT, GUIDE = '#fbfaf6', '#293b3d', '#677271', '#9aa4a0'
im = Image.new('RGB', (W*S, H*S), PAPER)
draw = ImageDraw.Draw(im)
font_path = 'C:/Windows/Fonts/msyh.ttc'
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       f'<rect width="{W}" height="{H}" fill="{PAPER}"/>']

def text(x, y, label, size=22, color=INK):
    draw.text((x*S, y*S), label, font=ImageFont.truetype(font_path, size*S), fill=color)
    svg.append(f'<text x="{x}" y="{y+size}" font-family="Microsoft YaHei,sans-serif" font-size="{size}" fill="{color}">{html.escape(label)}</text>')

def line(points, color=INK, width=2, dashed=False):
    if dashed:
        a, b = points
        from math import hypot
        length = hypot(b[0]-a[0], b[1]-a[1])
        for i in range(0, int(length), 17):
            t1, t2 = i/length, min(i+9, length)/length
            p = [(a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t) for t in [t1,t2]]
            draw.line([(round(x*S),round(y*S)) for x,y in p], fill=color, width=round(width*S))
    else:
        draw.line([(round(x*S),round(y*S)) for x,y in points], fill=color, width=round(width*S), joint='curve')
    dash = ' stroke-dasharray="9 8"' if dashed else ''
    svg.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{dash}/>')

def circle(x,y,r,color=INK,width=2,fill=PAPER):
    draw.ellipse(((x-r)*S,(y-r)*S,(x+r)*S,(y+r)*S),fill=fill,outline=color,width=round(width*S))
    svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{color}" stroke-width="{width}"/>')

def shore(commands, ox, oy):
    points=[];d=[];current=None
    for cmd in commands:
        if cmd[0] in ['M','L']:
            current=(cmd[1]+ox,cmd[2]+oy);points.append(current)
            d.append(f'{cmd[0]} {current[0]} {current[1]}')
        else:
            p0=current;p1=(cmd[1]+ox,cmd[2]+oy);p2=(cmd[3]+ox,cmd[4]+oy);p3=(cmd[5]+ox,cmd[6]+oy)
            for j in range(1,49):
                t=j/48;q=1-t
                points.append((q**3*p0[0]+3*q*q*t*p1[0]+3*q*t*t*p2[0]+t**3*p3[0],q**3*p0[1]+3*q*q*t*p1[1]+3*q*t*t*p2[1]+t**3*p3[1]))
            current=p3;d.append(f'C {p1[0]} {p1[1]} {p2[0]} {p2[1]} {p3[0]} {p3[1]}')
    draw.polygon([(round(x*S),round(y*S)) for x,y in points],fill='#ffffff')
    draw.line([(round(x*S),round(y*S)) for x,y in points],fill=INK,width=6,joint='curve')
    svg.append(f'<path d="{" ".join(d)}" fill="#ffffff" stroke="{INK}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')

options = [
 ('A','宽圆角','一整块圆弧岸线，宽宽地接回原岛',
  [('M',720,76),('L',275,76),('C',100,76,65,105,65,211),('C',65,300,139,328,271,328),('L',720,328)], (195,158)),
 ('B','多边形切角','用几段折线切出宽角，外侧有一段平面',
  [('M',720,76),('L',270,76),('L',160,89),('L',85,150),('L',85,252),('L',155,317),('L',270,328),('L',720,328)], (195,158)),
 ('C','斜切宽角','不对称地斜切，转折与篝火形成错位',
  [('M',720,76),('L',326,76),('L',176,113),('L',92,180),('L',122,287),('L',288,328),('L',720,328)], (207,172)),
 ('D','浅凹圆角','宽圆角后缘凹进一点，保留宽阔连接',
  [('M',720,76),('L',430,76),('C',370,76,360,122,315,119),('C',277,116,276,70,213,67),('C',120,62,68,118,73,200),('C',76,287,162,328,280,328),('L',720,328)], (195,165)),
]

text(48,28,'岛角轮廓 · 俯视线稿',34)
text(50,82,'篝火在后侧宽地，人物沿横向虚线行走。右侧接现有岛体。',23,SOFT)
text(1320,40,'形状提案 / 未改模型',20,SOFT)

for i,(letter,title,desc,commands,fire) in enumerate(options):
    ox=50+(i%2)*810;oy=158+(i//2)*492
    text(ox,oy,f'{letter}  {title}',28)
    text(ox,oy+44,desc,20,SOFT)
    dy=oy+94
    shore(commands,ox,dy)
    # All proposals share the same walk line and actor anchor.
    line([(ox+292,dy+262),(ox+707,dy+262)],GUIDE,2,True)
    line([(ox+696,dy+256),(ox+707,dy+262),(ox+696,dy+268)],GUIDE,2)
    circle(ox+351,dy+262,9,INK,2.2,'#ffffff')
    text(ox+333,dy+281,'人',19)
    text(ox+470,dy+278,'横向行走',19,SOFT)
    text(ox+590,dy+164,'接原岛',20,SOFT)
    text(ox+12,dy+196,'海',20,SOFT)
    fx,fy=ox+fire[0],dy+fire[1]
    circle(fx,fy,22,INK,2,'#ffffff')
    line([(fx-13,fy-11),(fx+13,fy+11)],INK,3)
    line([(fx-13,fy+11),(fx+13,fy-11)],INK,3)
    text(fx+34,fy-16,'篝火',20)
    text(fx+34,fy+12,'不可走入',17,SOFT)

line([(48,1118),(1610,1118)],'#d3d7d2',1)
text(50,1140,'仅比较岸线形状与相对位置；实际尺寸、岩壁和植被等选定后再细化。',21,SOFT)
svg.append('</svg>')
(OUT/'cape-shapes.svg').write_text('\n'.join(svg),encoding='utf8')
im.resize((W,H),Image.Resampling.LANCZOS).save(OUT/'cape-shapes.png')
for i,(letter,*_) in enumerate(options):
    x=40+(i%2)*810;y=148+(i//2)*492
    im.crop((x*S,y*S,(x+780)*S,(y+470)*S)).resize((1170,705),Image.Resampling.LANCZOS).save(OUT/f'option-{letter.lower()}.png')
print(OUT/'cape-shapes.png')
