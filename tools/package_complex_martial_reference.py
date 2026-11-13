"""Package diagnostic original-game animation previews without changing pose."""
from pathlib import Path
import csv
import json
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0,str(Path(__file__).resolve().parent))
from review_acupoint_microsegments import anim

ROOT=Path(__file__).resolve().parents[1]/'artifacts/gulong-complex-martial-review'
RENDER=ROOT/'runtime/original-render'
OUT=ROOT/'reference-review'
NAMES={'014':'踏月留香','039':'天落金鹏','088':'孤形吊影','040':'凤舞九天','083':'摸爬滚打剑'}
FONT=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)


def main():
    assert (RENDER/'DONE.txt').exists()
    OUT.mkdir(exist_ok=True)
    stats=[]
    for folder in sorted(RENDER.glob('gl_skill*')):
        paths=sorted((folder/'side').glob('*.png'))
        frames=[Image.open(path).convert('RGB') for path in paths]
        name=NAMES[folder.name[-3:]]
        # Display-only uniform resize of the whole fixed camera frame.
        small=[im.resize((512,512),Image.Resampling.LANCZOS) for im in frames]
        anim(small,OUT/f'{folder.name}-30fps.gif',30)
        if folder.name.endswith('083'):
            anim(small,OUT/f'{folder.name}-slow-15fps.gif',15)
            other=[Image.open(path).convert('RGB').resize((512,512),Image.Resampling.LANCZOS)
                   for path in sorted((folder/'three-quarter').glob('*.png'))]
            anim(other,OUT/f'{folder.name}-three-quarter.gif',30)
        board=Image.new('RGB',(1280,1120),(24,29,37));draw=ImageDraw.Draw(board)
        for j in range(20):
            k=round(j*(len(frames)-1)/19);x=j%5*256;y=j//5*280
            board.paste(frames[k].resize((256,256),Image.Resampling.LANCZOS),(x,y+24))
            draw.text((x+4,y+2),f'{name} F{k:03d} {k/30:.2f}s',font=FONT,fill='white')
        board.save(OUT/f'{folder.name}-sheet.jpg')
        rows=list(csv.DictReader((folder/'bones.csv').open(encoding='utf-8-sig')))
        stats.append(dict(id=folder.name,name=name,frames=len(frames),fps=30,
            head_below_hips_frames=[int(r['frame']) for r in rows if float(r['Head_y'])<float(r['Hips_y'])],
            head_y_range=[min(float(r['Head_y']) for r in rows),max(float(r['Head_y']) for r in rows)]))
    (OUT/'measurements.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf8')
    print('Packaged 5 diagnostic motions')


if __name__=='__main__':main()
