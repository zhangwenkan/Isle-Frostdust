"""Undo wide-screen paint distortion in Blender via MCP; preserve walk geometry."""
import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector
root=Path('D:/自己做着玩的/孤屿霜尘'); out=root/'assets/layered_island'
scene=bpy.data.scenes['Layered_Island_20261116']
previous=bpy.context.window.scene; bpy.context.window.scene=scene
C=Vector((0,-32,24)); F=(Vector((0,4,3))-C).normalized()
R=Vector((1,0,0)); U=R.cross(F).normalized(); T=math.tan(math.radians(32)/2)
def ray(u,v):return F+R*((u/2048-.5)*2*T*4/3)+U*((.5-v/1536)*2*T)
def signature(ob):
    return hashlib.sha256(repr(([tuple(v.co) for v in ob.data.vertices],
        [[tuple(x.uv) for x in layer.data] for layer in ob.data.uv_layers])).encode()).hexdigest()
before={o.name:signature(o) for o in scene.objects if o.type=='MESH'}
restored={}
for name in ['Cave_Outer_Relief','Trees_Cave_Back','Foreground_Right_Rock',
             'Foreground_Right_Leaves','Foreground_Bottom','Mountain_Far',
             'Mountain_Middle','Mountain_Near']:
    ob=scene.objects[name]; seen=set(); uv=ob.data.uv_layers[0]
    for loop in ob.data.loops:
        i=loop.vertex_index
        if i in seen:continue
        seen.add(i); p=uv.data[loop.index].uv
        depth=(ob.data.vertices[i].co-C).dot(F)
        # Original full-canvas coordinates: no widening, lowering, or edge stretch.
        ob.data.vertices[i].co=C+ray(p.x*2048,(1-p.y)*1536)*depth
    ob.data.update();restored[name]=len(seen)
archive=bpy.data.collections.get('90_Rejected_Wide_Frame_Extensions')
if not archive:
    archive=bpy.data.collections.new('90_Rejected_Wide_Frame_Extensions');scene.collection.children.link(archive)
archived=[]
for name in ['Trees_Right_Extension','Land_Left_Extension','Bamboo_Left_Extension']:
    ob=scene.objects.get(name)
    if not ob:continue
    for col in list(ob.users_collection):col.objects.unlink(ob)
    archive.objects.link(ob);ob.hide_render=True;ob.hide_set(True);archived.append(name)
live=[o for o in scene.objects if o.type=='MESH' and o.name not in archived]
unchanged=[o.name for o in live if signature(o)==before[o.name]]
layout=json.loads((out/'layout.json').read_text(encoding='utf-8'))
layout['revision']='local-framing-original-proportions'
layout['camera']['local_zoom']=2.5
layout['camera']['canvas_bounds']=[10,45,1980,1480]
layout['objects']=[{'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons)} for o in live]
(out/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),encoding='utf-8')
report={'restored':restored,'archived':archived,'unchanged_live_meshes':unchanged,
        'walk_and_bridge_unchanged':all(o.name in unchanged for o in live if o.name.startswith(('WALK_','SUPPORT_','Bridge_')))}
(root/'artifacts/local-camera-review/blender-restoration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.data.libraries.write(str(out/'layered_island.blend'),{scene},fake_user=True,compress=True)
bpy.ops.object.select_all(action='DESELECT')
for ob in live:ob.hide_set(False);ob.select_set(True)
bpy.context.view_layer.objects.active=scene.objects['Cave_Outer_Relief']
bpy.ops.export_scene.gltf(filepath=str(out/'layered_island.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
bpy.context.window.scene=previous
print(json.dumps({'restored':list(restored),'archived':archived,'unchanged_live_mesh_count':len(unchanged),'walk_and_bridge_unchanged':report['walk_and_bridge_unchanged']}))
