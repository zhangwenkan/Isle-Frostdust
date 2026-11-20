"""Blender MCP: assemble expanded rock coast, supported stairs and sand contact."""
import bpy,bmesh,json,math,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/rock-cape-weight-review';A=R/'assets/layered_island/tripo_replica'
SN='Rock_Cape_Weight_Game_20261119';assert not bpy.data.scenes.get(SN),'Inspect existing weight assembly.'
status=json.loads((O/'weight-bake-status.json').read_text());assert status['status']=='complete'
base=bpy.data.scenes['Tripo_Game_Assembly_20261119'];delivery=bpy.data.scenes['Rock_Cape_Weight_Delivery_20261119']
s=bpy.data.scenes.new(SN);bpy.context.window.scene=s
fit=json.loads((A/'game_assembly.json').read_text());author=json.loads((O/'author.json').read_text());P=Matrix(fit['placement_matrix'])
for old in base.objects:
    if old.name in ['WALK_Tripo_Rock_Surface','WALK_Tripo_Stairs']:continue
    cp=old.copy();cp.data=old.data.copy();cp.name=old.name+'_Weight';s.collection.objects.link(cp)
    cp['game_name']=old.get('game_name',old.name)
for oldname,newname in [('Weight_Delivery_Rocks','WALK_Tripo_Rock_Surface'),('Weight_Delivery_Stairs','WALK_Tripo_Stairs')]:
    src=delivery.objects[oldname];cp=src.copy();cp.data=src.data.copy();cp.name=newname+'_Weight';cp['game_name']=newname;cp.matrix_world=P@src.matrix_world;s.collection.objects.link(cp)
# Support exists as a continuous embedded wedge, leaving only the stone sides
# and selected step noses visible. It reaches below the beach at the lower end.
ys=[-.540,-.511,-.484,-.458,-.433,-.409,-.386,-.363,-.341,-.319,-.298,-.278,-.258,-.239,-.220,-.202,-.184]
zs=[.082,.096,.112,.128,.145,.161,.179,.197,.216,.234,.253,.272,.291,.309,.327,.343,.343]
verts=[];faces=[]
for i,(y,z) in enumerate(zip(ys,zs)):
    c=-.070+(y+.449)*.287;w=.087 if i<3 else .073
    verts.extend([(c-w,y,z-.010),(c+w,y,z-.010),(c-w,y,.054),(c+w,y,.054)])
for i in range(len(ys)-1):
    a=i*4;b=a+4;faces.extend([(a,b,b+1,a+1),(a+2,b+2,b,a),(a+1,b+1,b+3,a+3),(a+3,b+3,b+2,a+2)])
faces.extend([(0,1,3,2),(len(verts)-4,len(verts)-2,len(verts)-1,len(verts)-3)])
me=bpy.data.meshes.new('Embedded_Stone_Stair_Core');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
ob=bpy.data.objects.new('Rock_Stair_Embedded_Core_Weight',me);s.collection.objects.link(ob);ob.matrix_world=P;ob['game_name']='Rock_Stair_Embedded_Core'
m=bpy.data.materials.new('Weight_Embedded_Core_Stone');m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.162,.172,.145,1);bs.inputs['Roughness'].default_value=.95;me.materials.append(m)
# A local sand copy lets the bottom two steps sink into a low natural contact
# rather than stand as a thin, detached edge on a flat plane. No global beach remesh.
with bpy.data.libraries.load(str(R/'assets/layered_island/layered_island.blend'),link=False) as (available,loaded):loaded.objects=['WALK_Cape_Sand']
sand=loaded.objects[0];sand.name='GameJoin_WALK_Cape_Sand_Weight';sand['game_name']='GameJoin_WALK_Cape_Sand';s.collection.objects.link(sand)
start=P@Vector((-.070+(-.535+.449)*.287,-.535,.082));end=P@Vector((-.070+(-.184+.449)*.287,-.184,.343));axis=(Vector((end.x,end.y))-Vector((start.x,start.y))).normalized();side=Vector((axis.y,-axis.x));changed=0
for v in sand.data.vertices:
    p=v.co;d=Vector((p.x-start.x,p.y-start.y));a=d.dot(axis);b=abs(d.dot(side))
    if -.85<a<1.15 and b<2.15 and p.z>-.15:
        wa=math.exp(-((a-.20)/.66)**2);wb=math.exp(-(b/1.65)**4)
        # Higher on the sides, low across the walk centre to keep the first tread.
        rise=(.055+.080*min(1,b/1.25))*wa*wb
        v.co.z+=rise;changed+=1
sand.data.update()
fit['sample_anchors']=author['sample_anchors']
fit['copied_clips'].append({'name':'GameJoin_WALK_Cape_Sand','original':'WALK_Cape_Sand','method':'local low sand shoulder around bottom two steps','changed_vertices':changed})
fit['revision']='rock-cape-weight-game-1';s['revision']=fit['revision']
# Canonical game names are exported using a reversible rename, leaving other
# Blender review scenes intact while allowing stable Godot material routing.
changes=[]
for ob in s.objects:
    target=ob.get('game_name',ob.name.removesuffix('_Weight'))
    conflict=bpy.data.objects.get(target)
    if conflict and conflict!=ob:changes.append((conflict,conflict.name));conflict.name=target+'_Prior_Weight_Archive'
    ob.name=target
for ob in s.objects:ob.select_set(ob.type=='MESH')
bpy.context.view_layer.objects.active=s.objects['WALK_Tripo_Rock_Surface']
bpy.data.libraries.write(str(A/'tripo_game_assembly.blend'),{s},fake_user=True,compress=True)
bpy.ops.export_scene.gltf(filepath=str(A/'tripo_game_assembly.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
(A/'game_assembly.json').write_text(json.dumps(fit,indent=2),encoding='utf8')
report={'scene':SN,'revision':s['revision'],'objects':[ob.name for ob in s.objects],'sand_vertices_adjusted':changed,'sample_anchors':fit['sample_anchors'],'bounds':author['bounds_after'],'old_shoulders_restored':False}
(O/'assembly.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
