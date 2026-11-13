"""Unify the western coastal cliff and taper the forest into two open edges.
Execute only in Blender through blender-mcp. Keep walking surface and cape outline.
"""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/coast-unification-review'
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
def active():return [o for o in s.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
def sig(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 for uv in o.data.uv_layers:
  for d in uv.data:h.update(str(tuple(d.uv)).encode())
 h.update(str(o.matrix_world).encode());return h.hexdigest()
before={o.name:sig(o) for o in active()};changed=[]
arc=bpy.data.collections.get('90_Before_Coast_Unification') or bpy.data.collections.new('90_Before_Coast_Unification')
if arc.name not in s.collection.children:s.collection.children.link(arc)
arc.hide_render=True
def baseline(o):
 name='UnifiedBaseline_'+o.name;b=bpy.data.objects.get(name)
 if b is None:
  b=o.copy();b.data=o.data.copy();b.name=name;arc.objects.link(b);b.hide_set(True);b.hide_render=True
 return b
def restore(o):
 b=baseline(o);o.data=b.data.copy();o.matrix_world=b.matrix_world.copy();changed.append(o.name);return b
def smooth(a,b,v):
 t=max(0,min(1,(v-a)/(b-a)));return t*t*(3-2*t)
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def height(t,x,y):
 p=t.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0];return p.z if p else None
def planar(p):
 x=p.x
 if x < -14:x=-14+(x+14)*.43
 if x > -5:x=-5+(x+5)*.72
 w=smooth(-18.5,-13.3,x)*(1-smooth(-5.0,1.05,x))
 y=1.35+(p.y-1.35)*(.06+.94*w)
 z=p.z
 if z>1.84:z=1.84+(z-1.84)*w
 return Vector((x,y,z))
floor=s.objects['PixelForest_Low_Floor'];oldfloor=restore(floor);oldtree=tree(oldfloor)
inv=floor.matrix_world.inverted()
for v in floor.data.vertices:v.co=inv@planar(floor.matrix_world@v.co)
floor.data.normals_split_custom_set([(0,0,0)]*len(floor.data.loops));floor.data.update();newtree=tree(floor)
placements=[]
for ob in list(active()):
 if not ob.name.startswith('PixelBamboo_'):continue
 b=restore(ob);inv=ob.matrix_world.inverted()
 root0=Vector((b['root_godot'][0],-b['root_godot'][2],b['root_godot'][1]))
 root=planar(root0);support=height(newtree,root.x,root.y);assert support is not None,ob.name
 root.z=support-.035;delta=root-root0
 # Peripheral plants diminish in height so the sea opens progressively at the bridge.
 edge=smooth(-18.5,-14,root.x)*(1-smooth(-4.5,1.1,root.x))
 size=.78+.22*edge
 for v in ob.data.vertices:
  p=b.matrix_world@b.data.vertices[v.index].co
  q=root+(p-root0)*size
  w=1-smooth(.15,1.6,p.z-root0.z)
  if w>0:
   oldh=height(oldtree,p.x,p.y);newh=height(newtree,q.x,q.y)
   if oldh is not None and newh is not None:q.z+=(newh-root.z-(oldh-root0.z)*size)*w
  v.co=inv@q
 ob.data.update();ob['root_godot']=[root.x,root.z,-root.y]
 placements.append({'name':ob.name,'root_before':list(root0),'root_after':list(root),'scale':size})
 # Wind weights and atlas coordinates are never regenerated.
 assert all((a.uv-bb.uv).length<1e-7 for a,bb in zip(ob.data.uv_layers[1].data,b.data.uv_layers[1].data))
for name in ['InkSample_Rock_02','InkSample_Rock_03','InkSample_Rock_04']:
 ob=s.objects[name];b=restore(ob);inv=ob.matrix_world.inverted();ps=[ob.matrix_world@v.co for v in ob.data.vertices];center=sum(ps,Vector())/len(ps)
 target=planar(center)
 if name=='InkSample_Rock_04':target.x-=.30;target.y-=.20
 a=height(oldtree,center.x,center.y);h=height(newtree,target.x,target.y);assert a is not None and h is not None
 delta=target-center;delta.z=h-a
 for v,p in zip(ob.data.vertices,ps):v.co=inv@(p+delta)
 ob.data.update()
for ob in list(active()):
 if not ob.name.startswith('ForestLightShaft_'):continue
 restore(ob);inv=ob.matrix_world.inverted()
 for v in ob.data.vertices:v.co=inv@planar(ob.matrix_world@v.co)
 ob.data.update()
# Replace the disconnected facade chunks with a single continuous geological shell.
fractures=s.objects.get('Cliff_Fractures_West')
if fractures:
 for c in list(fractures.users_collection):c.objects.unlink(fractures)
 arc.objects.link(fractures);fractures.hide_set(True);fractures.hide_render=True;changed.append(fractures.name)
for name in ['Fish_Tidal_Reef_02_Body','Fish_Tidal_Reef_03_Body']:
 ob=s.objects.get(name)
 if ob:
  for c in list(ob.users_collection):c.objects.unlink(ob)
  arc.objects.link(ob);ob.hide_set(True);ob.hide_render=True;changed.append(name)
land=s.objects['Fish_West_Continuous_Land'];base=restore(land)
count=2626;rows=26;n=100
boundary=[i*rows for i in range(n+1)]+[n*rows+j for j in range(1,rows)]+[i*rows+rows-1 for i in range(n-1,-1,-1)]+list(range(rows-2,0,-1))
top=[base.matrix_world@v.co for v in list(base.data.vertices)[:count]]
topfaces=[p for p in base.data.polygons if p.material_index==0]
verts=[p.copy() for p in top];faces=[tuple(p.vertices) for p in topfaces];mats=[0]*len(faces)
uvs=[tuple(base.data.uv_layers.active.data[i].uv) for p in topfaces for i in p.loop_indices]
perimeter=[top[i] for i in boundary];lengths=[0.0]
for j in range(len(boundary)):lengths.append(lengths[-1]+(perimeter[(j+1)%len(boundary)]-perimeter[j]).length)
total=lengths[-1]
normals=[]
for j,p in enumerate(perimeter):
 tangent=perimeter[(j+1)%len(boundary)]-perimeter[(j-1)%len(boundary)]
 normal=Vector((-tangent.y,tangent.x,0)).normalized();normals.append(normal)
mat=bpy.data.materials.get('Coastal_Strata_Painted') or bpy.data.materials.new('Coastal_Strata_Painted');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=1
tex=mat.node_tree.nodes.get('CoastalStrata') or mat.node_tree.nodes.new('ShaderNodeTexImage');tex.name='CoastalStrata'
tex.image=bpy.data.images.load(str(R/'assets/coastal_strata/coastal_strata_color.png'),check_existing=True);tex.image.reload()
mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
fractions=[.018,.055,.105,.12,.135,.19,.25,.27,.285,.36,.46,.49,.505,.62,.72,.735,.75,.88,1.04]
def sculpt(j,t):
 p=perimeter[j];u=lengths[j];nn=normals[j]
 # Long sections share their seam direction; sparse shoulders interrupt it.
 ribs=0.0
 for cx,width,amount in [(-29.1,1.25,.36),(-26.6,1.6,.58),(-23.1,1.3,.40),(-20.0,1.7,.64),(-16.8,1.4,.72),(-13.8,1.7,.52),(-10.0,2.1,.68),(-6.0,1.5,.57),(-3.2,1.8,.70),(.0,1.3,.48),(2.4,1.4,.38)]:
  q=(p.x-cx-.42*t)/width
  shape=max(0,min(1.0,(1.0-abs(q))*1.5))
  ribs=max(ribs,amount*shape)
 seam=.38*math.sin(p.x*.62)+.20*math.sin(p.x*1.23+1.2)+.13*(ribs-.3)
 z=p.z-(p.z+3.35)*t+math.sin(min(t/.55,1)*math.pi)*seam
 # Recesses under the lips produce real narrow shadows instead of dark painted belts.
 contour=[(0,0),(.055,-.015),(.105,-.005),(.12,-.015),(.135,-.12),(.25,-.08),(.27,-.09),(.285,-.22),(.46,-.14),(.49,-.16),(.505,-.29),(.735,-.24),(.75,-.40),(1.04,-.58)]
 off=contour[-1][1]
 for (a,va),(b,vb) in zip(contour,contour[1:]):
  if a<=t<=b:off=va+(vb-va)*(t-a)/(b-a);break
 shoulder=ribs*smooth(0,.13,t)*(1-.48*smooth(.25,.85,t))
 off+=shoulder*(1.0+.28*math.sin(p.x*1.3+t*4.5))
 # Narrow diagonal joints divide broad angular ribs; no isolated boulder facade.
 joint=max(0,1-abs(math.sin(p.x*1.02+t*.85))/.17)
 off-=joint*.14*smooth(.02,.09,t)
 q=p+nn*off;q.z=z;return q
previous=boundary;previous_t=0
for t in fractions:
 current=[]
 for j in range(len(boundary)):current.append(len(verts));verts.append(sculpt(j,t))
 for j in range(len(boundary)):
  k=(j+1)%len(boundary);faces.append((previous[j],previous[k],current[k],current[j]));mats.append(1)
  a=lengths[j]/total;b=lengths[j+1]/total
  uvs.extend([(a,1-previous_t),(b,1-previous_t),(b,1-t),(a,1-t)])
 previous=current;previous_t=t
faces.append(tuple(reversed(previous)));mats.append(1);uvs.extend([(0,0)]*len(previous))
me=bpy.data.meshes.new('West_Continuous_Painted_Strata');me.from_pydata(verts,[],faces);me.materials.append(base.data.materials[0]);me.materials.append(mat);me.update()
uv=me.uv_layers.new(name='CoastUV');uv.data.foreach_set('uv',[v for pair in uvs for v in pair])
if base.data.color_attributes:
 ca=me.color_attributes.new(name='LandscapeColor',type='FLOAT_COLOR',domain='POINT')
 colors=[tuple(base.data.color_attributes['LandscapeColor'].data[i].color) for i in range(count)]+[(.3,.32,.27,1)]*(len(verts)-count)
 ca.data.foreach_set('color',[v for c in colors for v in c])
for p,m in zip(me.polygons,mats):p.material_index=m;p.use_smooth=m==0
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4]);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
empty=[f for f in bm.faces if f.calc_area()<1e-10]
if empty:bmesh.ops.delete(bm,geom=empty,context='FACES_ONLY')
bm.to_mesh(me);bm.free();me.update();land.data=me;land.matrix_world.identity()
assert max((land.matrix_world@me.vertices[i].co-top[i]).length for i in range(count))<1e-6
# Re-seat the five existing fern roots on the new ledges without deforming leaves.
landtree=tree(land)
for ob in list(active()):
 if not ob.name.startswith('Cliff_Fern_West_'):continue
 b=restore(ob);ps=[ob.matrix_world@v.co for v in ob.data.vertices]
 cx=sum(p.x for p in ps)/len(ps)
 j=min(range(len(boundary)),key=lambda j:abs(perimeter[j].x-cx)+max(0,perimeter[j].y+1.0)*20)
 target=sculpt(j,.115)
 # Source's maximum y is the root side of this hanging fern.
 oldroot=Vector((cx,max(p.y for p in ps),max(p.z for p in ps)-.10))
 delta=target-oldroot;delta.z-=.02;inv=ob.matrix_world.inverted()
 for v,p in zip(ob.data.vertices,ps):v.co=inv@(p+delta)
 ob.data.update()
preserved=[o.name for o in active() if o.name not in changed]
assert all(sig(s.objects[name])==before[name] for name in preserved)
me.calc_loop_triangles();assert not any(t.area<1e-10 for t in me.loop_triangles)
report={'changed':changed,'preserved_meshes':len(preserved),'top_vertices_unchanged':count,'perimeter_m':total,'cliff_removed':'Cliff_Fractures_West','bamboo_placements':placements,'uv2_preserved':True,'floor_bounds':[[min((floor.matrix_world@v.co)[i] for v in floor.data.vertices) for i in range(3)],[max((floor.matrix_world@v.co)[i] for v in floor.data.vertices) for i in range(3)]]}
(O/'authoring.json').write_text(json.dumps(report,indent=2),encoding='utf8')
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
print('COAST_UNIFIED',json.dumps({k:v for k,v in report.items() if k not in ['changed','bamboo_placements']}))
