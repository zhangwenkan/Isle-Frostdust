"""Correct terrain/foliage depth through Blender MCP, preserving painted framing."""
import bpy, json, shutil
from pathlib import Path
from mathutils import Vector
root = Path('D:/自己做着玩的/孤屿霜尘')
out = root/'assets/layered_island'
backup = root/'artifacts/layered-island-build/before-playable-visibility'
backup.mkdir(exist_ok=True)
for name in ['layered_island.blend', 'layered_island.glb', 'layout.json']:
    if not (backup/name).exists():
        shutil.copy2(out/name, backup/name)
scene = bpy.data.scenes['Layered_Island_20261116']
previous = bpy.context.window.scene
bpy.context.window.scene = scene
camera = Vector((0,-32,24))
forward = (Vector((0,4,3))-camera).normalized()
right = Vector((1,0,0)); up = right.cross(forward).normalized()
from math import tan, radians
half = tan(radians(32)/2)
changes = {}

# These supplied clumps belong behind the ascending route. Retain their exact
# camera-space silhouette/UV and wind weights while moving the support planes.
for name, y in [('Bamboo_Back',18.0),('Bamboo_Middle_Left',14.2),('Bamboo_Middle_Deep',15.6)]:
    ob = scene.objects[name]
    for vertex in ob.data.vertices:
        ray = vertex.co-camera
        vertex.co = camera + ray*((y-camera.y)/ray.y)
    ob.data.update()
    changes[name] = len(ob.data.vertices)

def smooth(a,b,v):
    t=max(0,min(1,(v-a)/(b-a)))
    return t*t*(3-2*t)

# The painted landing was an upright relief in front of the entire hero. Push
# its local backing behind the traversable floor; the upper arch and distant
# right wall retain their existing depth. Ropes still occlude the lower body.
ob=scene.objects['Cave_Outer_Relief']; changed=0
for vertex in ob.data.vertices:
    q=vertex.co-camera; depth=q.dot(forward)
    u=1024+q.dot(right)/depth/(half*4/3)*1024
    v=768-q.dot(up)/depth/half*768
    w=smooth(1460,1510,u)*(1-smooth(1765,1810,u))*smooth(610,665,v)*(1-smooth(895,935,v))
    target=(4.1-camera.y)/q.y
    if w>0 and target>1:
        vertex.co=camera+q*(1+(target-1)*w);changed+=1
ob.data.update();changes[ob.name]=changed
layout=json.loads((out/'layout.json').read_text(encoding='utf-8'))
layout['revision']='resume-playable-visibility'
layout['objects']=[{'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons)} for o in scene.objects if o.type=='MESH']
(out/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.data.libraries.write(str(out/'layered_island.blend'),{scene},fake_user=True,compress=True)
bpy.ops.object.select_all(action='DESELECT')
for item in scene.objects:
    if item.type=='MESH':item.select_set(True)
bpy.context.view_layer.objects.active=ob
bpy.ops.export_scene.gltf(filepath=str(out/'layered_island.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
bpy.context.window.scene=previous
print(json.dumps({'changed_vertices':changes}))
