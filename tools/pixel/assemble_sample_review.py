from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
root=Path(__file__).resolve().parents[2]
out=root/'artifacts/hd2d-sample'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21)
small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
for name in ['sample-midshot','sample-bridgehead','sample-cliff','sample-no-lens']:
 im=Image.open(out/(name+'.png')).convert('RGB')
 im.resize((1280,720),Image.Resampling.NEAREST).save(out/(name+'-1280.png'))
board=Image.new('RGB',(1280,802),'#173237');d=ImageDraw.Draw(board)
items=[('sample-midshot','主角附近 · 最终样区'),('sample-bridgehead','桥头 · 阴影与浅水'),('sample-cliff','左端断崖 · 无路可行'),('sample-no-lens','关闭景深 · 检查资产本身')]
for i,(name,label) in enumerate(items):
 x=i%2*640;y=i//2*401
 d.text((x+15,y+8),label,font=font,fill='#e3eadb')
 board.paste(Image.open(out/(name+'.png')).convert('RGB').resize((640,360),Image.Resampling.NEAREST),(x,y+41))
board.save(out/'sample-review-board.jpg',quality=95)
before=Image.open(root/'artifacts/blender/refined-midshot-1280.png').convert('RGB')
after=Image.open(out/'sample-midshot-1280.png').convert('RGB')
comparison=Image.new('RGB',(1280,1536),'#173237');d=ImageDraw.Draw(comparison)
d.text((24,12),'上一版 · 噪声纹理与重复细碎几何',font=font,fill='#e3eadb')
comparison.paste(before,(0,48))
d.text((24,780),'本轮样区 · 像素叶簇、断裂岩岸与真实景深（同一镜头）',font=font,fill='#e3eadb')
comparison.paste(after,(0,816))
comparison.save(out/'sample-before-after.jpg',quality=95)
print('Review board and integer-scaled gameplay captures saved.')
