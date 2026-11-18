"""Arrange actual fixed-camera and motion captures for visual review."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/forest-light-depth-review'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21)
def rows(items,dest,width=960):
    im0=Image.open(OUT/items[0][0]);height=im0.height*width//im0.width
    board=Image.new('RGB',(width,(height+32)*len(items)),'#212820');draw=ImageDraw.Draw(board)
    for i,(file,label) in enumerate(items):
        y=i*(height+32);draw.text((10,y+2),label,font=font,fill='white')
        board.paste(Image.open(OUT/file).resize((width,height),Image.Resampling.LANCZOS),(0,y+32))
    board.save(OUT/dest,quality=94)
rows([('final-middle-no-shared-field.jpg','同机位：关闭共用透光变化与可见斜光'),('final-middle-no-rays.jpg','同机位：保留跨层受光，只关闭可见斜光'),('final-middle-t05.jpg','同机位：完整效果')],'light-diagnosis.jpg')
def tiles(items,dest):
    board=Image.new('RGB',(960,296*((len(items)+1)//2)),'#212820');draw=ImageDraw.Draw(board)
    for i,(path,label) in enumerate(items):
        x=(i%2)*480;y=(i//2)*296
        draw.text((x+8,y+1),label,font=font,fill='white')
        board.paste(Image.open(path).resize((480,270),Image.Resampling.LANCZOS),(x,y+26))
    board.save(OUT/dest,quality=94)
tiles([(OUT/f'final-clearing-t{time:02d}.jpg',f'透光时间 {time:02d} 秒　风动与雾形固定') for time in [0,5,10,15]],'fixed-light-contact.jpg')
tiles([(OUT/f'motion-frames/frame-{time*12:04d}.jpg',f'{time:02d} 秒　'+('固定镜头停留' if time<18 else '行走／停留／回头')) for time in [0,5,10,15,18,20,23,26]],'motion-contact.jpg')
report=json.loads((OUT/'motion-check.json').read_text(encoding='utf-8'))
assert not report['failures'];assert sum(report['shader_binding_counts'].values())==315
frames=list((OUT/'motion-frames').glob('*.jpg'));assert len(frames)==336
print('315 material bindings, 336 frames, no failures')
