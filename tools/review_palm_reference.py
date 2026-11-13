"""Read reference evidence and preserve the pre-change project state."""
from pathlib import Path
import json, shutil, urllib.request, concurrent.futures, hashlib
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/palm-style-review'
REF=Path('D:/steam/steamapps/common/I Just Wanted to Fish Demo/analysis/exported_all')
OUT.mkdir(exist_ok=True)
backup=OUT/'backup';backup.mkdir(exist_ok=True)
for name in ['assets/island_blender/nameless_island.blend','assets/island_blender/nameless_island.glb','assets/island_blender/asset_manifest.json','scripts/island.gd','project.godot','shaders/fish_foliage.gdshader','shaders/fish_water.gdshader']:
    src=ROOT/name;dst=backup/name;dst.parent.mkdir(parents=True,exist_ok=True)
    if not dst.exists():shutil.copy2(src,dst)
for name in ['final-midshot.png','final-bridge.png','final-cliff.png','final-east.png']:
    dst=OUT/name.replace('final-','before-')
    if not dst.exists():shutil.copy2(ROOT/'artifacts/fish-style-review'/name,dst)
api='https://store.steampowered.com/api/appdetails?appids=5351000&l=english'
data=json.load(urllib.request.urlopen(api,timeout=25))['5351000']['data']
(OUT/'official-steam-reference.json').write_text(json.dumps({'page':'https://store.steampowered.com/app/5351000/','screenshots':data['screenshots']},indent=2),encoding='utf-8')
def download(item):
    dest=OUT/('reference-%02d.jpg'%item['id'])
    if not dest.exists():
        for attempt in range(3):
            try:
                with urllib.request.urlopen(item['path_thumbnail'],timeout=30) as r:payload=r.read()
                dest.write_bytes(payload)
                break
            except Exception:
                if attempt==2:raise
    return dest
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:files=list(pool.map(download,data['screenshots']))
sheet=Image.new('RGB',(1728,9//3*352),'#22272a');draw=ImageDraw.Draw(sheet)
for i,path in enumerate(files):
    im=Image.open(path).convert('RGB');im.thumbnail((576,324));x=(i%3)*576;y=(i//3)*352
    sheet.paste(im,(x,y));draw.text((x+8,y+327),path.stem,fill='white')
sheet.save(OUT/'reference-overview.jpg',quality=92)
names=['T_Palm_Albedo_399.png','T_Palm_Normal_501.png','T_Rock_A_Albedo_667.png','T_Rock_A_Normal_494.png','T_Terrain_Albedo_Demo_542.png','T_Terrain_Normal_Demo_436.png','T_TerrainIslet_Albedo_Demo_679.png','T_RockDetail_Demo_517.png','T_FloraAtlas_425.png']
sheet=Image.new('RGB',(1200,1290),'#333333');draw=ImageDraw.Draw(sheet)
for i,name in enumerate(names):
    p=REF/'textures'/name
    if not p.exists():continue
    im=Image.open(p).convert('RGB');im.thumbnail((400,400));x=i%3*400;y=i//3*430;sheet.paste(im,(x,y));draw.text((x+5,y+402),name,fill='white')
sheet.save(OUT/'reference-maps.jpg',quality=95)
print('Preserved pre-change assets and downloaded',len(files),'official reference screenshots.')
