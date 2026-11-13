import bpy,json
from pathlib import Path
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Island_Refined']
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
result={'file':bpy.data.filepath,'objects':[]}
for ob in scene.objects:
    if ob.name.startswith(('Depth_Bamboo_Main_','Depth_Bamboo_Fore_','Mist_Peak_','Seabird_')):
        result['objects'].append({'name':ob.name,'location':list(ob.location),'dimensions':list(ob.dimensions),'vertices':len(ob.data.vertices),'custom':dict(ob.items())})
(ROOT/'artifacts/living-coast-review/before-objects.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('LIVING_COAST_INSPECT',json.dumps(result))
