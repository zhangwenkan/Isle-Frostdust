"""Execute only inside Blender through MCP: inspect palm shapes and live materials."""
import bpy,json
from pathlib import Path
from mathutils import Matrix
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
REF=Path('D:/steam/steamapps/common/I Just Wanted to Fish Demo/analysis/exported_all')
original=bpy.context.scene
report={'file':bpy.data.filepath,'scene':original.name,'materials':[],'palms':[]}
for name in ['Fish_Terrain_Painted','Fish_Rock_A','Fish_Grass']:
    m=bpy.data.materials.get(name)
    report['materials'].append({'name':name,'nodes':[{'type':n.type,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None} for n in m.node_tree.nodes]})
scene=bpy.data.scenes.get('Palm_Reference_Study') or bpy.data.scenes.new('Palm_Reference_Study')
bpy.context.window.scene=scene
for ob in list(scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
for i,file in enumerate(['Palm_Bent_4201.obj','Palm_Tall_3358.obj','Palm_Short_4522.obj','Palm_Young_1034.obj','Palm_Triple_1962.obj']):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.obj_import(filepath=str(REF/'meshes'/file),forward_axis='NEGATIVE_Z',up_axis='Y',use_split_objects=False,use_split_groups=True)
    for ob in list(bpy.context.selected_objects):
        ob.data.transform(ob.matrix_world);ob.matrix_world=Matrix.Identity(4)
        lo=[min(v.co[k] for v in ob.data.vertices) for k in range(3)];hi=[max(v.co[k] for v in ob.data.vertices) for k in range(3)]
        report['palms'].append({'file':file,'part':ob.name,'bounds':[lo,hi],'verts':len(ob.data.vertices),'faces':len(ob.data.polygons),'uv':len(ob.data.uv_layers),'smooth_faces':sum(p.use_smooth for p in ob.data.polygons)})
        ob.location.x=i*12
bpy.context.window.scene=original
(ROOT/'artifacts/palm-style-review/blender-inspection.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
