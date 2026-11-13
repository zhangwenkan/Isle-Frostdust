"""Assemble unretouched in-engine still crops for comparison."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/hero-volume-review'
FONT=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24)
SMALL=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)

def main():
    items=[('岛角 · 高俯角','cape-stride',(735,185,955,540)),
           ('坡路 · 行走','slope-stride',(330,255,550,610)),
           ('吊桥 · 行走','bridge-stride',(450,195,670,550))]
    sheet=Image.new('RGB',(1420,790),(26,34,37))
    d=ImageDraw.Draw(sheet)
    d.text((24,16),'人物融入场景 · 静态实机对比',font=FONT,fill=(239,231,209))
    d.text((24,56),'每组左：修改前　右：本轮　｜同动作帧局部裁切、最近邻放大',font=SMALL,fill=(181,196,194))
    for i,(label,name,rect) in enumerate(items):
        x=24+i*466
        d.text((x,92),label,font=FONT,fill=(239,231,209))
        for col,phase in enumerate(['before','final']):
            im=Image.open(OUT/f'{phase}-{name}.png').convert('RGB').crop(rect)
            sheet.paste(im.resize((220,355),Image.Resampling.NEAREST),(x+col*228,136))
            d.text((x+col*228,499),'修改前' if col==0 else '本轮',font=SMALL,fill=(181,196,194))
            # Ground relationship enlarged from the same screenshot, without retouching.
            feet_rect={'cape-stride':(790,375,900,455),'slope-stride':(365,466,475,546),'bridge-stride':(500,395,610,475)}[name]
            feet=Image.open(OUT/f'{phase}-{name}.png').crop(feet_rect).resize((220,160),Image.Resampling.NEAREST)
            sheet.paste(feet,(x+col*228,536))
    d.text((24,724),'原行走像素保留；调整朝向、脚底落点、受光和投影。背景动态不作为本轮修改项。',font=SMALL,fill=(181,196,194))
    sheet.save(OUT/'comparison.png')
    print(OUT/'comparison.png')

if __name__=='__main__':main()
