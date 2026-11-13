"""Run only in Blender through blender-mcp. Articulated gull, wind weights and peak shoulders."""
import bpy,bmesh,math,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/living-coast-review'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
def collection(name):
 c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
 if c.name not in scene.collection.children:scene.collection.children.link(c)
 return c
def G(p):return Vector((p[0],-p[2],p[1]))
def digest(me):
 h=hashlib.sha256()
 for v in me.vertices:h.update(struct.pack('<fff',*v.co))
 for p in me.polygons:h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 return h.hexdigest()
protected={o.name:digest(o.data) for o in scene.objects if o.type=='MESH' and (o.name.startswith('Bridge_') or o.name in ['Fish_West_Continuous_Land','Fish_East_Continuous_Land'])}
archive=collection('90_Superseded_Static_Birds')
for ob in list(scene.objects):
 if ob.name.startswith('Seabird_'):
  for c in list(ob.users_collection):c.objects.unlink(ob)
  archive.objects.link(ob);ob.hide_set(True)
template=collection('90_Living_Coast_Templates')
for ob in list(template.objects):bpy.data.objects.remove(ob,do_unlink=True)
def mat(name,h):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=tuple((int(h[i:i+2],16)/255)**2.2 for i in (0,2,4))+(1,);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=m.diffuse_color;p.inputs['Roughness'].default_value=.86
 return m
slate=mat('Gull_Slate','465756');ivory=mat('Gull_Underwing','b7beb0');beak=mat('Gull_Beak','706a52');leafmat=mat('Breeze_Bamboo_Leaf','718257')
def empty(name,parent=None,pos=(0,0,0)):
 ob=bpy.data.objects.new(name,None);template.objects.link(ob);ob.parent=parent;ob.location=G(pos);return ob
root=empty('Coastal_Gull')
def mesh(name,verts,faces,material,parent=root):
 me=bpy.data.meshes.new(name);me.from_pydata([G(v) for v in verts],[],faces);me.materials.append(material);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);template.objects.link(ob);ob.parent=parent
 for p in me.polygons:p.use_smooth=True
 return ob
def ellipsoid(name,center,scale,material):
 bm=bmesh.new();bmesh.ops.create_uvsphere(bm,u_segments=16,v_segments=10,radius=1)
 for v in bm.verts:v.co=G((center[0]+v.co.x*scale[0],center[1]+v.co.z*scale[1],center[2]+v.co.y*scale[2]))
 me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();me.materials.append(material)
 ob=bpy.data.objects.new(name,me);template.objects.link(ob);ob.parent=root
 for p in me.polygons:p.use_smooth=True
 return ob
ellipsoid('Gull_Body',(0,0,0),(.075,.085,.22),slate)
ellipsoid('Gull_Breast',(0,-.026,-.048),(.067,.067,.16),ivory)
ellipsoid('Gull_Head',(0,.04,-.20),(.052,.054,.068),slate)
mesh('Gull_Beak',[(-.025,.035,-.24),(.025,.035,-.24),(0,.055,-.24),(0,.019,-.24),(0,.024,-.34)],[(0,2,4),(2,1,4),(1,3,4),(3,0,4),(0,3,1,2)],beak)
mesh('Gull_Tail',[(-.04,.015,.13),(.04,.015,.13),(.10,-.008,.36),(0,-.005,.29),(-.10,-.008,.36),(-.04,-.012,.13),(.04,-.012,.13)],[(0,1,2,3,4),(5,4,3,2,6),(0,4,5),(1,6,2),(0,5,6,1)],slate)
def wing(name,parent,side,stations):
 verts=[]
 for x,front,back,lift in stations:
  verts.extend([(side*x,lift,front),(side*x,lift+.022,(front+back)*.5),(side*x,lift,back),(side*x,lift-.015,(front+back)*.5)])
 faces=[(3,2,1,0)]
 for j in range(len(stations)-1):
  for k in range(4):faces.append((j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k))
 faces.append(tuple((len(stations)-1)*4+k for k in range(4)))
 ob=mesh(name,verts,faces,slate,parent);ob.data.materials.append(ivory)
 for p in ob.data.polygons:
  if p.normal.z<-.2:p.material_index=1
 return ob
