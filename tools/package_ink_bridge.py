"""Static before/after boards, from actual Godot renders."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];O=R/'artifacts/ink-bridge-review'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',26)
for label,title in [('original-middle','桥 · 正常游戏距离'),('detail','桥 · 关闭景深近查')]:
    out=Image.new('RGB',(1280,1520),(30,39,37));d=ImageDraw.Draw(out)
    for j,(phase,text) in enumerate([('before','修改前'),('review','调整后')]):
        y=j*760;d.text((18,y+5),title+' / '+text,font=font,fill=(232,229,208))
        out.paste(Image.open(O/f'{phase}-{label}.png').convert('RGB'),(0,y+40))
    out.save(O/f'before-after-{label}.jpg',quality=94)
views=[('original-west-entry','西桥头'),('original-middle','桥中'),('original-east-entry','东桥头'),('sunset-middle','夕阳背景')]
out=Image.new('RGB',(1920,1160),(30,39,37));d=ImageDraw.Draw(out)
for i,(file,title) in enumerate(views):
    x=i%2*960;y=i//2*580;d.text((x+16,y+4),title,font=font,fill=(232,229,208))
    out.paste(Image.open(O/f'review-{file}.png').resize((960,540),Image.Resampling.LANCZOS),(x,y+40))
out.save(O/'static-overview.jpg',quality=93)
print('Bridge static comparison boards packaged')
