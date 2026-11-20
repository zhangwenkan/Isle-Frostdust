"""Compose annotated 2D evidence; no geometry or game assets are authored."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/tripo-rock-stair-analysis'
FONT='C:/Windows/Fonts/msyh.ttc'
title=ImageFont.truetype(FONT,26);small=ImageFont.truetype(FONT,19);number=ImageFont.truetype(FONT,18)
bg=(29,34,36);fg=(231,232,225);accent=(239,188,101)

def panel(path,crop,label,size,marks=None):
    p=Image.new('RGB',size,bg);im=Image.open(path).convert('RGB')
    if crop:im=im.crop(crop)
    fit=ImageOps.contain(im,(size[0]-16,size[1]-55),Image.Resampling.LANCZOS)
    x=(size[0]-fit.width)//2;y=52+(size[1]-55-fit.height)//2
    p.paste(fit,(x,y));d=ImageDraw.Draw(p);d.text((16,12),label,font=title,fill=fg)
    if marks:
        scale=fit.width/im.width
        for n,point in marks.items():
            px=x+(point[0]-crop[0])*scale;py=y+(point[1]-crop[1])*scale
            d.ellipse((px-14,py-14,px+14,py+14),fill=bg,outline=accent,width=2)
            d.text((px,py-1),str(n),anchor='mm',font=number,fill=accent)
    return p

c=Image.new('RGB',(1800,545),bg)
data=[(ROOT/'artifacts/forest-rocky-terminus-study/reference/user-forest-coast.png',(280,260,1010,690),'用户参考 · 局部', {1:(468,482),2:(445,601),3:(591,521)}),
      (OUT/'tripo-native-0.png',(130,150,890,665),'Tripo · 独立模型',{1:(365,410),2:(397,557),3:(486,504)}),
      (ROOT/'artifacts/strict-forest-coast-review/review-stairs.png',(475,276,970,625),'当前实机 · 局部',{1:(560,390),2:(566,470),3:(657,458)})]
for i,(path,crop,label,marks) in enumerate(data):c.paste(panel(path,crop,label,(600,465),marks),(600*i,0))
d=ImageDraw.Draw(c);d.text((20,476),'标号：1 主岩   2 崖脚岩块   3 下行台阶。比较形体与嵌合关系。',font=small,fill=fg)
d.text((20,507),'这组图光照、机位不同，局部裁切只方便观看；不能据此测量真实米数或归因于贴图。',font=small,fill=(179,190,192))
c.save(OUT/'reference-tripo-current.png')

for angle in [0,35]:
    c=Image.new('RGB',(1600,755),bg)
    for i,key in enumerate(['tripo','current']):
        label='Tripo · 灰模' if key=='tripo' else '当前 · 灰模（局部裁切）'
        c.paste(panel(OUT/(key+'-matched-clay-'+str(angle)+'.png'),None,label,(800,690)),(800*i,0))
    d=ImageDraw.Draw(c);d.text((20,699),'相同材质、光照与相机；按组合总高度等比归一，保留内部比例。',font=small,fill=fg)
    d.text((20,729),'当前组合地表/基础为诊断副本裁切，后侧直切边仅是取景边界。项目模型未修改。',font=small,fill=(179,190,192))
    c.save(OUT/('matched-clay-comparison-'+str(angle)+'.png'))
print('Saved reference/Tripo/current and two matched clay comparisons.')
