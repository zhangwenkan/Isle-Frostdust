"""Seal terrain from its actual boundary and finish embedded rock volumes, MCP."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/layered_island/coast_recovery';s=bpy.data.scenes['Coast_Structure_Recovery_20261120'];bpy.context.window.scene=s
old=s.objects['Recovery_Cape_Terminus_Bedrock'];old.name='Rejected_Recovery_Offset_Bedrock';s.collection.objects.unlink(old);old.hide_render=True
terrain=s.objects['Recovery_WALK_Forest_Ground'];bm=bmesh.new();bm.from_mesh(terrain.data)
edges=[e for e in bm.edges if e.is_boundary and max(v.co.x for v in e.verts)<-53.99 and min(v.co.x for v in e.verts)<-54.01]
# Reuse the exact top boundary. The seam cannot leave a strip of sea between
# grass and rock. Lower tiers have broad outward footing submerged in sand.
verts=[];faces=[];uv=[]
for e in edges:
 p,q=[v.co.copy() for v in e.verts];edge=q-p;out=Vector((edge.y,-edge.x,0)).normalized()
 mid=(p+q)*.5
 # Choose outward relative to the adjacent terrain face.
 fc=e.link_faces[0].calc_center_median()
 if out.dot(mid-fc)<0:out=-out
 start=len(verts)
 for fraction,spread in [(1,0),(.70,.10),(.30,.20),(0,.14)]:
  for v in [p,q]:
   co=v+out*spread;co.z=-.42+(v.z+.42)*fraction;verts.append(tuple(co));uv.append((v.x*.12,1-fraction))
 for k in range(3):j=start+k*2;faces.append((j,j+1,j+3,j+2))
bm.free();me=bpy.data.meshes.new('Recovery_Continuous_Edge_Core');me.from_pydata(verts,[],faces);me.update();me.materials.append(bpy.data.materials['Recovery_Face_Stone'])
ob=bpy.data.objects.new('Recovery_Cape_Terminus_Bedrock',me);s.collection.objects.link(ob);ob['game_name']='Cape_Terminus_Bedrock'
uvlayer=me.uv_layers.new(name='UVMap')
for f in me.polygons:
 for li in f.loop_indices:uvlayer.data[li].uv=uv[me.loops[li].vertex_index]
# Remove non-rock props from each measured crop, using closest source face
# material labels before retaining only its sculpted rock portion.
src=bpy.data.scenes['Tripo_Grit_Textured_Delivery_20261119'].objects['Grit_Delivery_Rocks']
from mathutils.bvhtree import BVHTree
tree=BVHTree.FromPolygons([v.co for v in src.data.vertices],[list(f.vertices) for f in src.data.polygons])
for name in ['West','StairRight']:
 o=s.objects['Recovery_Cape_Inset_'+name];bm=bmesh.new();bm.from_mesh(o.data)
 cut=[]
 for f in bm.faces:
  hit=tree.find_nearest(f.calc_center_median())
  if hit[2] is not None and src.data.polygons[hit[2]].material_index!=0:cut.append(f)
 bmesh.ops.delete(bm,geom=cut,context='FACES')
 # Fill thin open seams; retain the modeled outer relief.
 boundary=[e for e in bm.edges if e.is_boundary]
 if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 if name=='StairRight':o.location.x-=.20;o.location.y+=.22;o.location.z-=.14
 else:o.location.y+=.13
# Ensure the core and rock use neighbouring values rather than a two-tone wall.
m=bpy.data.materials['Recovery_Face_Stone'];m.diffuse_color=(.245,.26,.22,1);m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=m.diffuse_color
report=json.loads((A/'assembly.json').read_text());report['revision']='continuous-boundary-sealed-stair-local-rocks-4';report['edge_core_segments']=len(edges);s['revision']=report['revision']
for o in s.objects:o.select_set(o.type=='MESH')
bpy.context.view_layer.objects.active=ob
bpy.data.libraries.write(str(A/'coast_structure.blend'),{s},fake_user=True,compress=True)
bpy.ops.export_scene.gltf(filepath=str(A/'coast_structure.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_materials='EXPORT',export_vertex_color='ACTIVE',export_all_vertex_colors=True,export_cameras=False,export_lights=False)
(A/'assembly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('SEALED_BOUNDARY',len(edges))
