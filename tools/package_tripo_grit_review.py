"""Package real Blender renders and check delivery containers; no 3D edits."""
from pathlib import Path
import json,hashlib,struct,io
from PIL import Image,ImageDraw,ImageFont
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'artifacts/tripo-replica-review';A=R/'assets/layered_island/tripo_replica'
report=json.loads((O/'roughness-readback.json').read_text());assert report['status']=='complete'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',29);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
for angle in ['three-quarter','front']:
    left=Image.open(O/f'textured-final-{angle}.png').convert('RGB');right=Image.open(O/f'roughness-final-{angle}.png').convert('RGB')
    im=Image.new('RGB',(2400,1060),(239,239,234));im.paste(left,(0,65));im.paste(right,(1200,65));d=ImageDraw.Draw(im)
    d.text((26,15),'上一版 · 表面偏光滑',font=font,fill=(45,49,48));d.text((1226,15),'本轮 · 分区颗粒与浅剥落起伏',font=font,fill=(45,49,48))
    d.line((1200,0,1200,1025),fill=(160,165,160),width=2);d.text((26,1029),'相同模型、UV、机位和光照。两侧均为 GLB 重新导入后的真实渲染。',font=small,fill=(60,65,60))
    im.save(O/f'roughness-before-after-{angle}.png')
# Crop actual render pixels at 1:1 so fine grain can be assessed without upscaling.
box=(245,315,800,705);cw=box[2]-box[0];ch=box[3]-box[1]
im=Image.new('RGB',(cw*2,ch+88),(239,239,234));d=ImageDraw.Draw(im)
for x,f,title in [(0,'textured-final-three-quarter.png','上一版 · 局部原像素'),(cw,'roughness-final-three-quarter.png','本轮 · 局部原像素')]:
    im.paste(Image.open(O/f).convert('RGB').crop(box),(x,48));d.text((x+14,9),title,font=small,fill=(45,49,48))
d.text((14,ch+54),'颗粒有疏密，浅起伏参与受光；旧版保留，未接入游戏。',font=small,fill=(60,65,60));im.save(O/'roughness-detail-comparison.png')
b=(A/'tripo_replica_grit.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);start=20+n+8;embedded=[]
for img in g['images']:
    v=g['bufferViews'][img['bufferView']];data=b[start+v.get('byteOffset',0):start+v.get('byteOffset',0)+v['byteLength']];p=Image.open(io.BytesIO(data));p.load();embedded.append({'name':img.get('name'),'size':list(p.size),'bytes':len(data)})
assert len(g['meshes'])==2 and len(g['materials'])==5 and len(embedded)==6
for m in g['materials']:
    assert 'normalTexture' in m and 'baseColorTexture' in m['pbrMetallicRoughness'] and 'metallicRoughnessTexture' in m['pbrMetallicRoughness']
protected=json.loads((O/'continuation-protected-files.json').read_text(encoding='utf8'))
checks={f:hashlib.sha256((R/f).read_bytes()).hexdigest()==h for f,h in protected.items() if f!='AGENTS.md'};assert all(checks.values())
yes=np.asarray(Image.open(O/'roughness-final-three-quarter.png').convert('RGB'),dtype=float)
no=np.asarray(Image.open(O/'roughness-diagnostic-without-normal.png').convert('RGB'),dtype=float)
diff=np.abs(yes[315:705,245:800]-no[315:705,245:800]);normal_check={'roi_mean_rgb_abs_delta':float(diff.mean()),'roi_fraction_above_5':float((diff.max(axis=2)>5).mean()),'interpretation':'Same static view with and without stone normal maps; image differences and visual inspection confirm baked normals affect shading. Not an art acceptance metric.'}
state={'status':'Grit material revision completed, awaiting user evaluation.','scene':'Tripo_Grit_Textured_Delivery_20261119','revision':'grit-textures-baked-3','glb':str(A/'tripo_replica_grit.glb'),'blend':str(A/'tripo_replica_grit.blend'),'editable_material':str(A/'tripo_grit_material_authoring.blend'),
 'embedded_images':embedded,'geometry_uv_unchanged':report['unchanged_geometry_uv'],'protected_game_files':checks,'normal_shading_check':normal_check,
 'scope':'Only stone material revised; existing geometry/UV and other prop materials retained. No Godot integration or gameplay testing.',
 'limitations':['Reference-dependent reconstruction remains.','Existing side/back missing volume and incomplete props remain.','No new physical displacement or silhouette changes; relief is baked normal shading.','No claim of user acceptance or independent rock workflow.']}
(O/'roughness-review-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'status':state['status'],'normal_check':normal_check,'protected_game_files':checks},ensure_ascii=False))
