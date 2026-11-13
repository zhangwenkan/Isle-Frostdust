"""Match the cape grass to the authored western ink sample in live Blender MCP.

Keep existing patch placement and rooted blades. Narrow their broad leaf bellies,
apply the sample's pigments, and author the same UV brush edges / wind weights.
The continuous terrain and all four rock meshes, normals and UVs are untouched.
"""
import bpy,json,hashlib,struct
from pathlib import Path
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/cape-colored-ink-review'
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene

def active_meshes():
    return [o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]

def digest(ob):
    me=ob.data
    data={'vertices':[list(v.co) for v in me.vertices],'polygons':[list(p.vertices) for p in me.polygons],
          'normals':[list(n.vector) for n in me.corner_normals],'uvs':[[list(d.uv) for d in u.data] for u in me.uv_layers],
          'transform':[list(row) for row in ob.matrix_world]}
    return hashlib.sha256(json.dumps(data,separators=(',',':')).encode()).hexdigest()

before={o.name:digest(o) for o in active_meshes()}
archive=bpy.data.collections.get('90_Before_Cape_Ink_Grass')
if archive is None:
    archive=bpy.data.collections.new('90_Before_Cape_Ink_Grass');scene.collection.children.link(archive)
archive.hide_render=True
palette=['586e40','687e4b','607749']
def color(hex):
    v=[int(hex[i:i+2],16)/255 for i in [0,2,4]]
    return tuple(a/12.92 if a<=.04045 else ((a+.055)/1.055)**2.4 for a in v)+(1,)
report=[]
for index in range(4):
    ob=scene.objects['Coast_Low_Grass_%02d.003'%index]
    name='CapeInkBaseline_'+ob.name
    baseline=scene.objects.get(name)
    if baseline is None:
        baseline=ob.copy();baseline.data=ob.data.copy();baseline.name=name
        archive.objects.link(baseline);baseline.hide_render=True;baseline.hide_set(True)
    me=baseline.data.copy();me.name='Cape_Ink_Grass_%02d'%index;ob.data=me
    assert len(me.vertices)%8==0
    root_error=0.
    for start in range(0,len(me.vertices),8):
        for a,b in [(0,1),(2,3),(4,5)]:
            va=me.vertices[start+a];vb=me.vertices[start+b];mid=(va.co+vb.co)*.5
            # Reuse the spatially composed leaves, with a finer lifted brush tip.
            va.co=mid+(va.co-mid)*.46;vb.co=mid+(vb.co-mid)*.46
        root_before=(baseline.data.vertices[start].co+baseline.data.vertices[start+1].co)*.5
        root_after=(me.vertices[start].co+me.vertices[start+1].co)*.5
        root_error=max(root_error,(root_after-root_before).length)
    for ca in list(me.color_attributes):me.color_attributes.remove(ca)
    ca=me.color_attributes.new(name='InkColor',type='FLOAT_COLOR',domain='POINT')
    for v in me.vertices:ca.data[v.index].color=color(palette[(v.index//24+index)%len(palette)])
    me.color_attributes.active_color=ca;me.color_attributes.render_color_index=0
    me.materials.clear();me.materials.append(bpy.data.materials['InkSample_Grass'])
    for p in me.polygons:p.material_index=0
    u=me.uv_layers.new(name='BrushUV');w=me.uv_layers.new(name='WindWeight')
    uv=[(.5,0),(.5,0),(0,.48),(1,.48),(.23,.81),(.77,.81),(.5,1),(.5,1)]
    for loop in me.loops:
        k=loop.vertex_index%8;u.data[loop.index].uv=uv[k];w.data[loop.index].uv=(uv[k][1],0)
    me.update()
    report.append({'object':ob.name,'blades':len(me.vertices)//8,'root_position_error_m':root_error,'material':'InkSample_Grass','uv_layers':[l.name for l in me.uv_layers]})
after={o.name:digest(o) for o in active_meshes()}
changed=[name for name in before if before[name]!=after[name]]
assert set(changed)=={'Coast_Low_Grass_%02d.003'%i for i in range(4)}
assert all(r['root_position_error_m']<.000001 for r in report)
report_data={'grass':report,'changed_meshes':changed,'unchanged_geometry_normals_uv_transforms':len(before)-len(changed),'rock_and_land_unchanged':all(before[n]==after[n] for n in before if n.startswith('InkSample_Rock_') or n=='Fish_West_Continuous_Land'),'before':before,'after':after}
(OUT/'blender-verification.json').write_text(json.dumps(report_data,indent=2),encoding='utf-8')
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
manifest_path=ROOT/'assets/island_blender/asset_manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['revision']='Cape vegetation matched to western colored ink sample; cape rock and terrain geometry preserved'
ref='../../artifacts/cape-colored-ink-review/README.md'
if ref not in manifest['source_manifests']:manifest['source_manifests'].append(ref)
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('CAPE_INK_GRASS_EXPORTED',len(changed),'changed meshes;',len(before)-len(changed),'unchanged; roots fixed')
