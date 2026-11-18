"""Compose genuine runtime captures; does not alter game assets."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/forest-wind-mist-review'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21)
def board(rows,dest,width=960):
    result=Image.new('RGB',(width,rows[0][0].height*width//rows[0][0].width*len(rows)+34*len(rows)),'#222922')
    y=0;draw=ImageDraw.Draw(result)
    for im,label in rows:
        height=im.height*width//im.width;im=im.resize((width,height),Image.Resampling.LANCZOS)
        draw.text((12,y+3),label,font=font,fill='white');result.paste(im,(0,y+34));y+=height+34
    result.save(OUT/dest,quality=94)
board([(Image.open(ROOT/'artifacts/forest-layer-role-review/final-middle.jpg'),'本轮前：后林主要只有虚化（历史实机）'),(Image.open(OUT/'final-middle-current.jpg'),'本轮：独立林影、暗冠层与局部薄雾')],'before-after.jpg')
board([(Image.open(OUT/f'final-middle-{v}.jpg'),label) for v,label in [('raw_layers','同机位：绘景本身（关闭雾与景深）'),('no_mist','同机位：仅关闭局部雾片'),('current','同机位：完整效果')]],'layer-diagnosis.jpg')
times=[0,3,6,9,11,13,16,19]
rows=[]
for t in times:
    rows.append((Image.open(OUT/f'retry-motion-frames/frame-{t*12:04d}.jpg'),f'{t:02d} 秒　'+('固定镜头停留' if t<12 else '移动／停留／回头')))
tile_w,tile_h=480,294
result=Image.new('RGB',(tile_w*2,tile_h*4),'#222922');draw=ImageDraw.Draw(result)
for i,(im,label) in enumerate(rows):
    x=(i%2)*tile_w;y=(i//2)*tile_h
    result.paste(im.resize((480,270),Image.Resampling.LANCZOS),(x,y+24));draw.text((x+8,y),label,font=font,fill='white')
result.save(OUT/'motion-contact.jpg',quality=94)
