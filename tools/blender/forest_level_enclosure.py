"""Level west path and seat the grove; author foreground and light carriers in Blender MCP."""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/forest-enclosure-review'
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
assert Path(bpy.data.filepath)==R/'assets/island_blender/nameless_island.blend'
def active():return [o for o in s.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
def signature(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 for uv in o.data.uv_layers:
  for d in uv.data:h.update(str(tuple(d.uv)).encode())
 h.update(str(o.matrix_world).encode());return h.hexdigest()
before={o.name:signature(o) for o in active()}
arc=bpy.data.collections.get('90_Before_Level_Forest') or bpy.data.collections.new('90_Before_Level_Forest')
if arc.name not in s.collection.children:s.collection.children.link(arc)
arc.hide_render=True
new=bpy.data.collections.get('34_Forest_Enclosure') or bpy.data.collections.new('34_Forest_Enclosure')
if new.name not in s.collection.children:s.collection.children.link(new)
def saved(o):
 name='LevelForestBaseline_'+o.name;b=bpy.data.objects.get(name)
 if b is None:
  b=o.copy();b.data=o.data.copy();b.name=name;arc.objects.link(b);b.hide_set(True);b.hide_render=True
 return b
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
land=s.objects['Fish_West_Continuous_Land'];floor=s.objects['PixelForest_Low_Floor']
oldland=tree(saved(land));oldfloor=tree(saved(floor))
def top_data(o):
 ids={i for p in o.data.polygons if p.material_index==0 for i in p.vertices}
 points=[o.matrix_world@v.co for v in o.data.vertices]
 kd=KDTree(len(ids))
 for i in ids:kd.insert(Vector((points[i].x,points[i].y,0)),i)
 kd.balance()
 return points,kd
landtop=top_data(saved(land));floortop=top_data(saved(floor))
def rim_height(x,y,data=landtop):
 points,kd=data
 hits=kd.find_n(Vector((x,y,0)),4)
 weights=[1/max(.0001,d*d) for _,_,d in hits]
 return sum(points[i].z*w for (_,i,_),w in zip(hits,weights))/sum(weights)
def hit(t,x,y):
 p=t.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0];return p.z if p else None
def smooth(a,b,v):
 t=max(0,min(1,(v-a)/(b-a)));return t*t*(3-2*t)
def ground(x,y):
 z=-y
 # The walkable strip is strictly level. Low shoulders stay at road height,
 # with very small irregularity deep inside the forest rather than a hillside.
 return 1.86 + smooth(1.2,5.0,-z)*(.055*math.sin(x*.58)+.045*math.sin(z*.7+x*.3))-.09*smooth(2.0,4.5,z)
def old_support(x,y,preferred=None):
 h=hit(preferred,x,y) if preferred else None
 if h is not None:return h
 hs=[a for a in [hit(oldland,x,y),hit(oldfloor,x,y)] if a is not None]
 if hs:return max(hs)
 p=oldland.find_nearest(Vector((x,y,3)))[0];return p.z if p else 2.5
changed=[]
for o,t in [(land,oldland),(floor,oldfloor)]:
 b=saved(o);o.data=b.data.copy();o.matrix_world=b.matrix_world.copy();inv=o.matrix_world.inverted()
 top_ids={i for p in o.data.polygons if p.material_index==0 for i in p.vertices}
 for v in o.data.vertices:
  p=o.matrix_world@v.co;h=rim_height(p.x,p.y,landtop if o==land else floortop)
  edge=1-smooth(2.8,4.1,p.x)
  surface=ground(p.x,p.y)-(.025 if o==floor else 0)
  if v.index in top_ids:target=surface
  elif p.z>-3.6:target=-3.6+(surface+3.6)*max(0,min(1,(p.z+3.6)/(h+3.6)))
  else:target=p.z
  p.z+=(target-p.z)*edge;v.co=inv@p
 o.data.normals_split_custom_set([(0,0,0)]*len(o.data.loops));o.data.update();changed.append(o.name)

for o in list(active()):
 name=o.name
 if name.startswith('PixelBamboo_'):
  b=saved(o);o.data=b.data.copy();o.matrix_world=b.matrix_world.copy();inv=o.matrix_world.inverted()
  root=o.matrix_world.translation;delta=ground(root.x,root.y)-old_support(root.x,root.y,oldfloor)
  for v in o.data.vertices:
   p=o.matrix_world@v.co;h=old_support(p.x,p.y,oldfloor)
   low=1-smooth(.1,2.0,p.z-h)
   p.z+=delta*(1-low)+(ground(p.x,p.y)-h)*low;v.co=inv@p
  o.data.update();o['root_godot']=[root.x,ground(root.x,root.y)-.035,-root.y];changed.append(name)
 elif name.startswith('InkSample_Rock_') and 'ForestRock' in str(o.data.materials[0].name):
  b=saved(o);o.data=b.data.copy();o.matrix_world=b.matrix_world.copy();points=[o.matrix_world@v.co for v in o.data.vertices];c=sum(points,Vector())/len(points)
  o.location.z+=ground(c.x,c.y)-old_support(c.x,c.y,oldfloor);changed.append(name)
 elif name.startswith('Coast_Low_Grass_') or name=='InkSample_Path_Grass':
  if min((o.matrix_world@v.co).x for v in o.data.vertices)>4:continue
  b=saved(o);o.data=b.data.copy();o.matrix_world=b.matrix_world.copy();inv=o.matrix_world.inverted();stride=4 if name=='InkSample_Path_Grass' else 8
  for start in range(0,len(o.data.vertices),stride):
   vs=list(o.data.vertices)[start:start+stride];pts=[o.matrix_world@v.co for v in vs];root=pts[0] if stride==4 else (pts[0]+pts[1])*.5
   newroot=root.copy();z=-root.y
   if abs(z-.25)<1.12:
    z=.25+(1 if z>=.25 else -1)*(1.18+.14*math.sin(start*.31));newroot.y=-z
   delta=newroot-root;delta.z=ground(newroot.x,newroot.y)-old_support(root.x,root.y,oldland)
   for v,p in zip(vs,pts):v.co=inv@(p+delta)
  o.data.update();changed.append(name)
 elif name=='Cliff_Fractures_West' or name.startswith('Cliff_Fern_West_') or name.startswith('Campfire_'):
  b=saved(o);o.data=b.data.copy();o.matrix_world=b.matrix_world.copy();inv=o.matrix_world.inverted()
  for v in o.data.vertices:
   p=o.matrix_world@v.co;h=rim_height(p.x,p.y)
   if name.startswith('Campfire_'):target=p.z+ground(p.x,p.y)-old_support(p.x,p.y,oldland)
   elif p.z>-3.6:target=-3.6+(ground(p.x,p.y)+3.6)*max(0,min(1,(p.z+3.6)/(h+3.6)))
   else:target=p.z
   p.z+=(target-p.z)*(1-smooth(2.8,4.1,p.x));v.co=inv@p
  o.data.update();changed.append(name)

# Three small near-side foliage groups grow outside the path. Their lower
# portions remain low; the high crowns frame the top edge instead of a wall
# of full-height stems across the actor's travel corridor.
for ob in list(new.objects):bpy.data.objects.remove(ob,do_unlink=True)
for i,(x,z,h) in enumerate([(-14.0,2.65,5.5),(-9.0,3.15,5.8),(-1.0,2.5,5.4)]):
 source=s.objects[['PixelBamboo_L0_004','PixelBamboo_L0_007','PixelBamboo_L0_010'][i]]
 ob=source.copy();ob.data=source.data.copy();ob.name='ForestForeground_%02d'%i;new.objects.link(ob)
 # Uniformly scale existing authored card around its root, then seat locally.
 baseline=saved(source);ob.data=baseline.data.copy()
 matrix=baseline.matrix_world.copy();root=matrix.translation.copy();scale=h/6.0
 for v in ob.data.vertices:
  p=matrix@v.co;v.co=Vector((x+(p.x-root.x)*scale,-z+(p.y-root.y)*scale,ground(x,-z)+(p.z-old_support(p.x,p.y,oldfloor))*scale))
 ob.matrix_world=Matrix.Identity(4);ob['pixel_bamboo_layer']=-1;ob['foreground_foliage']=True
 ob['root_godot']=[x,ground(x,-z),z]
 ob.data.update()

# Seven light carriers sit at different depths; shader will soften and animate
# their opacity. These are genuine Blender geometry, never runtime-generated.
mat=bpy.data.materials.get('Forest_Light_Shaft') or bpy.data.materials.new('Forest_Light_Shaft');mat.diffuse_color=(.8,.85,.65,.15)
for i,(x,z,width,top,bottom) in enumerate([(-14,-4.5,1.3,8.8,2.0),(-10.7,-6.5,1.8,9.4,1.9),(-7,-8.0,1.0,8.8,2.2),(-4,-5.3,1.7,8.6,1.9),(-1.6,-9.0,1.5,9.2,2.2),(-11,-11,2.1,9.8,2.3),(-6,-13,1.7,9.2,2.1)]):
 verts=[];faces=[];nx=4;ny=12
 for j in range(ny+1):
  t=j/ny;y=bottom+(top-bottom)*t;cx=x-3.4*t;cz=z-1.0*t
  for k in range(nx+1):verts.append((cx+(k/nx-.5)*width,-cz,y))
 for j in range(ny):
  for k in range(nx):
   a=j*(nx+1)+k;faces.append((a,a+1,a+nx+2,a+nx+1))
 me=bpy.data.meshes.new('ForestLightCarrier');me.from_pydata(verts,[],faces);me.materials.append(mat);me.update();uv=me.uv_layers.new(name='ShaftUV')
 for l in me.loops:
  j,k=divmod(l.vertex_index,nx+1);uv.data[l.index].uv=(k/nx,j/ny)
 ob=bpy.data.objects.new('ForestLightShaft_%02d'%i,me);new.objects.link(ob);ob['shaft_phase']=i*1.73

# Verify the continuous road against actual edited terrain, including both edges.
nt=tree(land);checks=[]
for i in range(200):
 x=-15.2+i*(18.0/199)
 for z in [-.30,.25,.80]:
  h=hit(nt,x,-z);assert h is not None,(x,z)
  checks.append(dict(x=x,z=z,height=h,error=h-1.86))
assert max(abs(a['error']) for a in checks)<.025
preserved=[o.name for o in active() if o.name in before and o.name not in changed and not o.name.startswith('Forest')]
assert all(before[n]==signature(s.objects[n]) for n in preserved)
(O/'authoring.json').write_text(json.dumps(dict(changed=changed,preserved_meshes=len(preserved),new_objects=[o.name for o in new.objects],route_samples=len(checks),route_max_error=max(abs(a['error']) for a in checks)),indent=2),encoding='utf8')
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
print('LEVEL_FOREST_EXPORTED',len(changed),'preserved',len(preserved),'route error',max(abs(a['error']) for a in checks))
