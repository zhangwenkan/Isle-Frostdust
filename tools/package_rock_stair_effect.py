"""Package unretouched real game captures for this static art review."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
root=Path('D:/自己做着玩的/孤屿霜尘');r=root/'artifacts/rock-stair-composition-review'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
for shot in ['stairs','camp']:
 before=root/'artifacts/strict-forest-coast-review'/('review-'+shot+'.png');after=r/('review-'+shot+'.png')
 a=Image.open(before).convert('RGB');b=Image.open(after).convert('RGB');assert a.size==b.size==(1280,720)
 out=Image.new('RGB',(1280,1520),(26,29,30));draw=ImageDraw.Draw(out)
 draw.text((18,7),'调整前 · 同机位实机',font=font,fill=(232,234,235));out.paste(a,(0,40))
 draw.text((18,767),'本轮试作 · 同机位实机',font=font,fill=(232,234,235));out.paste(b,(0,800));out.save(r/('before-after-'+shot+'.png'))
script=root/'scripts/layered_island.gd';old=r/'before/layered_island.gd'
result={'screenshots':'Actual Godot 4.7.2 Forward+ captures; no retouching, sharpening or painting over game pixels. Label bars added outside images.','unchanged_runtime_script':hashlib.sha256(script.read_bytes()).digest()==hashlib.sha256(old.read_bytes()).digest(),'captured_revision':json.loads((r/'effect-captures.json').read_text(encoding='utf8'))['revision'],'scope':'Static art review. No passage audit or continuous walking test.'}
(r/'delivery-record.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
