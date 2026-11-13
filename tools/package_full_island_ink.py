"""Make static review boards from real Godot captures; no video generation."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
R=Path(__file__).resolve().parents[1];O=R/'artifacts/full-island-ink-review'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',26)
def compare(label,title):
    out=Image.new('RGB',(1280,1520),(29,40,40));d=ImageDraw.Draw(out)
    for j,(phase,text) in enumerate([('before','修改前'),('review','扩展后')]):
        y=j*760;d.text((20,y+5),title+' · '+text,font=font,fill=(235,234,216))
        out.paste(Image.open(O/f'{phase}-original-{label}.png').convert('RGB'),(0,y+40))
    out.save(O/f'before-after-{label}.jpg',quality=94)
compare('east-entry','东岸草地、道路与岩石')
compare('valley','西岸草地与后谷')
items=[('original-cape','岛角'),('original-west','西岸'),('original-valley','后谷'),('original-waterfall','桥前'),('original-east-entry','东岸入口'),('sunset-east-end','夕阳背景·东岸')]
board=Image.new('RGB',(1920,1740),(29,40,40));d=ImageDraw.Draw(board)
for i,(file,label) in enumerate(items):
    x=(i%2)*960;y=(i//2)*580
    d.text((x+16,y+4),label,font=font,fill=(235,234,216))
    board.paste(Image.open(O/f'review-{file}.png').resize((960,540),Image.Resampling.LANCZOS),(x,y+40))
board.save(O/'static-overview.jpg',quality=93)
print('Packaged 2 before/after boards and 6-view static overview')
