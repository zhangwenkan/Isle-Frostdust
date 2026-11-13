"""Blender MCP: finish fish joints and root-weighted underwater blades."""
import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
def G(p):return Vector((p[0],-p[2],p[1]))
for i,scale in enumerate([.70,.54,.62,.48]):
    root=scene.objects['Fish_Underwater_Swimmer_%02d'%i]
    tail=scene.objects[root.name+'_Tail']
    if not tail.get('joint_refined'):
        pivot=G((.20*scale,0,0))
        for v in tail.data.vertices:v.co=v.co*scale-pivot
        tail.location=pivot;tail['joint_refined']=True
        verts=[(-.1,.035,0),(.08,.05,0),(.04,.16,0),(-.01,.055,-.08),(.08,.025,-.03),(.06,.02,-.19),(-.01,.055,.08),(.08,.025,.03),(.06,.02,.19)]
        me=bpy.data.meshes.new(root.name+'_Fins');me.from_pydata([G(p)*scale for p in verts],[],[(0,1,2),(3,4,5),(6,8,7)]);me.materials.append(bpy.data.materials['Fish_Underwater_Belly']);me.update()
        fins=bpy.data.objects.new(root.name+'_Fins',me);bpy.data.collections['24_Underwater_Life'].objects.link(fins);fins.parent=root
for ob in scene.objects:
    if not ob.name.startswith('Fish_Underwater_Kelp'):continue
    if not ob.data.uv_layers:ob.data.uv_layers.new(name='SurfaceUV')
    uv=ob.data.uv_layers.get('WaterWeight') or ob.data.uv_layers.new(name='WaterWeight')
    low=min(v.co.z for v in ob.data.vertices);high=max(v.co.z for v in ob.data.vertices)
    for loop in ob.data.loops:uv.data[loop.index].uv=((ob.data.vertices[loop.vertex_index].co.z-low)/(high-low),.5)
manifest=json.loads((ROOT/'assets/island_blender/asset_manifest.json').read_text())
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
p=ROOT/'assets/island_blender/asset_manifest.json';new=json.loads(p.read_text());new['revision']=manifest['revision'];new['source_manifests']=manifest['source_manifests'];p.write_text(json.dumps(new,indent=2),encoding='utf-8')
print('Fish joint hierarchy preserved; 3 underwater plants root weighted')
