"""Package actual Blender renders; this script authors no 3D geometry."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];O=R/'artifacts/tripo-replica-review'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',32)
small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24)
for angle in [0,35]:
    left=Image.open(O/f'reference-gray-{angle}.png').convert('RGB')
    right=Image.open(O/f'review-replica-gray-{angle}.png').convert('RGB')
    im=Image.new('RGB',(2400,1085),(241,241,237));im.paste(left,(0,85));im.paste(right,(1200,85))
    d=ImageDraw.Draw(im);d.text((36,21),'Tripo 原件 · 灰材质',font=font,fill=(44,49,49))
    d.text((1236,21),'本轮表面重建样品 · 灰材质',font=font,fill=(44,49,49))
    d.line((1200,0,1200,1045),fill=(170,177,174),width=2)
    d.text((36,1052),'同机位、同光照。右侧依赖参考表面测量；不代表独立雕刻或工作流已完成。',font=small,fill=(68,74,74))
    im.save(O/f'review-comparison-{angle}.png')
protected=json.loads((O/'continuation-protected-files.json').read_text(encoding='utf8'))
state={f:hashlib.sha256((R/f).read_bytes()).hexdigest()==h for f,h in protected.items() if f!='AGENTS.md'}
assert all(state.values()),state
(O/'protected-game-files-final.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'comparisons':['review-comparison-0.png','review-comparison-35.png'],'protected_game_files':state},ensure_ascii=False))
