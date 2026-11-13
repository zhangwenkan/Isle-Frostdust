"""Extend the existing western promontory in the live Blender MCP scene.

Keep its level top and continuous cliff shell. The forest is not translated.
"""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/west-cape-extension-review'
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
def active():return [o for o in s.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
def signature(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 for uv in o.data.uv_layers:
  for d in uv.data:h.update(str(tuple(d.uv)).encode())
 h.update(str(o.matrix_world).encode());return h.hexdigest()
before={o.name:signature(o) for o in active()}
archive=bpy.data.collections.get('90_Before_West_Cape_Extension') or bpy.data.collections.new('90_Before_West_Cape_Extension')
if archive.name not in s.collection.children:s.collection.children.link(archive)
archive.hide_render=True
def baseline(o):
 b=bpy.data.objects.get('WestExtensionBaseline_'+o.name)
 if b is None:
  b=o.copy();b.data=o.data.copy();b.name='WestExtensionBaseline_'+o.name;archive.objects.link(b);b.hide_set(True);b.hide_render=True
 return b
def shift(x):
 t=max(0.,min(1.,(x+15.)/4.));return -9.*(1.-t*t*(3.-2.*t))
def deform(p):return Vector((p.x+shift(p.x),p.y,p.z))
changed=[]
for o in list(active()):
 name=o.name
 land=name=='Fish_West_Continuous_Land'
 fire=name.startswith('Campfire_')
 grass=name.startswith('Coast_Low_Grass_') or name=='InkSample_Path_Grass'
 cliff=name=='Cliff_Fractures_West' or name.startswith('Cliff_Fern_West_')
 if not (land or fire or grass or cliff):continue
 if min((o.matrix_world@v.co).x for v in o.data.vertices)>=-11:continue
 b=baseline(o);o.data=b.data.copy();o.matrix_world=b.matrix_world.copy();inv=o.matrix_world.inverted()
 if name.startswith('Cliff_Fern_West_'):
  pts=[o.matrix_world@v.co for v in o.data.vertices]
  center=sum(pts,Vector())/len(pts)
  delta=Vector((shift(center.x),0,0))
  for v,p in zip(o.data.vertices,pts):v.co=inv@(p+delta)
 elif grass:
  stride=4 if name=='InkSample_Path_Grass' else 8
  for start in range(0,len(o.data.vertices),stride):
   vs=list(o.data.vertices)[start:start+stride];pts=[o.matrix_world@v.co for v in vs]
   root=pts[0] if stride==4 else (pts[0]+pts[1])*.5
   delta=Vector((shift(root.x),0,0))
   for v,p in zip(vs,pts):v.co=inv@(p+delta)
 else:
  for v in o.data.vertices:v.co=inv@deform(o.matrix_world@v.co)
 # Clear obsolete custom normals only where the continuous shell changed.
 if land or cliff:o.data.normals_split_custom_set([(0,0,0)]*len(o.data.loops))
 o.data.update();changed.append(name)
land=s.objects['Fish_West_Continuous_Land']
tree=BVHTree.FromPolygons([land.matrix_world@v.co for v in land.data.vertices],[tuple(p.vertices) for p in land.data.polygons])
samples=[]
for i in range(551):
 x=-24.2+(2.8+24.2)*i/550
 for z in [-.30,.25,.80]:
  p=tree.ray_cast(Vector((x,-z,20)),Vector((0,0,-1)))[0]
  assert p is not None,(x,z)
  samples.append({'x':x,'z':z,'height':p.z,'error':p.z-1.86})
assert max(abs(a['error']) for a in samples)<.025
preserved=[o.name for o in active() if o.name in before and o.name not in changed]
assert all(signature(s.objects[n])==before[n] for n in preserved)
def top_points(o):
 ids={i for p in o.data.polygons if p.material_index==0 for i in p.vertices}
 return [[float(v) for v in o.matrix_world@o.data.vertices[i].co] for i in sorted(ids)]
report={'extension_m':9,'hero_start_x':-24.2,'campfire_x':-26.5,'changed':changed,'preserved_meshes':len(preserved),'route_samples':len(samples),'max_route_height_error':max(abs(a['error']) for a in samples),'before_top':top_points(baseline(land)),'after_top':top_points(land),'west_x_before':min(p[0] for p in top_points(baseline(land))),'west_x_after':min(p[0] for p in top_points(land))}
(O/'authoring.json').write_text(json.dumps(report,indent=2),encoding='utf8')
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
print('WEST_CAPE_EXTENDED',json.dumps({k:v for k,v in report.items() if k not in ['before_top','after_top']}))
