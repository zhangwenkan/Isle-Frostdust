import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/west-cape-extension-review'
s=bpy.data.scenes['Island_Refined']
o=s.objects['Fish_West_Continuous_Land'];b=bpy.data.objects['WestExtensionBaseline_'+o.name]
o.data.calc_loop_triangles();b.data.calc_loop_triangles()
flips=0;collapsed=0
for t,old in zip(o.data.loop_triangles,b.data.loop_triangles):
 p=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
 q=[b.matrix_world@b.data.vertices[i].co for i in old.vertices]
 area=(p[1]-p[0]).cross(p[2]-p[0]);oldarea=(q[1]-q[0]).cross(q[2]-q[0])
 if area.length<1e-9 and oldarea.length>=1e-9:collapsed+=1
 if t.material_index==0 and area.z*oldarea.z<0:flips+=1
uv_unchanged=all(len(u.data)==len(v.data) and all((a.uv-b.uv).length<1e-7 for a,b in zip(u.data,v.data)) for u,v in zip(o.data.uv_layers,b.data.uv_layers))
fern=[]
for name in ['Cliff_Fern_West_00','Cliff_Fern_West_01']:
 a=s.objects[name];base=bpy.data.objects['WestExtensionBaseline_'+name]
 shift=(a.matrix_world@a.data.vertices[0].co)-(base.matrix_world@base.data.vertices[0].co)
 residual=max(((a.matrix_world@v.co)-(base.matrix_world@q.co)-shift).length for v,q in zip(a.data.vertices,base.data.vertices))
 fern.append({'name':name,'rigid_translation_error':residual})
assert flips==0 and collapsed==0 and uv_unchanged
assert all(a['rigid_translation_error']<1e-5 for a in fern)
report={'terrain_inverted_top_triangles':flips,'new_collapsed_triangles':collapsed,'terrain_uv_unchanged':uv_unchanged,'ferns':fern}
(O/'mesh-verification.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('WEST_CAPE_MESH_AUDIT',json.dumps(report))
