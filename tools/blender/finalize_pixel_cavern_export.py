"""Final placement and export details, only through Blender MCP."""
import bpy
from pathlib import Path
exec((Path('D:/自己做着玩的/孤屿霜尘/tools/blender/pixel_cavern_lib.py')).read_text(encoding='utf-8'),globals())
scene=bpy.data.scenes[SCENE];bpy.context.window.scene=scene
assert scene['revision']=='pixel-cavern-color-depth-6'

# Match the screen quad's author axes to glTF Y-up before the screen shader.
quad=scene.objects['Render_Pixel_Edges']
for v in quad.data.vertices:v.co=Vector((v.co.x,0,v.co.y))

# Attached greenery follows the ledge compression from the color/depth pass.
for ob in scene.objects:
    if ob.type!='MESH':continue
    is_front_plant=ob.name.startswith(('Plant_Edge_Shrub','Plant_Fern','Plant_Grass_Patch','Plant_Cliff_Creeper','Root_Cliff_Creeper'))
    if not is_front_plant:continue
    for v in ob.data.vertices:
        if v.co.x>5 and v.co.y<1:v.co.y=1+(v.co.y-1)*.65
scene['revision']='pixel-cavern-review-7';export_scene(scene['revision'])

# Isolated GLB round trip, preserving the editable author scene.
audit=bpy.data.scenes.new('PCC_Export_Audit');bpy.context.window.scene=audit
bpy.ops.import_scene.gltf(filepath=str(OUT/'pixel_cavern_coast.glb'))
objects=[o for o in audit.objects if o.type=='MESH']
for ob in objects:ob.data.calc_loop_triangles()
result={'revision':scene['revision'],'meshes':len(objects),'triangles':sum(len(o.data.loop_triangles) for o in objects),'missing_uv':[o.name for o in objects if not o.data.uv_layers],'foreign_default_objects':[o.name for o in audit.objects if o.name in ['Cube','Camera','Light']],'source_scene':SCENE}
(ROOT/'artifacts/pixel-cavern-coast-review/reimport-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
for ob in list(audit.objects):bpy.data.objects.remove(ob,do_unlink=True)
bpy.context.window.scene=scene;bpy.data.scenes.remove(audit)
print(json.dumps(result))
