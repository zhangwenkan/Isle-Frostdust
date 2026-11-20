"""Package actual Godot screenshots, without retouching rendering."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
p=root/'artifacts/cape-stone-steps-clarity-review'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)

def compare(filename,out):
    a=Image.open(p/'before'/filename).convert('RGB');b=Image.open(p/filename).convert('RGB')
    canvas=Image.new('RGB',(1280,1500),'#202a2a');d=ImageDraw.Draw(canvas)
    canvas.paste(a,(0,35));canvas.paste(b,(0,780))
    d.text((18,4),'修改前 · 同机位',font=font,fill='#e4e9de')
    d.text((18,748),'本轮 · 场景像素化，人物独立全分辨率',font=font,fill='#e4e9de')
    canvas.save(p/out)
compare('game-stairs-detail.png','stairs-before-after.png')
compare('game-character-detail.png','scene-before-after.png')

# Fixed crop coordinates in the same camera. Both enlarged identically for review.
box=(638,244,718,394)
canvas=Image.new('RGB',(700,520),'#202a2a');d=ImageDraw.Draw(canvas)
for i,src in enumerate([p/'before/game-character-detail.png',p/'game-character-detail.png']):
    crop=Image.open(src).crop(box).resize((240,450),Image.Resampling.NEAREST)
    canvas.paste(crop,(50+i*350,55))
    d.text((50+i*350,14),'修改前' if i==0 else '人物全分辨率',font=font,fill='#e4e9de')
canvas.save(p/'hero-same-size-comparison.png')
stats={}
for name in ['character-transparent-pass.png','occlusion-buried-alpha.png','occlusion-partial-alpha.png']:
    if (p/name).exists():
        a=Image.open(p/name).getchannel('A');stats[name]={'bounds':a.getbbox(),'visible_pixels':sum(v>0 for v in a.get_flattened_data())}
(p/'hero-pass-check.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
print(stats)
frames=sorted((p/'motion').glob('*.png'))
if len(frames)==48:
    sheet=Image.new('RGB',(1280,1140),'#202a2a')
    d=ImageDraw.Draw(sheet)
    for i,j in enumerate([0,9,19,28,38,47]):
        img=Image.open(frames[j]).resize((640,360),Image.Resampling.NEAREST)
        x=(i%2)*640;y=(i//2)*380
        sheet.paste(img,(x,y+20));d.text((x+10,y),f'frame {j}',font=small,fill='white')
    sheet.save(p/'motion-contact-sheet.png')
