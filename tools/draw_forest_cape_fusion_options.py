"""Two-dimensional composition proposals only. No scene or model edits."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, json, hashlib

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/forest-cape-fusion-sketches'
OUT.mkdir(parents=True,exist_ok=True)
FONT='C:/Windows/Fonts/msyh.ttc'
S=2
P={'paper':'#f1ede2','ink':'#384b44','soft':'#6b786e','sea':'#aebdb6','sealine':'#c8d1c8',
   'grass':'#7b8b61','grasslight':'#91a077','grassdark':'#607653','soil':'#a69777',
   'rock':'#a49d89','rocklight':'#b9b19a','rockdark':'#777968','rockdeep':'#5d6a5e',
   'forest':'#4f6b56','forestfar':'#a2b09a','forestmid':'#7d9279','sand':'#cec1a0','fire':'#ce9055'}

def font(n):return ImageFont.truetype(FONT,n*S)
def text(d,x,y,t,n=22,c=None):d.text((x*S,y*S),t,font=font(n),fill=c or P['ink'])
def poly(d,pts,c,outline=False):
    p=[(round(x*S),round(y*S)) for x,y in pts];d.polygon(p,fill=c)
    if outline:d.line(p+[p[0]],fill=P['ink'],width=2*S,joint='curve')
def line(d,pts,c=None,w=2):d.line([(round(x*S),round(y*S)) for x,y in pts],fill=c or P['ink'],width=max(1,round(w*S)),joint='curve')
def ellipse(d,x,y,rx,ry,c,edge=None):d.ellipse(((x-rx)*S,(y-ry)*S,(x+rx)*S,(y+ry)*S),fill=c,outline=edge,width=S)
def curve(pts,n=32):
    a,b,c,e=pts
    return [tuple((1-t)**3*a[k]+3*(1-t)**2*t*b[k]+3*(1-t)*t*t*c[k]+t**3*e[k] for k in range(2)) for t in [i/n for i in range(n+1)]]
def arrow(d,pts,c=None,w=2):
    line(d,pts,c,w);a,b=pts[-2:];q=math.atan2(b[1]-a[1],b[0]-a[0])
    line(d,[(b[0]-10*math.cos(q-.45),b[1]-10*math.sin(q-.45)),b,(b[0]-10*math.cos(q+.45),b[1]-10*math.sin(q+.45))],c,w)
def dashed(d,a,b,c=None,w=1):
    length=math.hypot(b[0]-a[0],b[1]-a[1])
    for i in range(0,int(length),14):
        p=[(a[0]+(b[0]-a[0])*t/length,a[1]+(b[1]-a[1])*t/length) for t in [i,min(i+7,length)]]
        line(d,p,c,w)

def bamboo(d,x,y,h,far=False):
    color=P['forestfar'] if far else P['forest'];lean=14 if far else -11
    line(d,[(x,y),(x+lean*.4,y-h*.45),(x+lean,y-h)],color,2.2 if far else 3.2)
    for t in [.28,.49,.71,.9]:
        yy=y-h*t;xx=x+lean*t;line(d,[(xx-3,yy),(xx+3,yy)],color,1)
    # Deliberately grouped crowns, with clear gaps between the culms.
    for branch in [-1,1]:
        for q,off in [(0,0),(.15,14),(.27,-12)]:
            yy=y-h*(.7+q);xx=x+lean*(.7+q)
            tip=(xx+branch*(52+off),yy-20+off*.3)
            line(d,[(xx,yy),tip],color,1.2)
            for t in [.30,.58,.84]:
                lx=xx+(tip[0]-xx)*t;ly=yy+(tip[1]-yy)*t
                for direction in [-1,1]:
                    poly(d,[(lx,ly),(lx+branch*16,ly+direction*5-7),(lx+branch*34,ly+direction*12-9),(lx+branch*17,ly+direction*12)],color)

def grass_marks(d,positions):
    for x,y in positions:
        line(d,[(x-17,y+4),(x,y),(x+25,y+2)],P['grassdark'],1.3)
        line(d,[(x-6,y),(x-10,y-8),(x-2,y-2),(x+4,y-13),(x+9,y-2),(x+16,y-7)],P['grasslight'],1.4)

def rock(d,top,depth=70):
    # These are explicitly 2D drawn shapes; no mesh or 3D source is made.
    front=top[len(top)//2:]+[top[0]]
    bottom=[(x+5,y+depth) for x,y in front]
    poly(d,front+bottom[::-1],P['rockdark'])
    line(d,[front[0],(front[0][0]+3,front[0][1]+depth*.67)],P['rockdeep'],1.5)
    if len(front)>2:
        mid=front[len(front)//2];line(d,[mid,(mid[0]+7,mid[1]+depth)],P['rockdeep'],1.5)
    poly(d,top,P['rock'])
    line(d,top[1:4],P['ink'],1.7)
    inset=[(x*.82+sum(q[0] for q in top)/len(top)*.18,y*.82+sum(q[1] for q in top)/len(top)*.18) for x,y in top]
    poly(d,inset[:4],P['rocklight'])
    line(d,[top[1],inset[1],inset[2]],P['soft'],1)

def fire(d,x,y,scale=1):
    ellipse(d,x,y+4,26*scale,11*scale,P['soil'])
    for t in range(7):
        a=t*math.tau/7;ellipse(d,x+23*scale*math.cos(a),y+8*scale*math.sin(a),5*scale,3.7*scale,P['rockdark'])
    line(d,[(x-13*scale,y+1*scale),(x+14*scale,y+4*scale)],P['rockdeep'],5*scale)
    line(d,[(x-9*scale,y+6*scale),(x+9*scale,y-5*scale)],P['rockdeep'],4*scale)
    poly(d,[(x-9*scale,y),(x-3*scale,y-12*scale),(x,y-33*scale),(x+5*scale,y-15*scale),(x+10*scale,y-8*scale),(x+7*scale,y+1*scale)],P['fire'])
    line(d,[(x+2*scale,y-39*scale),(x-3*scale,y-56*scale),(x+5*scale,y-73*scale)],P['soft'],1)

def seat(d,x,y):
    poly(d,[(x-30,y-7),(x+30,y-9),(x+32,y+4),(x-28,y+7)],P['soil'],True)
    line(d,[(x-25,y-4),(x+22,y-5)],P['soft'],1.4)
    line(d,[(x-27,y+5),(x-24,y+12)],P['rockdeep'],2)
    line(d,[(x+25,y+3),(x+23,y+10)],P['rockdeep'],2)

def stair(d,x,y,dx=10):
    top=[(x-30,y),(x+29,y+4),(x+dx+49,y+111),(x+dx-43,y+112)]
    poly(d,top,P['rockdark'],True)
    for i in range(13):
        t=i/13;cx=x+dx*t;yy=y+112*t;ww=30+15*t
        line(d,[(cx-ww,yy),(cx+ww,yy+3)],P['rocklight'],5)
        line(d,[(cx-ww,yy+4),(cx+ww,yy+7)],P['rockdeep'],1)

spr=Image.open(ROOT/'assets/characters/green_three_walk/right_idle.png').convert('RGBA')
spr=spr.crop(spr.getbbox());spr.thumbnail((53*S,103*S),Image.Resampling.LANCZOS)
def hero(im,d,x,y):
    ellipse(d,x+13,y+2,24,5,P['grassdark'])
    im.alpha_composite(spr,(int(x*S-spr.width*.5),int(y*S-spr.height)))

OPTIONS=[
 {'key':'A','title':'草地包住岩角','extra':'短延伸 · 约 6–8 米','reason':'草坡伸到外缘，三块露岩嵌在同一坡体里。',
  'benefit':'篝火在小片露岩上，草地从两侧包进来。','change':'保留原横向路势；末端稍展开。','fire':(434,344),'seat':(552,350),'stair':(461,426),
  'top':[(330,293),(463,280),(615,291),(790,273),(1280,262),(1280,424),(800,440),(622,444),(498,443),(370,424),(277,379)],
  'rocks':[
   [(301,340),(333,303),(386,298),(415,326),(410,355),(359,377),(308,366)],
   [(277,380),(317,359),(378,378),(395,409),(364,431),(302,414)],
   [(502,421),(536,399),(598,397),(628,426),(600,452),(539,451)]],
  'bare':[(365,334),(388,315),(452,309),(498,319),(512,344),(490,365),(463,384),(397,378),(371,359)],
  'path':[(1170,376),(898,371),(718,366),(578,370),(502,379)],
  'planland':[(470,55),(275,55),(211,59),(164,78),(106,116),(94,156),(113,202),(158,215),(227,211),(282,235),(470,235)],
  'planrock':[(100,119),(132,91),(161,107),(164,145),(142,173),(104,166)],
  'planfire':(191,139),'planseat':(235,144),'planstairs':(178,206),'planpath':[(450,160),(320,160),(263,161),(214,175)],'origin':280},
 {'key':'B','title':'林缘凹入岩窝','extra':'最短延伸 · 约 3–5 米','reason':'篝火空地退回林缘，岩石沿海边围出浅窝。',
  'benefit':'利用原竹林尽头的空间，草路直接经过。','change':'原林地末端需要局部整理空地。','fire':(578,333),'seat':(677,349),'stair':(568,421),
  'top':[(459,303),(511,277),(607,274),(709,286),(832,268),(1280,262),(1280,424),(811,440),(704,445),(581,433),(489,410),(429,367)],
  'rocks':[
   [(449,335),(460,306),(506,290),(540,314),(533,344),(492,361)],
   [(430,369),(458,351),(504,365),(515,399),(486,419),(449,401)],
   [(614,420),(651,393),(703,402),(733,431),(714,452),(660,448)]],
  'bare':[(519,316),(552,295),(596,291),(633,307),(659,328),(635,349),(611,362),(558,355),(530,342)],
  'path':[(1170,376),(942,372),(793,373),(663,377),(551,389)],
  'planland':[(470,55),(287,55),(241,61),(207,71),(175,107),(162,151),(186,190),(232,210),(283,221),(470,235)],
  'planrock':[(170,115),(184,91),(210,78),(233,94),(230,120),(200,144),(172,137)],
  'planfire':(260,127),'planseat':(306,147),'planstairs':(249,209),'planpath':[(450,161),(360,161),(307,173),(255,179)],'origin':280},
 {'key':'C','title':'斜向叠岩收口','extra':'斜向短延伸 · 约 5–7 米','reason':'露岩顺草坡斜向错开，海边形成不对称收口。',
  'benefit':'草路略斜向篝火，外缘岩块上下嵌合。','change':'末端路线与石阶朝向需要小幅调整。','fire':(431,359),'seat':(548,352),'stair':(364,433),
  'top':[(428,283),(514,272),(657,286),(796,273),(1280,262),(1280,424),(854,440),(666,440),(519,458),(393,445),(296,425),(258,388),(329,340)],
  'rocks':[
   [(332,345),(383,306),(430,313),(455,343),(421,371),(365,376)],
   [(257,388),(294,370),(341,383),(356,415),(327,442),(285,428)],
   [(435,444),(478,414),(534,427),(557,455),(526,478),(474,469)]],
  'bare':[(383,361),(414,336),(465,333),(502,356),(512,382),(464,405),(413,393)],
  'path':[(1170,376),(930,369),(748,374),(629,391),(535,413)],
  'planland':[(470,55),(284,55),(226,68),(198,84),(183,119),(132,156),(101,191),(138,226),(197,240),(250,235),(297,229),(470,235)],
  'planrock':[(135,158),(170,133),(194,143),(196,173),(167,198),(135,190)],
  'planfire':(223,172),'planseat':(260,153),'planstairs':(147,224),'planpath':[(450,155),(328,158),(276,185),(221,213)],'origin':280}
]

def scene(o):
    im=Image.new('RGBA',(1280*S,550*S),P['paper']);d=ImageDraw.Draw(im)
    # Large quiet color fields, without noise or surface texture promises.
    poly(d,[(0,160),(1280,160),(1280,550),(0,550)],P['sea'])
    for y in [204,229,257,293,336,385,467,510]:
        for x,w in [(35,100),(183,78),(12,58)]:line(d,[(x,y),(x+w,y-2)],P['sealine'],1.2)
    for x,h in [(743,156),(802,180),(869,161),(934,196),(1015,173),(1080,204),(1162,183),(1252,190)]:bamboo(d,x,310,h,True)
    for x,h in [(756,178),(849,211),(936,183),(1049,224),(1167,205),(1262,221)]:bamboo(d,x,305,h)
    land=o['top'];front=land[5:]
    poly(d,front+[(x,y+92) for x,y in front[::-1]],P['rockdark'])
    poly(d,land,P['grass'],True)
    poly(d,[(800,280),(1280,266),(1280,330),(888,325),(696,324),(550,344),(600,316)],P['grassdark'])
    poly(d,[(670,381),(944,391),(1280,383),(1280,421),(805,436),(614,431),(565,414)],P['grasslight'])
    poly(d,o['bare'],P['soil'])
    for top,depth in zip(o['rocks'],[48,72,57]):rock(d,top,depth)
    # Turf overlaps the roots of the rocks, giving both materials one contour.
    if o['key']=='A':
        poly(d,[(397,294),(462,283),(583,299),(547,323),(497,335),(459,315),(427,316)],P['grass'])
        poly(d,[(483,361),(539,346),(610,367),(600,401),(550,417),(495,407),(513,382)],P['grass'])
    elif o['key']=='B':
        poly(d,[(539,285),(612,279),(715,290),(690,320),(644,308),(610,301),(577,305),(550,321)],P['grass'])
        poly(d,[(523,352),(553,356),(619,365),(702,359),(696,392),(618,410),(530,399)],P['grass'])
    else:
        poly(d,[(455,289),(568,280),(669,296),(609,324),(533,336),(483,319)],P['grass'])
        poly(d,[(470,390),(545,361),(636,363),(612,407),(536,431),(482,428),(491,412)],P['grass'])
    # A muted footpath marks continuous ground; it has no hard shoulder seam.
    pts=o['path'];line(d,curve([pts[0],pts[1],pts[2],pts[-1]],60),P['soil'],18)
    line(d,curve([pts[0],pts[1],pts[2],pts[-1]],60),P['grasslight'],7)
    for x,y in [(727,340),(807,394),(899,346),(1003,411),(1109,349),(1203,408),(650,405),(601,326)]:grass_marks(d,[(x,y)])
    poly(d,[(245,515),(o['stair'][0]-72,496),(o['stair'][0]+90,506),(730,530),(800,550),(240,550)],P['sand'])
    stair(d,*o['stair'])
    seat(d,*o['seat']);fire(d,*o['fire'])
    hero(im,d,846,370)
    text(d,36,20,'横向构图草图',20,P['soft'])
    text(d,942,20,'同一人物尺度 · 单一连续地形',18,P['soft'])
    text(d,37,83,'海',21,P['soft'])
    text(d,998,240,'现有竹林',19,P['paper'])
    fx,fy=o['fire'];arrow(d,[(fx-100,fy-80),(fx-45,fy-65),(fx-19,fy-30)],P['soft'],1.3);text(d,fx-153,fy-109,'篝火空地',18)
    sx,sy=o['stair'];text(d,sx+60,sy+77,'下到沙滩',18,P['ink'])
    return im.convert('RGB')

def plan(o):
    im=Image.new('RGB',(500*S,350*S),P['paper']);d=ImageDraw.Draw(im)
    text(d,14,8,'俯视布局',20,P['soft'])
    poly(d,[(0,48),(500,48),(500,285),(0,285)],P['sea'])
    poly(d,o['planland'],P['grasslight'],True)
    for x in [327,368,410,453]:
        for y in [78,113]:
            ellipse(d,x,y,14,12,P['grassdark'])
            line(d,[(x-7,y-5),(x+8,y+5)],P['forest'],1.2)
    poly(d,o['planrock'],P['rock'],True)
    q=o['planrock'];poly(d,[(x+43,y+67) for x,y in q],P['rock'],True)
    fx,fy=o['planfire'];ellipse(d,fx,fy,23,15,P['soil']);fire(d,fx,fy,.45)
    x,y=o['planseat'];line(d,[(x-11,y),(x+12,y+3)],P['rockdeep'],5)
    path=o['planpath'];arrow(d,path,P['ink'],1.8)
    sx,sy=o['planstairs'];poly(d,[(sx-13,sy-7),(sx+15,sy-5),(sx+18,sy+47),(sx-16,sy+47)],P['rockdark'])
    for i in range(6):line(d,[(sx-13,sy+i*7),(sx+16,sy+i*7)],P['rocklight'],2)
    text(d,354,189,'竹林草路',17)
    text(d,8,261,'海 / 沙滩',17,P['soft'])
    # An authoring locator only, not a boundary proposed for the finished art.
    dashed(d,(o['origin'],48),(o['origin'],241),P['soft'],1)
    text(d,266,294,'虚线：原林地末端定位',17,P['soft'])
    text(d,14,323,'示意比例，非最终施工尺寸',16,P['soft'])
    return im

board=Image.new('RGB',(1800*S,2070*S),P['paper']);bd=ImageDraw.Draw(board)
text(bd,54,25,'竹林与岛角 · 先定整体，再建模',34)
text(bd,56,79,'三种紧凑布局：比较草坡、露岩、篝火与石阶怎样组成同一处林缘。',22,P['soft'])
for i,o in enumerate(OPTIONS):
    y=138+i*636
    text(bd,54,y,f"{o['key']}  {o['title']}",29)
    text(bd,880,y+4,o['extra'],21,P['soft'])
    visual=scene(o);top=plan(o)
    board.paste(visual.resize((1240*S,533*S),Image.Resampling.LANCZOS),(42*S,(y+51)*S))
    board.paste(top,((1280)*S,(y+51)*S))
    text(bd,59,y+593,o['reason']+'  '+o['benefit'],20)
    text(bd,1294,y+411,o['change'],17,P['soft'])
    if i<2:line(bd,[(54,y+623),(1747,y+623)],'#d2d5c7',1)
    # Keep a full-size option sheet with the entire stair/sea composition.
    sheet=Image.new('RGB',(1800*S,1040*S),P['paper']);sd=ImageDraw.Draw(sheet)
    text(sd,52,31,f"{o['key']}  {o['title']}",34);text(sd,54,84,o['extra']+' · 布局提案，未修改模型',22,P['soft'])
    sheet.paste(visual,(32*S,150*S));sheet.paste(top,(1290*S,170*S))
    text(sd,57,750,o['reason'],27);text(sd,57,806,o['benefit'],27)
    text(sd,58,874,o['change'],23,P['soft'])
    text(sd,58,956,'颜色和笔触仅用于分清草、土、石；最终材质、光照、尺寸和石阶级数待选定布局后确定。',20,P['soft'])
    sheet=sheet.resize((1800,1040),Image.Resampling.LANCZOS);sheet.save(OUT/f"option-{o['key'].lower()}.png")
    visual.resize((1280,550),Image.Resampling.LANCZOS).save(OUT/f"scene-{o['key'].lower()}.png")
    top.resize((500,350),Image.Resampling.LANCZOS).save(OUT/f"plan-{o['key'].lower()}.png")
board=board.resize((1800,2070),Image.Resampling.LANCZOS);board.save(OUT/'three-options.png')
record={'date':'2026-11-19','kind':'2D layout and composition sketches','modeling_performed':False,
        'image_generation_used':False,'hero_reference':'assets/characters/green_three_walk/right_idle.png',
        'proposals':[{k:o[k] for k in ['key','title','extra','reason','benefit','change']} for o in OPTIONS]}
(OUT/'proposals.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print('Saved three 2D proposal sheets and comparison. No Blender or Godot operation.')
