"""MCP isolated export readback and source plant data comparison."""
import bpy,json,math,numpy as np,hashlib
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/rock-cape-weight-review';A=R/'assets/layered_island/tripo_replica'
SN='Rock_Cape_Weight_Final_Readback_20261120';assert not bpy.data.scenes.get(SN)
s=bpy.data.scenes.new(SN);bpy.context.window.scene=s;bpy.ops.import_scene.gltf(filepath=str(A/'tripo_game_assembly.glb'))
rows=[]
for ob in s.objects:
    if ob.type!='MESH':continue
    assert all(math.isfinite(x) for v in ob.data.vertices for x in v.co)
    mats=[]
    for m in ob.data.materials:
        if m:mats.append({'name':m.name,'images':[(n.image.name,list(n.image.size)) for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]})
    rows.append({'name':ob.name,'vertices':len(ob.data.vertices),'faces':len(ob.data.polygons),'uv_layers':[u.name for u in ob.data.uv_layers],'materials':mats})
assert len(rows)==10
assert not any('Rock_Near' in r['name'] for r in rows)
def fp(me):
    result={}
    for name,seq,prop,size,dtype in [('verts',me.vertices,'co',3,'float32'),('loops',me.loops,'vertex_index',1,'int32')]:
        vals=np.empty(len(seq)*size,dtype=dtype);seq.foreach_get(prop,vals);result[name]=hashlib.sha256(vals.tobytes()).hexdigest()
    for uv in me.uv_layers:
        vals=np.empty(len(uv.data)*2,np.float32);uv.data.foreach_get('uv',vals);result[uv.name]=hashlib.sha256(vals.tobytes()).hexdigest()
    return result
plants=[];active=bpy.data.scenes['Rock_Cape_Weight_Game_20261119'];previous=bpy.data.scenes['Tripo_Game_Assembly_20261119']
for name in ['GameJoin_Forest_Strict_Grass','GameJoin_Forest_Strict_Understory','GameJoin_Forest_Strict_Flowers']:
    old=next(o for o in previous.objects if o.name.startswith(name));new=active.objects[name]
    assert fp(old.data)==fp(new.data);plants.append({'name':name,'geometry_uv_wind_unchanged':True})
(O/'glb-readback.json').write_text(json.dumps({'scene':SN,'objects':rows,'plant_preservation':plants,'old_shoulders_absent':True},indent=2),encoding='utf8')
bpy.context.window.scene=active
print('Ten expected meshes read back; plants and wind UVs unchanged; old shoulders absent.')
