"""Editable pixel brushes and palette studies for the island sample. No mesh work."""
from PIL import Image, ImageDraw
from pathlib import Path
import random, math

OUT=Path(__file__).resolve().parents[2]/'assets/island_blender/pixel'
OUT.mkdir(parents=True,exist_ok=True)
PAL={
 'pine':['173d38','235347','316750','477d52','67934e','92ad60','bec67e'],
 'grass':['2c4c37','38623a','46783d','5a8b42','78a04d','a2b561'],
 'stone':['354d50','4b6262','657b77','82918a','9ba69a','bac0a5'],
 'earth':['605e43','79764f','939064','aaa374','beb383'],
 'wood':['403f32','59513a','766747','938159','b19b6b','c7b486']}
def c(p,i): return '#'+PAL[p][i]
def save(im,name):
 if name.startswith('pine_bough') or name in ['fern_spray','grass_tuft','bamboo_spray','hanging_ivy']:
  im=im.resize((im.width//2,im.height//2),Image.Resampling.NEAREST)
 im.save(OUT/(name+'.png'))

# A broad coastal pine bough: intentionally scalloped masses, lit on upper edges.
def crown(name,variant=0):
 im=Image.new('RGBA',(128,64));d=ImageDraw.Draw(im);rr=random.Random(61+variant)
 lobes=[(15,37,12,8),(30,32,17,12),(47,24,18,13),(65,20,18,12),
        (81,26,17,13),(99,32,17,10),(113,39,11,7),(80,41,20,10),
        (53,40,22,13),(31,43,16,9),(66,34,17,13)]
 for x,y,rx,ry in lobes:
  x+=variant*2 if x<60 else -variant
  outline=[]
  for k in range(24):
   a=k*math.tau/24; notch=[1,.87,1.05,.93][k%4]
   outline.append((round(x+math.cos(a)*rx*notch),round(y+math.sin(a)*ry*notch)))
  d.polygon(outline,fill=c('pine',1))
  d.polygon([(x-rx+3,y-1),(x-rx+7,y-ry+3),(x-2,y-ry),(x+rx-4,y-ry+5),(x+rx-1,y),(x+2,y+4)],fill=c('pine',2))
  d.polygon([(x-rx+6,y-4),(x-4,y-ry+1),(x+6,y-ry+2),(x+rx-4,y-4),(x+3,y-1)],fill=c('pine',3))
  for j in range(18):
   px=x+rr.randint(-rx+4,rx-4);py=y+rr.randint(-ry+3,ry-2)
   if im.getpixel((max(0,min(127,px)),max(0,min(63,py))))[3]==0:continue
   idx=rr.choice([2,3,3,4,4,5]) if py<y else rr.choice([1,2,2,3])
   # Readable 3–7 pixel needle fans instead of isolated noise pixels.
   d.line([(px-3,py-2),(px,py),(px+4,py-3)],fill=c('pine',idx),width=1)
   d.line([(px,py),(px+1,py-4)],fill=c('pine',min(idx+1,5)),width=1)
   if py<y-3:d.line([(px-2,py-3),(px+1,py-4)],fill=c('pine',5),width=1)
 # Short needles articulate the silhouette at the ends.
 for x,y,sg in [(6,38,-1),(17,31,-1),(24,47,-1),(112,34,1),(119,41,1)]:
  for j in range(3):d.line([(x,y),(x+sg*(3+j),y-2+j*2)],fill=c('pine',3+j%2))
 save(im,name)
crown('pine_bough_a');crown('pine_bough_b',1)

# Ground mosaic: connected patches, small leaf motifs, no continuous noise field.
rr=random.Random(83)
im=Image.new('RGB',(128,128),c('grass',2));d=ImageDraw.Draw(im)
for row in range(-1,9):
 for col in range(-1,9):
  x=col*18+(row%2)*8+rr.randint(-4,4);y=row*17+rr.randint(-4,4)
  idx=rr.choice([1,2,2,3,3,4]);w=rr.randint(9,20);h=rr.randint(5,10)
  d.polygon([(x,y),(x+5,y-2),(x+w-3,y-1),(x+w,y+3),(x+w-5,y+h),(x+3,y+h+1),(x-2,y+4)],fill=c('grass',idx))
  for j in range(4):
   xx=x+rr.randint(1,w);yy=y+rr.randint(0,h)
   d.line([(xx-2,yy),(xx,yy-2),(xx+2,yy)],fill=c('grass',min(5,idx+1)))
save(im,'grass_cluster')

# Rock design: large broken slate surfaces and stepped cracks with light lips.
im=Image.new('RGB',(128,128),c('stone',3));d=ImageDraw.Draw(im)
patches=[([(0,0),(51,0),(46,18),(19,22),(0,15)],4),([(57,0),(109,0),(127,17),(91,28),(55,19)],3),
 ([(0,24),(22,29),(42,21),(55,35),(46,61),(7,69),(0,47)],2),
 ([(51,23),(90,29),(97,45),(83,66),(49,61),(56,37)],4),
 ([(99,24),(127,20),(127,72),(105,67),(90,57)],2),
 ([(0,77),(33,67),(47,73),(41,102),(9,113),(0,99)],3),
 ([(52,69),(88,67),(97,91),(82,111),(47,101)],2),
 ([(98,72),(127,76),(127,120),(93,112),(101,94)],4),
 ([(0,121),(44,108),(80,117),(88,127),(0,127)],4)]
for poly,idx in patches:d.polygon(poly,fill=c('stone',idx))
cracks=[[(0,23),(19,26),(25,23),(47,20),(55,24),(57,38),(52,44),(49,63),(34,68),(6,73),(0,76)],
 [(107,0),(103,15),(94,25),(96,41),(89,53),(95,64),(93,74),(100,93),(92,110),(85,119),(86,127)],
 [(0,116),(13,112),(28,111),(42,105),(58,107),(78,113),(91,112),(110,117),(127,120)],
 [(51,63),(65,65),(78,63),(93,69),(112,69),(127,72)]]
for line in cracks:
 d.line([(x,y-2) for x,y in line],fill=c('stone',5),width=1)
 d.line(line,fill=c('stone',1),width=2)
# Small flat chips support larger forms, not stippling.
for x,y,w in [(9,10,10),(63,12,15),(71,38,9),(22,45,13),(108,50,8),(15,89,11),(57,86,9),(107,95,10),(40,120,12)]:
 d.polygon([(x,y),(x+w,y-2),(x+w-3,y+2),(x+1,y+3)],fill=c('stone',4))
 d.line([(x,y),(x+w,y-2)],fill=c('stone',5))
save(im,'stone_fracture')

# Granite surface study: mineral planes, discontinuous faults and clustered lichen.
# The old full-width cell borders made the bank read as masonry; remove those.
im=Image.new('RGB',(128,128),c('stone',3));d=ImageDraw.Draw(im)
rr=random.Random(907)
for row in range(-1,6):
 for col in range(-1,6):
  x=col*28+row*9+rr.randint(-8,6);y=row*27+rr.randint(-6,6)
  w=rr.randint(20,41);h=rr.randint(14,28);idx=rr.choice([2,3,3,4])
  d.polygon([(x,y+8),(x+w*.4,y),(x+w,y+3),(x+w-7,y+h-4),(x+4,y+h),(x-5,y+h-9)],fill=c('stone',idx))
  d.line([(x+2,y+7),(x+int(w*.4),y+1),(x+w-3,y+3)],fill=c('stone',min(5,idx+1)),width=1)
for line in [[(17,0),(17,9),(14,12),(14,25),(9,33)],[(14,25),(31,28),(39,24)],
 [(76,17),(73,26),(73,42),(65,51),(65,63),(59,70)],[(65,51),(88,49),(96,45)],
 [(111,66),(105,79),(105,91),(97,101),(96,114),(88,127)],[(23,80),(29,89),(29,103),(36,113)]]:
 d.line([(x+1,y) for x,y in line],fill=c('stone',4),width=1)
 d.line(line,fill=c('stone',1),width=1)
for j in range(120):
 x=rr.randrange(128);y=rr.randrange(128);w=rr.randint(2,6)
 idx=rr.choice([2,3,4,4,5]);d.line([(x,y),(x+w,y-1)],fill=c('stone',idx))
 if j%3==0:d.line([(x,y+1),(x+w-2,y)],fill=c('stone',idx))
for x,y in [(5,6),(51,88),(104,31),(70,114)]:
 for j in range(13):
  xx=x+rr.randrange(-9,10);yy=y+rr.randrange(-6,7)
  d.rectangle((xx,yy,xx+rr.randrange(2,5),yy+1),fill=c('grass',rr.choice([1,2,3])))
save(im,'stone_fracture')

# A separate moss atlas preserves stone variation beneath the crown.
im=Image.open(OUT/'grass_cluster.png').convert('RGB');save(im,'moss_cluster')

# Dust and small bedded stones, warm without clipped sun highlights.
im=Image.new('RGB',(128,128),c('earth',2));d=ImageDraw.Draw(im)
rr=random.Random(12)
for j in range(60):
 x=rr.randrange(128);y=rr.randrange(128);w=rr.randrange(4,15)
 d.polygon([(x,y),(x+w,y-1),(x+w-2,y+3),(x-2,y+4)],fill=c('earth',rr.choice([1,2,3])))
for x,y,w in [(11,21,8),(53,8,5),(89,28,10),(34,58,6),(109,77,7),(63,106,9),(8,93,5)]:
 d.polygon([(x,y),(x+w-2,y-2),(x+w,y+1),(x+w-3,y+4),(x,y+3)],fill=c('stone',2))
 d.line([(x,y),(x+w-2,y-2),(x+w,y)],fill=c('stone',4))
save(im,'trail_dust')

# Bark grooves form connected staggered plates.
im=Image.new('RGB',(64,128),c('wood',1));d=ImageDraw.Draw(im)
for i in range(8):
 x=i*9;offset=(i%3)*12
 for y in range(-30,130,31):
  yy=y+offset
  d.polygon([(x+1,yy),(x+6,yy-3),(x+8,yy+7),(x+6,yy+24),(x+2,yy+27),(x,yy+15)],fill=c('wood',2+i%2))
  d.line([(x+3,yy+2),(x+2,yy+15),(x+3,yy+22)],fill=c('wood',4))
  d.line([(x+6,yy+6),(x+5,yy+20)],fill=c('wood',0))
save(im,'bark_plates')
im=Image.new('RGB',(64,128),c('wood',2));d=ImageDraw.Draw(im)
for x in [3,11,20,34,44,56,61]:
 d.line([(x,0),(x+2,23),(x-1,48),(x+1,69),(x,100),(x+2,127)],fill=c('wood',1))
 d.line([(x+2,0),(x+4,23),(x+1,48),(x+3,69),(x+2,100),(x+4,127)],fill=c('wood',4))
d.ellipse((22,48,37,72),fill=c('wood',1));d.ellipse((25,51,35,68),fill=c('wood',3));d.ellipse((29,55,32,64),fill=c('wood',0))
save(im,'wood_grain')

# Grass silhouette and fern sprays share the same palette, transparent cutouts.
im=Image.new('RGBA',(64,48));d=ImageDraw.Draw(im)
for x,h,lean in [(5,14,-4),(11,25,-6),(19,35,-5),(26,26,2),(31,41,-3),(36,29,8),(43,34,9),(50,23,10),(56,13,6)]:
 d.polygon([(x-3,47),(x-2,47-h//2),(x+lean,47-h),(x+lean+1,47-h+5),(x+2,47-h//2),(x+4,47)],fill=c('grass',2+(x%3)))
 d.line([(x,46),(x,47-h//2),(x+lean,48-h)],fill=c('grass',4))
save(im,'grass_tuft')
im=Image.new('RGBA',(96,64));d=ImageDraw.Draw(im)
for ex,ey in [(6,24),(18,10),(34,3),(54,4),(73,14),(91,29)]:
 bx,by=48,63
 d.line([(bx,by),(ex,ey)],fill=c('grass',4),width=1)
 dx,dy=ex-bx,ey-by;length=math.hypot(dx,dy);nx,ny=-dy/length,dx/length
 for j in range(2,11):
  t=j/12;cx=bx+dx*t;cy=by+dy*t;span=9*math.sin(t*math.pi)*(.8 if ex<10 or ex>85 else 1)
  for s in [-1,1]:
   tx=cx+nx*span*s+dx*.09;ty=cy+ny*span*s+dy*.09
   d.polygon([(round(cx),round(cy+1)),(round(tx),round(ty)),(round(cx+dx*.055+nx*span*s*.6),round(cy+dy*.055+ny*span*s*.6+2))],fill=c('pine',3+j%3))
save(im,'fern_spray')

# Bamboo leaves are long pointed strokes grouped around visible branch axes.
im=Image.new('RGBA',(96,64));d=ImageDraw.Draw(im)
for ex,ey in [(3,26),(13,15),(30,8),(63,10),(86,20),(94,37)]:
 d.line([(48,61),(40,36),(ex,ey)],fill=c('pine',3))
 for j in range(2,7):
  t=j/7;xx=40+(ex-40)*t;yy=36+(ey-36)*t
  for side in [-1,1]:
   dx=side*(8+(j%3)*2);dy=7+(j%2)*3
   d.polygon([(xx,yy),(xx+dx*.6,yy+2),(xx+dx,yy+dy),(xx+dx*.35,yy+5)],fill=c('pine',2+j%3))
save(im,'bamboo_spray')

# Hanging roots, creepers and moss make the grass-to-stone transition irregular.
im=Image.new('RGBA',(64,64));d=ImageDraw.Draw(im)
for x,length in [(4,22),(13,38),(25,27),(38,59),(48,33),(59,46)]:
 pts=[(x,0),(x-2,12),(x+2,23),(x-1,length)]
 d.line(pts,fill=c('wood',1))
 for j in range(5,length,6):
  xx=x+round(math.sin(j*.2)*3)
  d.polygon([(xx,j),(xx-5,j-3),(xx-7,j+1),(xx-3,j+4),(xx,j+2)],fill=c('pine',3))
  d.polygon([(xx+1,j+2),(xx+5,j-2),(xx+7,j+1),(xx+4,j+4)],fill=c('pine',4))
save(im,'hanging_ivy')

# Inspect source pixels at integer enlargement before using them on geometry.
names=['pine_bough_a','pine_bough_b','stone_fracture','grass_cluster','trail_dust','bark_plates','wood_grain','fern_spray','grass_tuft']
board=Image.new('RGB',(768,768),'#243c3e');bd=ImageDraw.Draw(board)
for i,n in enumerate(names):
 a=Image.open(OUT/(n+'.png')).convert('RGBA');a.thumbnail((240,224),Image.Resampling.NEAREST)
 # Use integer enlargement, retaining the authored pixel shapes.
 k=min(240//a.width,224//a.height);a=a.resize((a.width*k,a.height*k),Image.Resampling.NEAREST)
 x=i%3*256+(256-a.width)//2;y=i//3*256+24
 board.paste(a,(x,y),a);bd.text((i%3*256+9,i//3*256+6),n,fill='#ded7b5')
board.save(OUT/'pixel_palette_review.png')
print('Pixel sources saved:',OUT)
