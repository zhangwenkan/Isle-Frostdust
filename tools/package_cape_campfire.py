from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/cape-campfire-review'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24)
comparison=Image.new('RGB',(1280,1512),'#17282b');draw=ImageDraw.Draw(comparison)
for row,(name,label) in enumerate([('before-lying.png','此前：岛角露岩'),('final-original-rise-000.png','当前：睡姿侧前方的熄灭篝火')]):
    draw.text((20,row*756+5),label,font=font,fill='#e8e4d5')
    comparison.paste(Image.open(OUT/name),(0,row*756+36))
comparison.save(OUT/'before-after-lying.jpg',quality=94)
for name in ['import-errors.log','final-errors.log','opening/capture-errors.log']:
    assert not (OUT/name).read_text(encoding='utf-8').strip(),name
author=json.loads((OUT/'blender-authoring.json').read_text(encoding='utf-8'))
opening=json.loads((OUT/'opening/verification.json').read_text(encoding='utf-8'))
assert author['removed']==['InkSample_Rock_00'] and author['other_meshes_unchanged']==127
assert opening['minimum_fire_actor_rect_gap_px']>0
assert (OUT/'opening/opening-rest-dialogue-15s.mp4').stat().st_size>1000000
print('Campfire final verification passed: original rock removed; 127 existing meshes unchanged; actor/fire projections do not intersect; final logs clear.')
