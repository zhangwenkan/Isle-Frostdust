import bpy,json
from pathlib import Path
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'assets/island_blender'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
bpy.ops.object.select_all(action='DESELECT')
stats={};tri=0
for ob in scene.objects:
 if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
 ob.hide_set(False);ob.select_set(True);ob.data.calc_loop_triangles();tri+=len(ob.data.loop_triangles)
 for c in ob.users_collection:stats[c.name]=stats.get(c.name,0)+1
 # Preserve authored animation pivots instead of baking children into the world root.
 parent=ob.parent
 while parent is not None:
  parent.hide_set(False);parent.select_set(True);parent=parent.parent
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'nameless_island.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'nameless_island.glb'),export_format='GLB',use_selection=True,use_active_scene=True,
 export_yup=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',
 export_cameras=False,export_lights=False,export_extras=True)
manifest_path=OUT/'asset_manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}
manifest.update({'authoring':'Blender 5.1 through Blender MCP','collections':stats,'triangles':tri})
manifest.setdefault('style_reference','I Just Wanted to Fish Demo / official screenshots and supplied local assets')
manifest.setdefault('source_manifests',['fish_reference/source_manifest.json','palm_study/source_manifest.json'])
manifest.setdefault('revision','Imported Blender coast')
manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Fish island export',stats,'triangles',tri)
