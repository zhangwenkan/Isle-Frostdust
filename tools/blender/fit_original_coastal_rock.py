"""Fit original coastal rock modules through Blender MCP; archive borrowed coast and ferns."""
import bpy,bmesh,json,math,bisect,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/original-shore-review';A=R/'assets/original_coastal_rock'
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
def active():return [o for o in s.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
def sig(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 for l in o.data.uv_layers:
  for v in l.data:h.update(str(tuple(v.uv)).encode())
 h.update(str(o.matrix_world).encode());return h.hexdigest()
before={o.name:sig(o) for o in active() if not o.name.startswith('Original_Coast_')}
arc=bpy.data.collections.get('90_Before_Original_Coastal_Rock') or bpy.data.collections.new('90_Before_Original_Coastal_Rock')
if arc.name not in s.collection.children:s.collection.children.link(arc)
arc.hide_render=True;removed=[]
for ob in list(active()):
 if ob.name.startswith('WS_Reference_Shore_') or ob.name.startswith('Cliff_Fern_'):
  for c in list(ob.users_collection):c.objects.unlink(ob)
  arc.objects.link(ob);ob.hide_set(True);ob.hide_render=True;removed.append(ob.name)
land=s.objects['Fish_West_Continuous_Land'];baseline=bpy.data.objects.get('OriginalCoastBaseline_Land')
if baseline is None:
 baseline=land.copy();baseline.data=land.data.copy();baseline.name='OriginalCoastBaseline_Land';arc.objects.link(baseline);baseline.hide_render=True;baseline.hide_set(True)
land.data=baseline.data.copy()
recess=bpy.data.materials.get('Original_Coast_Recess') or bpy.data.materials.new('Original_Coast_Recess');recess.use_nodes=True
bs=recess.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.29,.25,.20,1);bs.inputs['Roughness'].default_value=1;land.data.materials[1]=recess
col=bpy.data.collections.get('36_Original_Coastal_Rock') or bpy.data.collections.new('36_Original_Coastal_Rock')
if col.name not in s.collection.children:s.collection.children.link(col)
for ob in list(col.objects):bpy.data.objects.remove(ob,do_unlink=True)
studio=bpy.data.scenes.get('Original_Shore_Studio')
if studio is None:
 with bpy.data.libraries.load(str(A/'original_coastal_rock.blend'),link=False) as (src,dst):dst.scenes=[n for n in src.scenes if n.startswith('Original_Shore_Studio')]
 studio=dst.scenes[0]
templates=sorted([o for o in studio.objects if o.type=='MESH' and o.name.startswith('Original_Shore_Module_')],key=lambda o:o.name)
assert len(templates)==5
top=[land.matrix_world@v.co for v in list(land.data.vertices)[:2626]]
topfaces=[tuple(p.vertices) for p in land.data.polygons if p.material_index==0];turftree=BVHTree.FromPolygons(top,topfaces)
boundary=[i*26 for i in range(101)]+[2600+j for j in range(1,26)]+[i*26+25 for i in range(99,-1,-1)]+list(range(24,0,-1))
perimeter=[top[i] for i in boundary];lengths=[0.]
for j in range(250):lengths.append(lengths[-1]+(perimeter[(j+1)%250]-perimeter[j]).length)
total=lengths[-1]
def at(u):
 u=u%total;j=min(249,bisect.bisect_right(lengths,u)-1);f=(u-lengths[j])/(lengths[j+1]-lengths[j]);p=perimeter[j].lerp(perimeter[(j+1)%250],f)
 tangent=(perimeter[(j+1)%250]-perimeter[(j-1)%250]).lerp(perimeter[(j+2)%250]-perimeter[j],f)
 return p,Vector((-tangent.y,tangent.x,0)).normalized()
widths=[5.2,4.1,5.7,4.6,5.0,4.2,5.9,4.8,5.1,4.3,5.6,4.7,5.8,4.5,5.3,4.9,5.0,4.4]
factor=total/sum(w*.65 for w in widths);cursor=0.;placements=[]
for i,w in enumerate(widths):
 w*=factor;center=cursor+w*.325;cursor+=w*.65
 variant=[0,2,4,1,3,2,0,4,3,1,4,0,2,3,1,0,4,2][i];mesh=templates[variant].data.copy()
 # Small changing joint lean avoids identical silhouettes; does not derive from any external mesh.
 mesh.transform(Matrix.Rotation([.02,-.06,.07,-.03,.05][i%5],4,'Z'))
 lo=Vector([min(v.co[j] for v in mesh.vertices) for j in range(3)]);hi=Vector([max(v.co[j] for v in mesh.vertices) for j in range(3)])
 height=[5.5,5.7,5.35,5.65,5.45][i%5];depth=[1.02,.97,1.08,1.0,1.05][i%5]
 for v in mesh.vertices:
  p,n=at(center+((v.co.x-lo.x)/(hi.x-lo.x)-.5)*w)
  out=(-v.co.y-.77)*depth
  q=p+n*out;q.z=p.z-.035-(hi.z-v.co.z)/(hi.z-lo.z)*height
  support=turftree.ray_cast(Vector((q.x,q.y,40)),Vector((0,0,-1)))[0]
  if support:q.z=min(q.z,support.z-.055)
  v.co=q
 # Clockwise shoreline frame mirrors local XY; make the visible faces point outward.
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 if mesh.has_custom_normals:mesh.normals_split_custom_set([(0,0,0)]*len(mesh.loops))
 mesh.update();ob=bpy.data.objects.new('Original_Coast_Rock_%02d'%i,mesh);col.objects.link(ob);ob['original_asset']=True;ob['module_variant']=variant
 placements.append(dict(name=ob.name,variant=variant,width=w,center_s=center,source_mesh='new original mineral profiles'))
preserved=[n for n in before if n not in removed and n!=land.name];assert all(sig(s.objects[n])==before[n] for n in preserved)
assert all(not o.name.startswith(('WS_Reference_Shore_','Cliff_Fern_')) for o in active())
previous=json.loads((O/'authoring.json').read_text(encoding='utf8')) if (O/'authoring.json').exists() else {}
(O/'authoring.json').write_text(json.dumps(dict(removed=sorted(set(previous.get('removed',[])+removed)),preserved_meshes=len(preserved),placements=placements,top_vertices_unchanged=2626,original_source=str(A/'original_coastal_rock.blend')),indent=2),encoding='utf8')
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
print('ORIGINAL_COAST_FITTED',len(placements),'archived',len(removed),'preserved',len(preserved))
