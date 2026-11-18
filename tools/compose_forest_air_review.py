from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1] / 'artifacts' / 'forest-air-review'
FONT = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 20)

def montage(rows, output, width=640):
    canvas = Image.new('RGB', (width*2, 390*((len(rows)+1)//2)), '#202521')
    draw = ImageDraw.Draw(canvas)
    for i, (path, label) in enumerate(rows):
        im = Image.open(ROOT / path).convert('RGB')
        im.thumbnail((width, 360), Image.Resampling.LANCZOS)
        x, y = (i % 2)*width, (i // 2)*390
        draw.text((x+10, y+3), label, font=FONT, fill='#f3efdf')
        canvas.paste(im, (x, y+30))
    canvas.save(ROOT / output, quality=90)

if len(sys.argv)==1:
    montage([
        ('diagnosis-clearing-original.jpg', 'A 原版：景深＋局部雾＋材质空气色'),
        ('diagnosis-clearing-no_far_dof.jpg', 'B 仅关远景景深（诊断用）'),
        ('diagnosis-clearing-no_volume.jpg', 'C 仅关局部体积雾'),
        ('diagnosis-clearing-no_material_air.jpg', 'D 仅关材质空气色'),
        ('diagnosis-clearing-no_volume_or_material_air.jpg', 'E 关两种雾色，保留原景深'),
    ], 'diagnosis-contact.jpg')
elif sys.argv[1] == 'review':
    rows=[]
    for view,label in [('clearing','林中空地'),('middle','横路中段'),('connection','旧竹径接头')]:
        rows.extend([(f'before-{view}-current.jpg',f'{label} · 调整前'),
                     (f'verification-{view}-current.jpg',f'{label} · 调整后，保留远景虚化')])
    montage(rows,'review-comparison.jpg')
    montage(rows[:2],'review-clearing-comparison.jpg',512)
    montage([(f'verification-{view}-current.jpg',label) for view,label in
             [('clearing','林中空地'),('middle','横路中段'),('connection','旧竹径接头'),
              ('end','新路尽头'),('beach','沙滩'),('bridge','桥上')]],'review-locations.jpg',480)
else:
    prefix=sys.argv[1]
    rows=[]
    for view, label in [('clearing','林中空地'),('middle','横路中段'),('connection','旧竹径接头')]:
        rows.extend([
            (f'diagnosis-{view}-original.jpg', f'{label} · 调整前'),
            (f'{prefix}-{view}-current.jpg', f'{label} · 调整后（景深保持）'),
        ])
    montage(rows, f'{prefix}-comparison.jpg')
