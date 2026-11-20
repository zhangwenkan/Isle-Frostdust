"""Reference reading and 2D composition study. Does not author 3D geometry."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib
import json
import math
import random
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/forest-rocky-terminus-study'
REF = Path('C:/Users/51440/AppData/Local/Temp/codex-clipboard-39930263-7396-4e08-ad69-cbd7f4ba08b7.png')
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'reference').mkdir(exist_ok=True)
shutil.copy2(REF, OUT / 'reference/user-forest-coast.png')
S = 2
FONT = 'C:/Windows/Fonts/msyh.ttc'
P = dict(paper='#eeeadd', ink='#37473b', soft='#687568', sea='#a7b9b5',
         foam='#d1dbcd', sand='#c8b893', grass='#80915e', grasslight='#a0aa73',
         grassdark='#596d49', forest='#466047', far='#94a38b', mid='#758a72',
         rock='#9f9980', top='#c1b596', side='#7a806d', dark='#536454',
         path='#b09e7b', fire='#cc8c44')

def canvas(w, h, color=None):
    return Image.new('RGB', (w*S, h*S), color or P['paper'])

def text(d, x, y, t, n=20, color=None):
    d.text((int(x*S), int(y*S)), t, font=ImageFont.truetype(FONT, n*S), fill=color or P['ink'])

def line(d, pts, color=None, w=1.5):
    d.line([(int(x*S), int(y*S)) for x,y in pts], fill=color or P['ink'], width=max(1, int(w*S)), joint='curve')

def poly(d, pts, color, edge=False):
    d.polygon([(int(x*S), int(y*S)) for x,y in pts], fill=color)
    if edge:
        line(d, pts + [pts[0]], w=1.5)

def ellipse(d, x, y, rx, ry, color):
    d.ellipse(((x-rx)*S, (y-ry)*S, (x+rx)*S, (y+ry)*S), fill=color)

def arrow(d, pts, color=None, w=2):
    line(d, pts, color, w)
    a,b=pts[-2:]
    ang=math.atan2(b[1]-a[1], b[0]-a[0])
    line(d, [(b[0]-10*math.cos(ang-.5),b[1]-10*math.sin(ang-.5)),b,
             (b[0]-10*math.cos(ang+.5),b[1]-10*math.sin(ang+.5))], color, w)

def mark(d, x, y, n):
    ellipse(d, x, y, 16,16,P['paper'])
    d.ellipse(((x-16)*S,(y-16)*S,(x+16)*S,(y+16)*S),outline=P['ink'],width=2*S)
    text(d,x-7,y-14,str(n),20)

def bamboo(d, x, y, h, tint, lean=0, thin=False):
    line(d,[(x,y),(x+lean*.45,y-h*.5),(x+lean,y-h)],tint,2 if thin else 3)
    for f in [.23,.4,.59,.76,.94]:
        px=x+lean*f; py=y-h*f
        line(d,[(px-3,py),(px+3,py)],tint,1)
    for f,spread in [(.6,36),(.78,46),(.93,32)]:
        px=x+lean*f;py=y-h*f
        for sign in [-1,1]:
            end=(px+sign*spread,py-19)
            line(d,[(px,py),end],tint,1)
            for t in [.28,.54,.8]:
                qx=px+(end[0]-px)*t;qy=py+(end[1]-py)*t
                for direction in [-1,1]:
                    poly(d,[(qx,qy),(qx+sign*12,qy+direction*5-4),
                            (qx+sign*24,qy+direction*10-4),(qx+sign*11,qy+direction*9)],tint)

def grass(d,x,y,size=1):
    ellipse(d,x,y+1,17*size,4*size,P['grassdark'])
    for dx,dy in [(-15,-4),(-7,-14),(0,-10),(7,-18),(16,-6)]:
        line(d,[(x,y),(x+dx*size,y+dy*size)],P['grasslight'],1.5)

def rockface(d,top,front,depth,light=True):
    # A drawn face and structure marks, never a mesh.
    bottom=[(x+4,y+depth) for x,y in front]
    poly(d,front+bottom[::-1],P['side'])
    for i,(x,y) in enumerate(front):
        if i%2==0:
            line(d,[(x,y),(x-3,y+depth*.38),(x+4,y+depth*.82)],P['dark'],1.5)
    poly(d,top,P['top'] if light else P['rock'])
    line(d,front,P['dark'],2)
    if len(top)>4:
        line(d,[top[1],top[2],top[3]],P['rock'],1)

def camp(d,x,y):
    ellipse(d,x,y+2,28,10,P['rock'])
    for i in range(7):
        a=i*math.tau/7
        ellipse(d,x+23*math.cos(a),y+7*math.sin(a),5,3,P['side'])
    line(d,[(x-12,y+2),(x+11,y-3)],P['dark'],5)
    poly(d,[(x-9,y),(x-4,y-16),(x+1,y-39),(x+5,y-17),(x+11,y-5),(x+7,y+2)],P['fire'])
    line(d,[(x+1,y-42),(x-3,y-57),(x+3,y-75)],P['soft'],1)
    poly(d,[(x+48,y-9),(x+95,y-5),(x+97,y+3),(x+49,y)],P['path'],True)

def save(im,name):
    im.resize((im.width//S,im.height//S),Image.Resampling.LANCZOS).save(OUT/name)

# Read the actual new reference, adding numbered observations outside the image.
ref=Image.open(REF).convert('RGB')
ref=ref.resize((1600*S,667*S),Image.Resampling.LANCZOS)
analysis=canvas(1600,970)
ad=ImageDraw.Draw(analysis)
text(ad,28,18,'新参考：竹林、岩岸和篝火属于同一片地形',28)
analysis.paste(ref,(0,70*S))
for n,(x,y) in enumerate([(477,342),(844,291),(1156,460),(1265,369)],1):
    mark(ad,x,y+70,n)
notes=[('篝火嵌在林岸开口','空地的石面接着道路，背后仍有竹林和岩层。'),
       ('竹子长到岩缘','草土留在岩层之间；林与岩没有整齐分界。'),
       ('崖体延续到林下','前侧岩层构成共同基底，不能只在左端摆几块石。'),
       ('路与空地直接相接','利用已有林端空间，开口见海；没有一段细长连接坡。')]
for i,(a,b) in enumerate(notes):
    col=i%2;row=i//2;x=32+col*790;y=767+row*92
    mark(ad,x+16,y+16,i+1)
    text(ad,x+45,y,a,23)
    text(ad,x+45,y+35,b,19,P['soft'])
save(analysis,'reference-reading.png')

# One revised proposal in the game's fixed lateral view, with mild perspective.
im=canvas(1600,770)
d=ImageDraw.Draw(im)
text(d,28,18,'竹林临海收尾 · 整体布局草图',28)
text(d,28,60,'篝火空地纳入林端，岩层延续到林下。比例、轮廓和路线均为待讨论示意。',19,P['soft'])

# Sea and low-key distant atmosphere, left of a closing forest.
poly(d,[(25,145),(1575,145),(1575,661),(25,661)],P['sea'])
for i in range(13):
    y=225+i*29
    line(d,[(32,y),(205+(i%3)*21,y-3)],P['foam'],.8)
text(d,54,178,'临海开口',19,P['soft'])

# All land shares an irregular edge, ending beside the camp without a neck.
land=[(369,353),(446,313),(567,296),(661,302),(757,299),(898,287),(1111,286),
      (1320,282),(1575,289),(1575,531),(1477,536),(1390,554),(1264,547),
      (1161,560),(1042,547),(922,550),(806,535),(720,541),(639,526),
      (555,533),(469,513),(407,500),(348,471),(321,415)]
front=land[9:]+[land[0]]
bottom=[(x,y+103) for x,y in front]
poly(d,front+bottom[::-1],P['side'])
poly(d,[(295,639),(410,616),(499,630),(614,640),(819,661),(322,661)],P['sand'])
line(d,[(292,641),(341,635),(390,622),(414,625)],P['foam'],3)
poly(d,land,P['grass'])

# Distant painted forest only; it stops naturally towards the sea opening.
for x,h in [(662,208),(717,244),(779,232),(845,241),(912,227),(981,254),(1063,250),
            (1137,245),(1211,254),(1294,231),(1381,260),(1455,249),(1535,245)]:
    bamboo(d,x,335,min(h*.72,335-157),P['far'],lean=8,thin=True)
for x,h in [(682,239),(802,247),(932,246),(1053,241),(1177,266),(1323,243),(1450,272)]:
    bamboo(d,x,350,min(h*.72,350-157),P['mid'],lean=-9,thin=True)

# Bedrock rises behind the clearing and runs inside the forest roots.
ridge=[(423,345),(473,312),(552,284),(607,291),(655,278),(710,303),
       (783,305),(831,334),(899,334),(943,360),(927,389),(832,391),
       (749,367),(675,377),(605,348),(526,369),(455,372)]
ridgefront=[(423,345),(455,372),(526,369),(605,348),(675,377),(749,367),(832,391),(927,389)]
rockface(d,ridge,ridgefront,43,False)
poly(d,[(530,300),(584,307),(604,329),(591,346),(631,352),(666,327),
        (680,307),(707,318),(746,332),(769,354),(812,355),(849,375),
        (834,389),(784,377),(750,364),(693,371),(650,359),(590,357),(538,339)],P['grassdark'])

# The rocky camp surface is flush with the soil path: interlocking shape, no seam bar.
clearing=[(347,404),(367,369),(419,354),(485,357),(533,370),(573,383),
          (610,394),(649,413),(640,430),(695,441),(652,457),(626,461),
          (584,484),(539,482),(509,505),(466,497),(411,499),(370,472),(338,441)]
poly(d,clearing,P['top'])
poly(d,[(510,391),(558,388),(576,405),(616,408),(602,424),(655,433),
        (636,446),(595,450),(570,469),(532,465),(538,446),(518,430)],P['path'])

# Path widens into the same opening; paving becomes exposed rock progressively.
path=[(1575,418),(1370,417),(1203,426),(1051,423),(932,431),(812,431),
      (714,437),(629,424),(571,415),(574,449),(640,461),(729,478),
      (827,476),(945,473),(1076,465),(1216,474),(1378,461),(1575,460)]
poly(d,path,P['path'])
for x,y,w,h in [(663,444,29,12),(726,449,25,10),(800,451,19,9),(875,453,21,9),
                 (959,451,16,8),(1075,445,14,7),(1220,453,12,7),(1400,439,11,6)]:
    poly(d,[(x-w,y),(x-9,y-h),(x+w,y-h+3),(x+w-4,y+5),(x,y+8)],P['rock'])
    line(d,[(x-w,y),(x,y+8),(x+w-4,y+5)],P['side'],1)
for pts in [[(370,399),(416,391),(450,406)],[(465,368),(476,398),(520,416)],
            [(412,455),(463,447),(486,478)],[(513,431),(544,447),(561,471)]]:
    line(d,pts,P['rock'],1.4)

# A few main culms: they root in the rock/soil pockets, including behind camp.
for x,y,h,lean in [(526,341,235,5),(585,350,272,-7),(677,367,249,8),(751,372,289,-7),
                  (869,383,258,4),(1012,392,292,-5),(1148,390,269,7),(1305,382,293,-7),
                  (1450,388,274,7),(1540,382,270,-8)]:
    bamboo(d,x,y,min(h*.72,y-157),P['forest'],lean)
    grass(d,x,y,1)

# An exposed front rock shelf runs under both camp and forest: irregular, not pillars.
poly(d,[(339,448),(375,471),(411,489),(466,487),(491,507),(511,495),
        (538,513),(546,538),(521,588),(474,581),(456,572),(412,587),
        (373,557),(353,514)],P['side'])
poly(d,[(343,444),(374,456),(405,469),(433,468),(444,483),(476,478),
        (490,500),(455,507),(416,494),(382,504),(353,478)],P['rock'])
poly(d,[(644,504),(695,505),(734,524),(809,518),(836,534),(933,530),
        (974,543),(1040,537),(1096,552),(1152,545),(1200,560),(1240,550),
        (1290,559),(1380,550),(1444,554),(1575,538),(1575,613),(1450,620),
        (1386,637),(1263,627),(1156,642),(1048,629),(921,632),(809,616),
        (734,624),(650,611)],P['side'])
for pts in [[(691,519),(719,549),(709,594)],[(843,535),(830,573),(842,606)],
            [(1017,542),(1025,575),(1012,619)],[(1197,556),(1187,579),(1200,628)],
            [(1380,552),(1398,580),(1390,626)]]:
    line(d,pts,P['dark'],1.5)
poly(d,[(674,496),(714,503),(748,494),(800,507),(832,504),(863,521),
        (826,535),(801,525),(754,536),(717,522),(683,528)],P['rock'])
poly(d,[(707,494),(756,498),(780,507),(795,521),(751,516),(719,511)],P['grassdark'])

# Single down-going stair notch, no extra upper staircase.
st=[(548,515),(605,518),(644,640),(551,640)]
poly(d,st,P['dark'])
for i in range(14):
    t=i/14;y=517+123*t;lx=548+3*t;rx=605+39*t
    poly(d,[(lx,y),(rx,y+2),(rx+1,y+7),(lx,y+6)],P['rock'])
    line(d,[(lx,y),(rx,y+2)],P['top'],2.8)
line(d,[(549,515),(605,518)],P['top'],3)

# Grouped grass keeps islands of soil and exposed stone legible.
for x,y in [(464,367),(614,384),(647,405),(735,396),(808,416),(891,412),(1002,420),
            (1119,418),(1230,399),(1390,412),(1500,410),(662,489),(774,484),
            (914,495),(1053,509),(1186,502),(1329,514),(1456,496),(1518,503)]:
    grass(d,x,y,.85)
camp(d,440,424)

spr=Image.open(ROOT/'assets/characters/green_three_walk/right_idle.png').convert('RGBA')
spr=spr.crop(spr.getbbox())
spr.thumbnail((53*S,103*S),Image.Resampling.LANCZOS)
ellipse(d,973,459,21,4,P['grassdark'])
im.paste(spr,(int(973*S-spr.width/2),int(459*S-spr.height)),spr)

# View labels have short leaders and live in intentionally empty margins.
text(d,47,288,'篝火是林端开口',20)
arrow(d,[(225,310),(310,335),(405,388)],P['soft'],1.3)
poly(d,[(770,244),(1005,244),(1005,276),(770,276)],P['paper'])
text(d,780,247,'竹林沿岩层长到海边',20)
arrow(d,[(780,278),(707,299),(644,322)],P['soft'],1.3)
text(d,1224,576,'共同的岩质基底',20)
text(d,511,673,'唯一一条下到沙滩的石阶',19)
text(d,45,718,'固定横向取景 · 路面与空地同一层 · 不设独立连接坡 · 不确定最终尺寸、石阶级数或材质',19,P['soft'])
save(im,'lateral-draft.png')

# Top view validates the compact unified footprint and the route without a bottleneck.
plan=canvas(1600,660)
pd=ImageDraw.Draw(plan)
text(pd,28,20,'俯视布局 · 一整片林岸在左侧结束',28)
text(pd,28,64,'海只在林端打开；林内仍保留原有深林背景。虚线区域是建议一起调整的末端范围。',19,P['soft'])
poly(pd,[(32,121),(1568,121),(1568,579),(32,579)],P['sea'])
foot=[(470,179),(610,151),(811,160),(1045,157),(1300,151),(1533,153),
      (1533,477),(1380,475),(1220,491),(1065,471),(903,482),(745,467),
      (631,482),(526,460),(451,423),(408,360),(407,280)]
poly(pd,foot,P['grass'],True)
poly(pd,[(414,270),(446,218),(499,199),(535,210),(555,257),(520,283),
         (553,307),(644,301),(671,281),(735,284),(774,313),(737,330),
         (650,328),(583,341),(514,324),(446,330)],P['rock'])
poly(pd,[(479,294),(520,283),(576,293),(606,328),(650,346),(649,383),
         (601,419),(547,428),(470,401),(449,358)],P['top'])
poly(pd,[(608,343),(686,362),(807,364),(999,359),(1240,357),(1533,356),
         (1533,393),(1250,397),(1003,398),(810,407),(675,401),(597,389)],P['path'])
poly(pd,[(478,404),(534,428),(557,451),(543,470),(517,483),(476,445),(451,423)],P['side'])
poly(pd,[(618,446),(659,451),(699,448),(741,467),(780,463),(807,475),
         (766,493),(696,483),(647,492),(620,473)],P['side'])
poly(pd,[(437,497),(526,491),(626,514),(694,546),(418,545)],P['sand'])
poly(pd,[(551,420),(607,424),(608,535),(550,535)],P['side'])
for y in range(432,532,9):
    line(pd,[(553,y),(604,y)],P['top'],4)
for x,y,r in [(577,228,27),(669,231,29),(751,232,24),(856,222,28),(960,226,29),
              (1080,223,27),(1180,231,24),(1287,219,31),(1406,226,28),
              (706,303,20),(833,308,21),(947,296,21),(1063,295,24),(1200,305,22),
              (1350,300,24),(1460,310,25)]:
    ellipse(pd,x,y,r,r*.64,P['forest'])
    line(pd,[(x-7,y-8),(x+8,y+9)],P['grassdark'],1)
camp(pd,519,346)
arrow(pd,[(1468,377),(1180,379),(944,380),(756,386),(650,379),(591,355)],P['ink'],2)
arrow(pd,[(596,395),(578,438),(578,519)],P['ink'],2)
for a,b in [((767,150),(767,471)),((412,150),(767,150))]:
    length=math.hypot(b[0]-a[0],b[1]-a[1])
    for step in range(0,int(length),15):
        pts=[(a[0]+(b[0]-a[0])*t/length,a[1]+(b[1]-a[1])*t/length) for t in [step,min(step+7,length)]]
        line(pd,pts,P['soft'],1)
text(pd,919,171,'现有横向竹林继续向右',22)
text(pd,783,438,'横向道路直接进入林端空地',20)
text(pd,40,171,'海',24,P['soft'])
text(pd,400,584,'左端一起重排：林缘 + 岩层 + 空地 + 路缘；不以加长连接段来拼合。',20)
save(plan,'plan-draft.png')

overview=canvas(1600,1430)
overview.paste(im,(0,0))
overview.paste(plan,(0,770*S))
save(overview,'revised-overview.png')

manifest={
    'date':'2026-11-19','continued_thread':'01a1f1b6-1db8-7b72-a123-0371eca53a04',
    'reference_sha256':hashlib.sha256(REF.read_bytes()).hexdigest(),
    'status':'2D proposal for discussion; no model or Godot edits',
    'user_observation':'The bamboo forest and rocks appear to form one whole at the end of the island, weakening the cape concept.',
    'proposal':'Recompose the terminal forest land as one rocky coast; embed the camp in an opening of the same footprint.',
    'not_fixed':['dimensions','outline','rock counts','stair treads','material colors','exact route coordinates'],
    'sources':{'reference':'reference/user-forest-coast.png','hero':'assets/characters/green_three_walk/right_idle.png'},
    'outputs':['reference-reading.png','lateral-draft.png','plan-draft.png','revised-overview.png'],
    'drawing_scope':'All drawn shapes are 2D composition marks. No new meshes, source model edits, shader edits or game import.'
}
(OUT/'proposal.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(OUT),'images':manifest['outputs']},ensure_ascii=False))
