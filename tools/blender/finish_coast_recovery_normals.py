"""Correct outward normals and broad structural folds on the continuous core."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/layered_island/coast_recovery';s=bpy.data.scenes['Coast_Structure_Recovery_20261120'];bpy.context.window.scene=s
terrain=s.objects['Recovery_WALK_Forest_Ground'];bm=bmesh.new();bm.from_mesh(terrain.data)
edges=[e for e in bm.edges if e.is_boundary and max(v.co.x for v in e.verts)<-53.99 and min(v.co.x for v in e.verts)<-54.01]
# Continuous outlines have shared vertices and staggered mid-height folds. The
# fixed upper ring still exactly matches the grass boundary; no floating cap.
points={};segments=[];normals={}
for e in edges:
 p,q=[v.co.copy() for v in e.verts];d=q-p;out=Vector((d.y,-d.x,0)).normalized()
 if out.dot((p+q)*.5-e.link_faces[0].calc_center_median())<0:out=-out
 count=max(1,int(d.length/1.5));row=[]
 for j in range(count+1):
  pt=p.lerp(q,j/count);key=tuple(round(x,5) for x in pt);points[key]=pt;normals[key]=normals.get(key,Vector())+out;row.append(key)
 for a,b in zip(row,row[1:]):segments.append((a,b,out))
verts=[];uv=[];idx={};faces=[]
for key,p in points.items():
 out=normals[key].normalized();val=.5+.5*math.sin(p.x*.83+p.y*.42)
 for k,(f,w) in enumerate([(1,0),(.76,.035),(.31,.22+val*.16),(0,.32+val*.18)]):
  co=p+out*w;co.z=-.5+(p.z+.5)*f
  if k==1:co.z+=(val-.5)*.23
  if k==2:co.z-=(val-.5)*.34
  idx[key,k]=len(verts);verts.append(tuple(co));uv.append(((co.x+72.5)/23,co.z/5))
for a,b,out in segments:
 for k in range(3):
  f=[idx[a,k],idx[b,k],idx[b,k+1],idx[a,k+1]];v=[Vector(verts[i]) for i in f]
  if (v[1]-v[0]).cross(v[2]-v[0]).dot(out)<0:f.reverse()
  faces.append(f)
bm.free();me=bpy.data.meshes.new('Recovery_Continuous_Rock_Core_Final');me.from_pydata(verts,[],faces);me.update();me.materials.append(bpy.data.materials['Recovery_Face_Stone']);u=me.uv_layers.new(name='UVMap')
for p in me.polygons:
 for li in p.loop_indices:u.data[li].uv=uv[me.loops[li].vertex_index]
core=s.objects['Recovery_Cape_Terminus_Bedrock'];core.data=me
report=json.loads((A/'assembly.json').read_text());report['revision']='coast-structure-recovery-7';report['core_normals']='all quads face outward from their shared terrain border';s['revision']=report['revision']
for o in s.objects:o.select_set(o.type=='MESH')
bpy.context.view_layer.objects.active=core
bpy.data.libraries.write(str(A/'coast_structure.blend'),{s},fake_user=True,compress=True)
bpy.ops.export_scene.gltf(filepath=str(A/'coast_structure.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_materials='EXPORT',export_vertex_color='ACTIVE',export_all_vertex_colors=True,export_cameras=False,export_lights=False)
(A/'assembly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('OUTWARD_CORE_NORMALS',len(faces))
