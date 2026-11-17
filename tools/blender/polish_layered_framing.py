"""Blender MCP-only correction of projection-frame occlusion."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'assets/layered_island'
scene=bpy.data.scenes['Layered_Island_20261116'];previous=bpy.context.window.scene;bpy.context.window.scene=scene
C=Vector((0,-32,24));F=(Vector((0,4,3))-C).normalized();R=Vector((1,0,0));U=R.cross(F).normalized();T=math.tan(math.radians(32)/2)
def ray(u,v):return F+R*((u/2048-.5)*2*T*4/3)+U*((.5-v/1536)*2*T)
def project(p):
    q=p-C;d=q.dot(F);return 1024+q.dot(R)/d/(T*4/3)*1024,768-q.dot(U)/d/T*768
def vertices(ob):
    seen=set();uv=ob.data.uv_layers[0]
    for loop in ob.data.loops:
        if loop.vertex_index in seen:continue
        seen.add(loop.vertex_index);q=uv.data[loop.index].uv
        yield ob.data.vertices[loop.vertex_index],q.x*2048,(1-q.y)*1536
for name in ['Foreground_Right_Rock','Foreground_Right_Leaves','Foreground_Bottom']:
    ob=scene.objects[name]
    for vert in ob.data.vertices:vert.co=C+(vert.co-C)*.72
    ob.data.update()
for name,plane_y in [('Trees_Cave_Back',14),('Trees_Right_Extension',16)]:
    ob=scene.objects[name]
    for vert,u,v in vertices(ob):
        if name.endswith('Extension'):u+=370;v+=60
        d=ray(u,v);vert.co=C+d*((plane_y-C.y)/d.y)
    ob.data.update()
outer=scene.objects['Cave_Outer_Relief']
for vert,u,v in vertices(outer):
    depth=(vert.co-C).dot(F)
    # Keep the arch and right doorpost at their original proportions. Expansion
    # is restricted to the far right rock edge, mostly behind near foliage.
    if u>1940:u+=(u-1940)*6.0
    if v>965:v+=(v-965)*2.7
    vert.co=C+ray(u,v)*depth
outer.data.update()
# Export reference geometry data for audits; the source camera has true perspective.
layout=json.loads((OUT/'layout.json').read_text(encoding='utf-8'));layout['revision']='resume-pass4'
(OUT/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.data.libraries.write(str(OUT/'layered_island.blend'),{scene},fake_user=True,compress=True)
bpy.ops.object.select_all(action='DESELECT')
for ob in scene.objects:
    if ob.type=='MESH':ob.select_set(True)
bpy.context.view_layer.objects.active=scene.objects['Land_Relief']
bpy.ops.export_scene.gltf(filepath=str(OUT/'layered_island.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
bpy.context.window.scene=previous
print('POLISH_EXPORTED')
