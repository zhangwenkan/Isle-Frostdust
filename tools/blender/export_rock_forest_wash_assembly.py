"""Apply the baked material to the fitted assembly and save/export via MCP."""
import bpy,json,numpy as np,hashlib
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/layered_island/tripo_replica';O=R/'artifacts/rock-forest-style-review'
s=bpy.data.scenes['Tripo_Game_Assembly_20261119'];bpy.context.window.scene=s
source=bpy.data.scenes['Rock_Forest_Wash_Delivery_20261119'];report=[]
def fp(me):
    result={}
    for name,seq,attr,size,dtype in [('vertices',me.vertices,'co',3,'float32'),('loops',me.loops,'vertex_index',1,'int32'),('uv',me.uv_layers.active.data,'uv',2,'float32')]:
        ar=np.empty(len(seq)*size,dtype=dtype);seq.foreach_get(attr,ar);result[name]=hashlib.sha256(ar.tobytes()).hexdigest()
    return result
for target,old in [('WALK_Tripo_Rock_Surface','Wash_Delivery_Rocks'),('WALK_Tripo_Stairs','Wash_Delivery_Stairs')]:
    ob=s.objects[target];before=fp(ob.data);ids=np.empty(len(ob.data.polygons),np.int32);ob.data.polygons.foreach_get('material_index',ids)
    ob.data.materials.clear()
    for m in source.objects[old].data.materials:ob.data.materials.append(m)
    ob.data.polygons.foreach_set('material_index',ids)
    assert before==fp(ob.data)
    report.append({'name':target,'geometry_uv_unchanged':True,'hashes':before,'faces':np.bincount(ids,minlength=4).tolist()})
# The support source material also remains meaningful in the editable Blender file.
m=s.objects['Forest_Bank_Continuous_Core'].data.materials[0];n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF')
im=bpy.data.images.load(str(A/'textures_wash/forest_bank_wash.png'),check_existing=True);im.pack();tex=next((q for q in n if q.type=='TEX_IMAGE'),None) or n.new('ShaderNodeTexImage');tex.image=im;l.new(tex.outputs['Color'],bs.inputs['Base Color'])
for ob in s.objects:ob.select_set(ob.type=='MESH')
bpy.context.view_layer.objects.active=s.objects['WALK_Tripo_Rock_Surface'];s['revision']='colored-wash-forest-bank-static-review-3'
bpy.data.libraries.write(str(A/'tripo_game_assembly.blend'),{s},fake_user=True,compress=True)
bpy.ops.export_scene.gltf(filepath=str(A/'tripo_game_assembly.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
(O/'assembly-export.json').write_text(json.dumps({'scene':s.name,'revision':s['revision'],'meshes':report,'objects':[o.name for o in s.objects if o.type=='MESH']},indent=2),encoding='utf8')
print('Colored wash assembly exported; measured geometry and UV preserved.')
