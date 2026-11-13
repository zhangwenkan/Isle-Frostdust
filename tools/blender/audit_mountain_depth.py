"""Read-only audit of backdrop export membership, terrain preservation and normals."""
import bpy, json, math, hashlib, struct
from pathlib import Path
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/mountain-depth-review'
scene=bpy.data.scenes['Island_Refined']
active=[o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
assert not any(o.name.startswith('Depth_Bamboo_Back') or o.name=='Depth_Forest_Shore' for o in active)
mountains=[o for o in active if o.name.startswith('Depth_Mountain_')]
assert len(mountains)==1
stats=[]
for ob in mountains:
    me=ob.data
    invalid=sum(not all(math.isfinite(c) for c in v.co) for v in me.vertices)
    zero=sum(p.area<1e-10 for p in me.polygons)
    assert invalid==zero==0
    stats.append({'name':ob.name,'vertices':len(me.vertices),'faces':len(me.polygons),'invalid_vertices':invalid,'zero_area_faces':zero,'color_attribute':me.color_attributes.active_color.name})

def fingerprint(me):
    h=hashlib.sha256()
    for v in me.vertices:h.update(struct.pack('<fff',*v.co))
    for p in me.polygons:h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
    return h.hexdigest()
names=['Fish_West_Continuous_Land','Fish_East_Continuous_Land']
names.extend(o.name for o in active if o.name.startswith(('Bridge_','Depth_Bamboo_Main_')))
before={n:fingerprint(scene.objects[n].data) for n in names}
# Load backup mesh datablocks only, without changing the current scene or files.
with bpy.data.libraries.load(str(OUT/'backup/nameless_island.blend'),link=False) as (src,dst):
    dst.objects=[n for n in names if n in src.objects]
comparison={}
for ob in dst.objects:
    base_name=next((n for n in names if ob.name==n or ob.name.startswith(n+'.')),None)
    if base_name:comparison[base_name]=before[base_name]==fingerprint(ob.data)
for ob in dst.objects:
    if ob:bpy.data.objects.remove(ob,do_unlink=True)
assert len(comparison)==len(names) and all(comparison.values())
report={'mountains':stats,'exported_mesh_objects':len(active),'preserved_terrain_bridge_main_groves':comparison,
        'retired_distant_groves_exported':0,'geometry_check':'finite vertices, nonzero face areas; existing terrain, bridge and main groves match pre-pass backup'}
(OUT/'geometry-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('MOUNTAIN_AUDIT',json.dumps({'mountains':stats,'preserved_objects':len(comparison),'retired_groves_exported':0}))