for side,label in [(-1,'L'),(1,'R')]:
 shoulder=empty('Wing_'+label,root,(side*.052,.012,-.035))
 wing('Wing_Surface_'+label,shoulder,side,[(0,-.07,.14,0),(.14,-.09,.17,.018),(.30,-.045,.16,.028),(.39,.015,.14,.018)])
 wrist=empty('Tip_'+label,shoulder,(side*.37,.018,.018))
 wing('Primary_Feathers_'+label,wrist,side,[(0,-.018,.14,0),(.12,.03,.17,.01),(.25,.10,.19,.0),(.35,.20,.22,-.015)])

bpy.ops.object.select_all(action='DESELECT')
for o in list(template.objects):o.hide_set(False);o.select_set(True)
birdpath=ROOT/'assets/island_blender/coastal_gull.glb'
bpy.ops.export_scene.gltf(filepath=str(birdpath),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True)
# One curved real leaf asset, reused by the runtime for sparse drifting leaves.
bpy.ops.object.select_all(action='DESELECT')
leaf=mesh('Breeze_Leaf',[(-.018,0,0),(0,.018,-.035),(.018,0,0),(0,-.006,.19)],[(0,1,2),(0,2,3)],leafmat,None)
leaf.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'assets/island_blender/breeze_leaf.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
for o in template.objects:o.hide_set(True)

# Store a smooth height weight in UV2: the original roots stay exactly in place.
weighted=[]
for ob in scene.objects:
 if not ob.name.startswith(('Depth_Bamboo_Main_','Depth_Bamboo_Fore_')):continue
 roots=json.loads(ob['root_positions_godot']);base=min(p[1] for p in roots);top=max(v.co.z for v in ob.data.vertices)
 if not ob.data.uv_layers:ob.data.uv_layers.new(name='SurfaceUV')
 uv=ob.data.uv_layers.get('WindWeight') or ob.data.uv_layers.new(name='WindWeight')
 for loop in ob.data.loops:
  p=ob.data.vertices[loop.vertex_index].co
  near=min(roots,key=lambda r:(r[0]-p.x)**2+(r[2]+p.y)**2)
  weight=max(0,min(1,(p.z-near[1])/max(top-base,.1)))
  uv.data[loop.index].uv=(weight,0.5)
 ob['wind_weight']='UV2.x height above authored root, anchored at zero';weighted.append(ob.name)

# Add a few low, oblique shoulders behind existing peaks; keep clear mist valleys.
peaks=collection('22_Mist_Peak_Shoulders')
for ob in list(peaks.objects):bpy.data.objects.remove(ob,do_unlink=True)
for name,source,cx,cz,top,wx,wz in [
 ('Mist_Shoulder_Left','Mist_Peak_Near_02',-17,-132,10.8,1.25,.95),
 ('Mist_Shoulder_Right','Mist_Peak_Near_03',44,-146,13.5,1.35,.85),
 ('Mist_Shoulder_Remote','Mist_Peak_Far_03',13,-226,15.8,1.10,.8)]:
 src=scene.objects[source];me=src.data.copy();sx=sum(v.co.x for v in me.vertices)/len(me.vertices);sz=-sum(v.co.y for v in me.vertices)/len(me.vertices)
 oldtop=max(v.co.z for v in me.vertices)
 for v in me.vertices:
  t=(v.co.z+10)/(oldtop+10);v.co.x=cx+(v.co.x-sx)*wx+math.sin(t*math.pi)*2.0;v.co.y=-(cz+(-v.co.y-sz)*wz);v.co.z=-10+t*(top+10)
 me.update();ob=bpy.data.objects.new(name,me);peaks.objects.link(ob);ob['depth_role']='Secondary low shoulder with open mist valley'

assert all(digest(scene.objects[n].data)==h for n,h in protected.items())
manifest=json.loads((ROOT/'assets/island_blender/asset_manifest.json').read_text())
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
p=ROOT/'assets/island_blender/asset_manifest.json';d=json.loads(p.read_text());d['source_manifests']=manifest.get('source_manifests',[]);d['revision']='Living coast: articulated gull, rooted bamboo wind weights, sparse secondary mountain shoulders';p.write_text(json.dumps(d,indent=2),encoding='utf-8')
report={'blender_mcp':True,'bird_asset':str(birdpath),'bird_parts':len(template.objects)-1,'wing_joints':['Wing_L','Wing_R','Tip_L','Tip_R'],'weighted_bamboo_objects':weighted,'preserved_terrain_bridge_objects':len(protected),'secondary_shoulders':len(peaks.objects)}
(OUT/'authoring.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('LIVING_ASSETS_COMPLETE',json.dumps(report))
