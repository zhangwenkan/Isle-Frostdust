"""Shorten the rear forest and raise its actual opaque slope, via Blender MCP."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/forest-backwall-review'
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
def active():return [o for o in s.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
def signature(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
 for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 for uv in o.data.uv_layers:
  for d in uv.data:h.update(str(tuple(d.uv)).encode())
 h.update(str(o.matrix_world).encode());return h.hexdigest()
before={o.name:signature(o) for o in active()}
arc=bpy.data.collections.get('90_Before_Compact_Forest_Backwall') or bpy.data.collections.new('90_Before_Compact_Forest_Backwall')
if arc.name not in s.collection.children:s.collection.children.link(arc)
arc.hide_render=True
def baseline(o):
 b=bpy.data.objects.get('BackwallBaseline_'+o.name)
 if b is None:
  b=o.copy();b.data=o.data.copy();b.name='BackwallBaseline_'+o.name;arc.objects.link(b);b.hide_set(True);b.hide_render=True
 return b
def smooth(a,b,v):
 t=max(0,min(1,(v-a)/(b-a)));return t*t*(3-2*t)
def depth(y):return y if y<=4 else 4+(y-4)*.52
def horizontal(x,y):
 d=max(0,y-1.65-.16*math.sin(x*.64))
 left=-18.6-5.8*smooth(0,10,d)
 right=2.7-5*smooth(0,17,d)+.4*math.sin(d*.5)*smooth(0,4,d)
 u=(x-left)/(right-left)
 return x+(((-21.3)+(2.8+21.3)*u)-x)*smooth(8,16,y)
def rise(x,y):
 nx=horizontal(x,y)
 side=smooth(-22.5,-17.8,nx)*(1-smooth(-1.8,3.2,nx))
 # A shallow recess opens between two shoulders. Successive ledges have
 # different setbacks, rather than four parallel lines across the forest.
 valley=1.2*math.exp(-((x+8.2)/3.1)**2)-.45*math.exp(-((x+14.2)/2.7)**2)
 d=y+.30*math.sin(x*.42)-valley*smooth(7.0,12.0,y)
 terraces=1.0*smooth(3.4,5.3,d)+2.3*smooth(7.8,10.2,d+.45*math.sin(x*.5+.7))+2.5*smooth(11.3,13.9,d+.55*math.sin(x*.36-1))+3.2*smooth(15.0,18.4,d+.35*math.sin(x*.48+1.2))
 return terraces*side
def planar(p):return Vector((horizontal(p.x,p.y),depth(p.y),p.z))
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
floor=s.objects['PixelForest_Low_Floor'];base=baseline(floor);floor.data=base.data.copy();floor.matrix_world=base.matrix_world.copy()
oldtree=tree(base);inv=floor.matrix_world.inverted();changed=[floor.name]
topids={i for p in floor.data.polygons if p.material_index==0 for i in p.vertices}
for v in floor.data.vertices:
 p=floor.matrix_world@v.co;q=planar(p)
 weight=1 if v.index in topids else max(0,min(1,(p.z+3.6)/5.45))
 q.z+=rise(p.x,p.y)*weight;v.co=inv@q
mat=bpy.data.materials.get('Forest_Backwall_Moss') or bpy.data.materials.new('Forest_Backwall_Moss')
mat.diffuse_color=(.08,.125,.085,1);mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Roughness'].default_value=1
floor.data.materials.append(mat)
side_mat=bpy.data.materials.get('Forest_Backwall_Rock') or bpy.data.materials.new('Forest_Backwall_Rock')
side_mat.use_nodes=True;side_mat.diffuse_color=(.12,.16,.13,1)
side_mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=side_mat.diffuse_color
floor.data.materials.append(side_mat)
for p,old in zip(floor.data.polygons,base.data.polygons):
 d=sum((base.matrix_world@base.data.vertices[i].co).y for i in old.vertices)/len(old.vertices)
 if d>3.4:p.material_index=2 if old.material_index==0 else 3
 p.use_smooth=p.material_index!=1
paint_uv=floor.data.uv_layers.new(name='BackwallPigmentUV')
for loop in floor.data.loops:
 p=floor.matrix_world@floor.data.vertices[loop.vertex_index].co
 paint_uv.data[loop.index].uv=((p.x+24)/30,(p.z-1.6)/14)
uvnode=mat.node_tree.nodes.get('BackwallUV') or mat.node_tree.nodes.new('ShaderNodeUVMap');uvnode.name='BackwallUV';uvnode.uv_map='BackwallPigmentUV'
texnode=mat.node_tree.nodes.get('BackwallPigment') or mat.node_tree.nodes.new('ShaderNodeTexImage');texnode.name='BackwallPigment'
texnode.image=bpy.data.images.load(str(R/'assets/pixel_bamboo_west/forest_floor.png'),check_existing=True);texnode.image.reload()
mat.node_tree.links.new(uvnode.outputs['UV'],texnode.inputs['Vector']);mat.node_tree.links.new(texnode.outputs['Color'],bs.inputs['Base Color'])
floor.data.normals_split_custom_set([(0,0,0)]*len(floor.data.loops));floor.data.update();newtree=tree(floor)
def hit(t,x,y):
 p=t.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0];return p.z if p else None
placements=[]
for ob in list(active()):
 if not ob.name.startswith('PixelBamboo_'):continue
 b=baseline(ob);ob.data=b.data.copy();ob.matrix_world=b.matrix_world.copy();inv=ob.matrix_world.inverted()
 oldroot=Vector((b['root_godot'][0],-b['root_godot'][2],b['root_godot'][1]))
 root=planar(oldroot);support=hit(newtree,root.x,root.y)
 assert support is not None,ob.name
 root.z=support-.035;delta=root-oldroot
 # Keep each crown's shape and UV2. Only its lowest culms follow the hillside.
 for v in ob.data.vertices:
  p=ob.matrix_world@v.co;q=p+delta
  localheight=p.z-oldroot.z
  w=1-smooth(.15,1.6,localheight)
  if w>0:
   h=hit(newtree,q.x,q.y)
   oldh=hit(oldtree,p.x,p.y)
   if h is not None and oldh is not None and h>0 and oldh>0:
    q.z+=(h-oldh-delta.z)*w
  v.co=inv@q
 ob.data.update();ob['root_godot']=[root.x,root.z,-root.y];changed.append(ob.name)
 placements.append({'name':ob.name,'before':list(oldroot),'after':list(root)})
rocks=[]
for name in ['InkSample_Rock_02','InkSample_Rock_03','InkSample_Rock_04']:
 ob=s.objects[name];b=baseline(ob);ob.data=b.data.copy();ob.matrix_world=b.matrix_world.copy();inv=ob.matrix_world.inverted()
 pts=[ob.matrix_world@v.co for v in ob.data.vertices];center=sum(pts,Vector())/len(pts)
 target=planar(center)
 if name=='InkSample_Rock_04':target.x+=.25
 oldheight=hit(oldtree,center.x,center.y);newheight=hit(newtree,target.x,target.y)
 assert oldheight is not None and newheight is not None
 delta=target-center;delta.z=newheight-oldheight
 for v,p in zip(ob.data.vertices,pts):v.co=inv@(p+delta)
 ob.data.update();changed.append(name)
 rocks.append({'name':name,'center_godot':[target.x,center.z+delta.z,-target.y],'vertical_delta':delta.z})
for ob in list(active()):
 if not ob.name.startswith('ForestLightShaft_'):continue
 b=baseline(ob);ob.data=b.data.copy();ob.matrix_world=b.matrix_world.copy();inv=ob.matrix_world.inverted()
 for v in ob.data.vertices:
  p=ob.matrix_world@v.co;q=planar(p);q.z+=rise(p.x,p.y);v.co=inv@q
 ob.data.update();changed.append(ob.name)
preserved=[o.name for o in active() if o.name in before and o.name not in changed]
assert all(signature(s.objects[n])==before[n] for n in preserved)
uv2_ok=all(all((a.uv-bb.uv).length<1e-7 for a,bb in zip(s.objects[p['name']].data.uv_layers[1].data,bpy.data.objects['BackwallBaseline_'+p['name']].data.uv_layers[1].data)) for p in placements)
assert uv2_ok
pts=[floor.matrix_world@v.co for v in floor.data.vertices]
report={'changed':changed,'preserved_meshes':len(preserved),'old_rear_depth':max((base.matrix_world@v.co).y for v in base.data.vertices),'new_rear_depth':max(p.y for p in pts),'top_height':max(p.z for p in pts),'bamboo_moved':placements,'bamboo_uv2_preserved':uv2_ok,'rocks':rocks}
(O/'authoring.json').write_text(json.dumps(report,indent=2),encoding='utf8')
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
print('COMPACT_FOREST_BACKWALL',json.dumps({k:v for k,v in report.items() if k not in ['bamboo_moved','changed']}))
