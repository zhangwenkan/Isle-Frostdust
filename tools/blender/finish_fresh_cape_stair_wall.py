"""Articulate the plain backing above the new stairs; Blender MCP only."""
import bpy,bmesh,json
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Fresh_Pixel_Cape'];bpy.context.window.scene=scene
assert scene['revision']=='fresh-cape-reference-polish-5'
col=bpy.data.collections['Fresh_02_Rock_Faces']
# Upper edge stays below the existing turf. A shallow broken ledge runs into
# the stair bay, behind the walking corridor and continuous side support.
vs=[(-.55,-1.16,.25),(.55,-1.08,.25),(1.8,-1.02,.25),(3.35,-1.06,.25),
(-.55,-1.32,1.42),(.55,-1.29,1.55),(1.8,-1.18,1.37),(3.35,-1.20,1.54),
(-.55,-1.30,2.12),(.55,-1.34,2.29),(1.8,-1.22,2.15),(3.35,-1.18,2.37),
(-.55,-1.17,2.94),(.55,-1.10,2.96),(1.8,-1.01,2.94),(3.35,-1.07,2.96)]
fs=[]
for r in range(3):
    for i in range(3):fs.append((r*4+i,r*4+i+1,(r+1)*4+i+1,(r+1)*4+i))
me=bpy.data.meshes.new('Rock_Stair_Back_Fractures_mesh');me.from_pydata(vs,[],fs);me.update()
ob=bpy.data.objects.new('Rock_Stair_Back_Fractures',me);col.objects.link(ob)
me.materials.append(bpy.data.materials['Fresh_Rock_Base']);me.materials.append(bpy.data.materials['Fresh_Rock_Cool'])
for p in me.polygons:p.material_index=1 if p.index in [0,2,4] else 0
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
uv=me.uv_layers.new(name='UVMap')
for li,l in enumerate(me.loops):v=me.vertices[l.vertex_index].co;uv.data[li].uv=(v.x*.2,v.z*.2)
ob['fresh_sample']=True;ob['authored_from']='new stair wall structure'
scene['revision']='fresh-cape-reference-polish-6'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/fresh_pixel_cape/fresh_pixel_cape.blend'))
print(json.dumps({'revision':scene['revision']}))
