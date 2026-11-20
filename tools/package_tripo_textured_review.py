"""Package verified Blender output and audit protected game files. No 3D edits."""
from pathlib import Path
import json,hashlib,struct,io
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];O=R/'artifacts/tripo-replica-review';A=R/'assets/layered_island/tripo_replica'
rb=json.loads((O/'textured-readback.json').read_text(encoding='utf8'))
assert rb['status']=='complete',rb
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',30);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
for label,ref,final in [('front','textured-reference-front.png','textured-final-front.png'),('three-quarter','textured-reference-three-quarter.png','textured-final-three-quarter.png')]:
    left=Image.open(O/ref).convert('RGB');right=Image.open(O/final).convert('RGB')
    im=Image.new('RGB',(2400,1075),(239,239,234));im.paste(left,(0,73));im.paste(right,(1200,73))
    d=ImageDraw.Draw(im);d.text((28,17),'Tripo 原件 · 原材质',font=font,fill=(45,49,48));d.text((1228,17),'本轮材质贴图版 · GLB 重新导入渲染',font=font,fill=(45,49,48))
    d.line((1200,0,1200,1033),fill=(155,161,155),width=2)
    d.text((28,1041),'同机位与光照。几何沿用参考表面重建；新色图及法线图。侧后缺体积仍在，未接入游戏。',font=small,fill=(65,70,68))
    im.save(O/f'textured-comparison-{label}.png')
sheet=Image.new('RGB',(1200,1020),(239,239,234));d=ImageDraw.Draw(sheet)
for k,(fname,title) in enumerate([('textured-final-front.png','正面'),('textured-final-three-quarter.png','斜侧'),('textured-final-left.png','左侧'),('textured-final-back.png','背侧 · 原有薄面与缺体积仍在')]):
    x=(k%2)*600;y=(k//2)*510
    sheet.paste(Image.open(O/fname).convert('RGB').resize((600,480),Image.Resampling.LANCZOS),(x,y+30))
    d.text((x+12,y+1),title,font=small,fill=(45,49,48))
sheet.save(O/'textured-four-views.png')
# Parse embedded images from the actual GLB, independently of Blender's report.
b=(A/'tripo_replica_textured.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);binstart=20+n+8
embedded=[]
for im in g['images']:
    view=g['bufferViews'][im['bufferView']];start=binstart+view.get('byteOffset',0);data=b[start:start+view['byteLength']]
    p=Image.open(io.BytesIO(data));p.load()
    embedded.append({'name':im.get('name'),'size':list(p.size),'mode':p.mode,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
assert len(g['meshes'])==2 and len(g['materials'])==5 and len(embedded)==4
protected=json.loads((O/'continuation-protected-files.json').read_text(encoding='utf8'))
checks={f:hashlib.sha256((R/f).read_bytes()).hexdigest()==sha for f,sha in protected.items() if f!='AGENTS.md'}
assert all(checks.values()),checks
report={'status':'Textured static sample completed; awaiting user evaluation, not game-ready or independent-sculpt validation.',
 'source_scene':'Tripo_Textured_Delivery_20261119','revision':'authored-textures-baked-6-material-slots-preserved',
 'source_blend':str(A/'tripo_replica_textured.blend'),'glb':str(A/'tripo_replica_textured.glb'),'authoring_blend':str(A/'tripo_material_authoring.blend'),
 'texture_files':[str(p) for p in sorted((A/'textures').glob('*.png'))],
 'mesh_count':len(g['meshes']),'material_count':len(g['materials']),'embedded_images':embedded,'protected_game_files':checks,
 'geometry_provenance':'Previous reference-dependent surface reconstruction, plus authored measured staircase; no new geometry or back repair this turn.',
 'texture_provenance':'New authored Blender materials baked to new UV. Original texture used only for discrete material-region classification, not RGB transfer.',
 'limits':['Not proof of independent rock generation without Tripo geometry.','Original side/back thin surfaces and missing volume remain.','Static camp flame only; no fire animation.','High polygon review asset; no performance optimization.','No Godot integration, passage audit, or motion testing.'],
 'verification':'UV bounds, embedded image data, material faces, isolated Blender GLB readback and four views. Source comparison uses identical camera and lighting.'}
(O/'textured-review-state.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'outputs':['textured-comparison-front.png','textured-comparison-three-quarter.png','textured-four-views.png'],'protected_game_files':checks,'embedded_image_count':len(embedded)},ensure_ascii=False))
