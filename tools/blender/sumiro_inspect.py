import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
OUT=ROOT/'artifacts/sumiro-style-review'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
col=bpy.data.collections.get('90_Sumiro_Source') or bpy.data.collections.new('90_Sumiro_Source')
if col.name not in scene.collection.children:scene.collection.children.link(col)
report=[]
for asset in ['env_cliff/wall','env_cliff/path','env_cliff/lobes','env_cliff/rocks','env_pines/pines','backdrop/hills']:
    prefix='SRC_'+asset.replace('/','_')+'__'
    if not any(o.name.startswith(prefix) for o in col.objects):
        before=set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(OUT/'source/assets'/f'{asset}.glb'))
        for ob in set(bpy.data.objects)-before:
            ob.name=prefix+ob.name
            for c in list(ob.users_collection):c.objects.unlink(ob)
            col.objects.link(ob);ob.hide_render=True;ob.hide_set(True)
    for ob in col.objects:
        if ob.type!='MESH' or not ob.name.startswith(prefix):continue
        pts=[ob.matrix_world@v.co for v in ob.data.vertices]
        report.append({'name':ob.name,'bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]], 'verts':len(pts),'faces':len(ob.data.polygons),'materials':[m.name for m in ob.data.materials], 'colors':[a.name for a in ob.data.color_attributes], 'uv':[a.name for a in ob.data.uv_layers]})
(OUT/'source/blender-inspection.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('SUMIRO_SOURCE_INSPECTED',len(report))
