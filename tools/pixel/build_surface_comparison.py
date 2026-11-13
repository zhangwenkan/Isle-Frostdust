"""Build truthful, matched image crops and a review board from Godot captures."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import io,json,base64

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/surface-review'
VIZ=Path('C:/Users/51440/.codex/visualizations/2026/11/06/01a1b0e1-f622-7751-ba35-c3ec4275f6aa')
VIZ.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',28)
small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
views=[('overview','主角附近','midshot',None),
       ('rock','岩面','midshot',(1210,520,1650,830)),
       ('grass','草地','midshot',(1400,910,1920,1110)),
       ('bark','树皮','midshot',(610,255,970,665)),
       ('wood','木板','bridge',(1450,835,2010,1000))]
data={}
pair_images=[]
for key,label,source,box in views:
    data[key]={'label':label}
    pair=[]
    for phase in ['before','after']:
        im=Image.open(OUT/f'{phase}-{source}.png').convert('RGB')
        if box:
            im=im.crop(box)
            im.save(OUT/f'{phase}-{key}-detail.png')
            pair.append(im)
        else:
            im=im.resize((1024,576),Image.Resampling.LANCZOS)
        # Preview encoding only. Original native 2560×1440 PNGs are retained.
        buf=io.BytesIO();im.save(buf,format='WEBP',quality=91,method=6)
        data[key][phase]='data:image/webp;base64,'+base64.b64encode(buf.getvalue()).decode()
    if box:pair_images.append((label,pair))

# PNG board: identical crops and exactly 2x nearest enlargement on both sides.
total_height=100+sum(pair[0].height*2+80 for _,pair in pair_images)
board=Image.new('RGB',(2320,total_height),'#183136');draw=ImageDraw.Draw(board)
draw.text((40,24),'调整前',font=font,fill='#eef4e9')
draw.text((1200,24),'调整后',font=font,fill='#eef4e9')
y=90
for label,pair in pair_images:
    draw.text((40,y),label+' · 同位置，等倍放大',font=small,fill='#b9cec6')
    for i,im in enumerate(pair):
        enlarged=im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST)
        board.paste(enlarged,(40+i*1160,y+42))
    y+=pair[0].height*2+80
board.save(OUT/'details-before-after.png')

# One compact scene board for sharing or opening outside the interactive view.
scene=Image.new('RGB',(2560,790),'#183136');draw=ImageDraw.Draw(scene)
for i,(phase,label) in enumerate([('before','调整前'),('after','调整后')]):
    draw.text((i*1280+24,16),label,font=font,fill='#eef4e9')
    im=Image.open(OUT/f'{phase}-midshot.png').convert('RGB').resize((1280,720),Image.Resampling.LANCZOS)
    scene.paste(im,(i*1280,64))
scene.save(OUT/'scene-before-after.png')

payload=json.dumps(data,ensure_ascii=False,separators=(',',':'))
template=(ROOT/'tools/pixel/surface_comparison_fragment.html').read_text(encoding='utf-8')
fragment=template.replace('SURFACE_IMAGE_DATA',payload)
target=VIZ/'island-surface-comparison.html'
target.write_text(fragment,encoding='utf-8')
assert target.stat().st_size < 1000000, target.stat().st_size
print('Comparison fragment',target.stat().st_size,'bytes')
print('Matched PNG boards:',OUT)
