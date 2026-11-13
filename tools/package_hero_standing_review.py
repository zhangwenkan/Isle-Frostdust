"""Package unretouched rendered stills and verify source/pose invariants."""
from pathlib import Path
import json
import hashlib
import difflib
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/hero-standing-light-review'
FONT='C:/Windows/Fonts/msyh.ttc'


def crop_comparison():
    sheet=Image.new('RGB',(1040,850),'#e7eae4')
    draw=ImageDraw.Draw(sheet)
    font=ImageFont.truetype(FONT,26)
    small=ImageFont.truetype(FONT,18)
    draw.text((24,16),'同机位站姿对照：左修改前，右当前版本',font=font,fill='#233e3b')
    for col,phase in enumerate(['before','final']):
        source=Image.open(OUT/f'{phase}-front-detail.png')
        crop=source.crop((520,178,760,540)).resize((480,724),Image.Resampling.NEAREST)
        sheet.paste(crop,(24+col*512,65))
    draw.text((24,809),'实机裁图最近邻放大；未给截图补画明暗或阴影。人物原图、比例和站姿保持。',font=small,fill='#526661')
    sheet.save(OUT/'standing-before-after.png')


def four_views():
    labels=[('front-detail','正面'),('right-detail','侧面'),('up-detail','背面'),('front-overcast','阴天')]
    sheet=Image.new('RGB',(1440,1120),'#e7eae4');draw=ImageDraw.Draw(sheet)
    font=ImageFont.truetype(FONT,22)
    for idx,(name,label) in enumerate(labels):
        x=idx%2*720;y=idx//2*560
        draw.text((x+20,y+10),label+'：左修改前 / 右当前版本',font=font,fill='#233e3b')
        for col,phase in enumerate(['before','final']):
            crop=Image.open(OUT/f'{phase}-{name}.png').crop((525,180,755,535)).resize((330,509),Image.Resampling.NEAREST)
            sheet.paste(crop,(x+15+col*350,y+45))
    sheet.save(OUT/'standing-four-comparisons.png')


def verify():
    before=json.loads((OUT/'source-hashes-before.json').read_text(encoding='utf8'))
    sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in before.items()}
    old=json.loads((OUT/'before-poses.json').read_text(encoding='utf8'))
    new=json.loads((OUT/'final-poses.json').read_text(encoding='utf8'))
    entries={e['label']:e for e in new}
    poses=[]
    for a in old:
        b=entries[a['label']]
        poses.append({'label':a['label'],'same_camera':a['camera']==b['camera'],'same_root':a['hero']==b['hero'],'same_light_direction':a['sun_direction']==b['sun_direction']})
    # Check source normals are finite and approximately normalized after PNG quantization.
    normals=[]
    for direction in ['down','right','up']:
        src=ROOT/f'assets/characters/green_three_walk/{direction}_idle.png'
        normal=ROOT/f'assets/characters/standing_surface/{direction}_idle_normal.png'
        mask=np.asarray(Image.open(src))[...,3]>90
        arr=np.asarray(Image.open(normal)).astype(float)/255*2-1
        error=np.abs(np.linalg.norm(arr[mask],axis=-1)-1)
        normals.append({'direction':direction,'size':list(Image.open(normal).size),'max_length_error':float(error.max()),'finite':bool(np.isfinite(arr).all())})
    result={'source_images_unchanged':all(sources.values()),'source_images':sources,'matched_comparisons':poses,'normal_maps':normals,'video_recorded':False}
    assert result['source_images_unchanged']
    assert all(p['same_camera'] and p['same_root'] and p['same_light_direction'] for p in poses)
    assert all(n['finite'] and n['max_length_error']<.008 for n in normals)
    (OUT/'asset-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    for name in ['scripts/hero_presentation.gd','shaders/hero_volume.gdshader']:
        original=(OUT/'backup'/name).read_text(encoding='utf8').splitlines(True)
        current=(ROOT/name).read_text(encoding='utf8').splitlines(True)
        diff=''.join(difflib.unified_diff(original,current,fromfile='before/'+name,tofile='after/'+name))
        (OUT/(Path(name).name+'.diff')).write_text(diff,encoding='utf8')
    print('Verified 9 source PNGs, identical camera/root/light in 7 comparisons, and 3 normal maps.')


if __name__=='__main__':
    crop_comparison();four_views();verify()
