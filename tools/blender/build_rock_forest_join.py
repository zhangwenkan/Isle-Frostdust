"""Create a continuous buried bank from the actual terrain, inside Blender MCP.
The core follows retained ground; rejected independent rock shoulders stay absent.
"""
import bpy,bmesh,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/rock-forest-style-review';A=R/'assets/layered_island/tripo_replica'
s=bpy.data.scenes['Tripo_Game_Assembly_20261119'];bpy.context.window.scene=s
assert not s.objects.get('Forest_Bank_Continuous_Core'),'Inspect existing core.'
ground=s.objects['GameJoin_WALK_Forest_Ground']
bm=bmesh.new();bm.from_mesh(ground.data);bmesh.ops.transform(bm,matrix=ground.matrix_world,verts=list(bm.verts))
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001);bm.normal_update()
# Retain the upward-facing slope surface. Clip only this buried support copy.
delete=[f for f in bm.faces if f.normal.z<.48];bmesh.ops.delete(bm,geom=delete,context='FACES')
for point,normal,inner in [((-60.6,0,0),(1,0,0),True),((-53.4,0,0),(1,0,0),False),((0,1.4,0),(0,1,0),True),((0,14.55,0),(0,1,0),False)]:
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=point,plane_no=normal,clear_inner=inner,clear_outer=not inner)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.002)
boundary=[e for e in bm.edges if e.is_boundary];topverts=set(v for e in boundary for v in e.verts)
for v in bm.verts:v.co.z-=.055
# Edge orientation follows the original face, yielding outward side normals.
edgepairs=[]
for e in boundary:
    loop=next(l for l in e.link_loops);edgepairs.append((loop.vert,loop.link_loop_next.vert))
mid={};low={};depths={v:0.0 for v in bm.verts}
for v in topverts:
    p=v.co;wave=math.sin(p.x*1.63+p.y*.51)*.11+math.sin(p.y*2.14-p.x*.37)*.06
    mid[v]=bm.verts.new((p.x+.08,p.y+.06+wave,p.z*.47-.08))
    low[v]=bm.verts.new((p.x+.16,p.y+.16+wave*.45,-.70))
    depths[mid[v]]=max(.5,p.z-mid[v].co.z);depths[low[v]]=p.z+.70
for a,b in edgepairs:
    bm.faces.new((b,a,mid[a],mid[b]));bm.faces.new((mid[b],mid[a],low[a],low[b]))
# Close each lower boundary; support remains buried beneath existing walk mesh.
bottom=[e for e in bm.edges if e.is_boundary and all(v.co.z<-.69 for v in e.verts)]
if bottom:bmesh.ops.holes_fill(bm,edges=bottom,sides=0)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.verts.index_update()
me=bpy.data.meshes.new('Continuous_Forest_Bank_Core');bm.to_mesh(me);bm.free();me.update()
ob=bpy.data.objects.new('Forest_Bank_Continuous_Core',me);s.collection.objects.link(ob)
uv=me.uv_layers.new(name='BankPaint');col=me.color_attributes.new(name='BankDepth',type='FLOAT_COLOR',domain='CORNER')
for p in me.polygons:
    p.use_smooth=False
    for li in p.loop_indices:
        v=me.vertices[me.loops[li].vertex_index].co
        uv.data[li].uv=((v.x+60.6)/7.2,(v.z+.70)/5.6)
        # Alpha encodes no opacity: it is only a top-edge blend control.
        is_top=abs(p.normal.z)>.48
        col.data[li].color=(1,1,1,1 if is_top else 0)
m=bpy.data.materials.new('ForestBank_Colored_Wash');m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.12,.14,.085,1);bs.inputs['Roughness'].default_value=.96;me.materials.append(m)
ob['description']='Continuous buried terrain core, derived from retained upward slope; no former rock shoulders.'
report={'vertices':len(me.vertices),'faces':len(me.polygons),'boundary_edges_before':len(boundary),'bounds':[[min(v.co[i] for v in me.vertices) for i in range(3)],[max(v.co[i] for v in me.vertices) for i in range(3)]],'ground_untouched':True,'tripo_shapes_untouched':True}
(O/'bank-core.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
