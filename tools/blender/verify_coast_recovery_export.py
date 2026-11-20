"""Keep the original whole-forest painting outside the local runtime overlay."""
import bpy,json
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/layered_island/coast_recovery';s=bpy.data.scenes['Coast_Structure_Recovery_20261120'];bpy.context.window.scene=s
base=bpy.data.scenes['Coast_Recovery_Strict_Baseline_20261120'];original=next(o for o in base.objects if o.name.split('.')[0]=='WALK_Forest_Ground');g=s.objects['Recovery_WALK_Forest_Ground']
ids=[p.material_index for p in g.data.polygons];g.data.materials.clear()
for m in original.data.materials:g.data.materials.append(m)
for p,i in zip(g.data.polygons,ids):p.material_index=i
if g.data.uv_layers.get('RecoveryFloor'):g.data.uv_layers.remove(g.data.uv_layers['RecoveryFloor'])
report=json.loads((A/'assembly.json').read_text());report['revision']='coast-structure-recovery-9';report['source_floor_uv']='original forest UV preserved; local floor painting is registered by Godot integration';s['revision']=report['revision']
for o in s.objects:o.select_set(o.type=='MESH')
bpy.context.view_layer.objects.active=g
bpy.data.libraries.write(str(A/'coast_structure.blend'),{s},fake_user=True,compress=True)
bpy.ops.export_scene.gltf(filepath=str(A/'coast_structure.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_materials='EXPORT',export_vertex_color='ACTIVE',export_all_vertex_colors=True,export_cameras=False,export_lights=False)
(A/'assembly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('FOREST_PAINT_PRESERVED')
# Reimport the actual export into its own readback scene.
check=bpy.data.scenes.new('Coast_Recovery_Final_Readback_20261120');bpy.context.window.scene=check;bpy.ops.import_scene.gltf(filepath=str(A/'coast_structure.glb'))
meshes=[o for o in check.objects if o.type=='MESH'];assert len(meshes)==len([o for o in s.objects if o.type=='MESH'])
summary={'revision':s['revision'],'source_meshes':len(s.objects),'export_meshes':len(meshes),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),'materials':sorted({m.name for o in meshes for m in o.data.materials if m}),'source_stair':report['source_stair'],'static_only':True}
(R/'artifacts/coast-structure-recovery/export-readback.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8');bpy.context.window.scene=s;print(json.dumps(summary))
