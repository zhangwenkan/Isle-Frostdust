"""Camera-matched, sculpted illustration relief. Execute only through Blender MCP.
Paint is attributed Louis reference art; geometry is authored here in Blender.
"""
import bpy,math,json,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/east_spring';O=R/'artifacts/east-spring-review'
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
old=bpy.context.scene
s=bpy.data.scenes.get('East_Spring_Reconstruction')
if s:
 for o in list(s.objects):bpy.data.objects.remove(o,do_unlink=True)
else:s=bpy.data.scenes.new('East_Spring_Reconstruction')
bpy.context.window.scene=s
col=bpy.data.collections.get('39_East_Forest_Spring')
if col:
 if col.name not in s.collection.children:s.collection.children.link(col)
else:col=bpy.data.collections.new('39_East_Forest_Spring');s.collection.children.link(col)
H=1.28;HERO=Vector((34,H,.8));off=Vector((1.35,4.3,13.2));back=off.normalized();right=Vector((0,1,0)).cross(back).normalized();up=back.cross(right)
island=bpy.data.scenes['Island_Refined'];east=island.objects['Fish_East_Continuous_Land']
worldpts=[east.matrix_world@v.co for v in east.data.vertices];bvh=BVHTree.FromPolygons(worldpts,[p.vertices[:] for p in east.data.polygons])
def old_height(x,z):
 hit=bvh.ray_cast(Vector((x,-z,12)),Vector((0,0,-1)))
 return hit[0].z if hit[0] else 1.24
focus=HERO+Vector((.87513503,3.68952392,0));camera=focus+off
tan=math.tan(math.radians(19));aspect=1280/720
def ray(px,py):return -back+right*((px/320-1)*tan*aspect)+up*((1-(py-20)/180)*tan)
def ground(px,py,y=H):
 v=ray(px,py);t=(y-camera.y)/min(-.025,v.y);t=max(1,min(64,t));return camera+v*t
def plane(px,py,z):
 v=ray(px,py);return camera+v*((z-camera.z)/v.z)
def bcoord(g):return (g.x,-g.z,g.y)
def smooth(a,b,x):t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def image(name):
 im=bpy.data.images.load(str(A/name),check_existing=True);im.reload();return im
img=image('spring_paint.png');regimg=image('regions.png')
baseimg=image('base_regions.png');baseimg.colorspace_settings.name='Non-Color'
base_values=np.empty(640*400*4,dtype=np.float32);baseimg.pixels.foreach_get(base_values)
base=(base_values.reshape(400,640,4)[::-1,:,0]*255+.5).astype(np.int32)
# Blender image pixels are bottom-to-top and color-managed; guide IDs are sRGB values.
guide=np.empty(640*400*4,dtype=np.float32);regimg.pixels.foreach_get(guide)
reg=(guide.reshape(400,640,4)[::-1,:,0]*255+.5).astype(np.int32)
# PNG guide is a data image, so use direct decoding without colorspace conversion.
regimg.colorspace_settings.name='Non-Color';regimg.pixels.foreach_get(guide)
reg=(guide.reshape(400,640,4)[::-1,:,0]*255+.5).astype(np.int32)
pix=np.empty(640*400*4,dtype=np.float32);img.pixels.foreach_get(pix);colors=pix.reshape(400,640,4)[::-1]
names=['Ground','Forest_Terrace','Masonry','Pool','Right_Canopy','Left_Trunk_Roots','Middle_Trunk_Roots','Back_Trunk','Front_Trunk_Roots','Timber_Aqueduct','Falling_Water','Pool_Rim','Reeds_West','Reeds_Centre','Reeds_Back','Reeds_Front']
wallxs=[90,140,190,240,290,340,390,430];wallvs=[215,213,194,182,167,164,181,214]
def wallz(px):
 x=px-80;v=float(np.interp(x,wallxs,wallvs));return ground(px,v+20).z
roots={4:(421,244),5:(63,232),6:(190,183),7:(410,74),8:(444,317),12:(163,220),13:(228,229),14:(274,169),15:(332,285)}
def position(px,py,label):
 u=px-80;v=py-20
 if label in [0,3]:
  p=ground(px,py,H if label==0 else H-.055)
  if label==0 and p.x<27.1:p.y=max(p.y,old_height(p.x,p.z)+.008)
  return p
 if label==1:
  return plane(px,py,-24+.15*math.sin(px*.031))
 if label==2:
  # Individual painted masonry courses sit in shallow staggered relief.
  z=wallz(px);row=int((v-65)/21);brick=int((u+(row%2)*17)/38)
  relief=.05+.055*math.sin(brick*4.1+row*1.7)
  p=plane(px,py,z+relief)
  floor=4.9 if label==7 else (H-.05 if label>=12 else H+.012)
  if p.y<floor:p=ground(px,py,floor)
  return p
 if label in roots:
  rx,ry=roots[label];z=ground(rx+80,ry+20,H if label!=7 else 4.9).z
  # Barrel-like depth across trunks; buttress roots expand toward their contact.
  w={4:85,5:70,6:22,7:50,8:45}.get(label,20)
  relief=.18*max(0,1-((u-rx)/w)**2) if label<9 else 0
  if label==4:relief+=.20*math.sin(u*.11)*math.sin(v*.10)
  p=plane(px,py,z+relief)
  floor=4.9 if label==7 else (H-.05 if label>=12 else H+.012)
  if p.y<floor:p=ground(px,py,floor)
  return p
 if label==9:
  z=ground(337+80,210+20).z-(u-337)*.085
  return plane(px,py,z)
 if label==10:
  p=plane(px,py,ground(337+80,210+20).z+.018)
  return ground(px,py,H-.045) if p.y<H-.045 else p
 if label==11:
  p=ground(px,py,H+.28);return p
 return ground(px,py)
def material(name,texture=img):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=1
 tx=m.node_tree.nodes.get('SpringPaint') or m.node_tree.nodes.new('ShaderNodeTexImage');tx.name='SpringPaint';tx.image=texture;tx.interpolation='Closest'
 m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color']);return m
mats=[material('Spring_'+n) for n in names]
backmat=material('Spring_Backfill',image('spring_backfill.png'))
def mesh(name,verts,faces,uvs,mat,weights=None):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(mat)
 uv=me.uv_layers.new(name='SourcePaint');wind=me.uv_layers.new(name='WindWeights')
 indices=np.empty(len(me.loops),dtype=np.int32);me.loops.foreach_get('vertex_index',indices)
 uv.data.foreach_set('uv',np.asarray(uvs,dtype=np.float32)[indices].reshape(-1))
 wind_values=np.zeros((len(verts),2),dtype=np.float32)
 if weights:wind_values[:,0]=weights
 wind.data.foreach_set('uv',wind_values[indices].reshape(-1))
 # glTF handles the Blender Z-up to Godot Y-up conversion exactly once.
 ob['source']='Louis @LouisPretends 2119792131929739595';ob['authoring']='Blender MCP, camera-matched sculpted relief'
 return ob
STEP=2
stats={}
for label,name in enumerate(names):
 verts=[];uvs=[];faces=[];weights=[];cache={}
 def vertex(x,y):
  k=(x,y)
  if k in cache:return cache[k]
  idx=len(verts);cache[k]=idx;p=position(x,y,label);verts.append(bcoord(p));uvs.append((x/640,1-y/400))
  if label in [12,13,14,15]:
   root=roots[label][1]+20;weights.append(max(0,min(1,(root-y)/45))**1.5)
  elif label==4:weights.append(.2+.35*smooth(370,460,x-80))
  else:weights.append(0)
  return idx
 for y in range(0,400,STEP):
  for x in range(0,640,STEP):
   if int(reg[y+1,x+1])!=label:continue
   a,b,c,d=[vertex(*q) for q in [(x,y),(x+STEP,y),(x+STEP,y+STEP),(x,y+STEP)]]
   faces.extend([(a,c,b),(a,d,c)])
 if not faces:continue
 ob=mesh('Spring_'+name,verts,faces,uvs,mats[label],weights)
 stats[ob.name]={'vertices':len(verts),'triangles':len(faces)}
 (O/'build-progress.json').write_text(json.dumps(stats),encoding='utf8')
 # Thickness supplies side faces behind trunks and masonry when the hero approaches.
 if label in [2,5,6,7,8,9,11]:
  sol=ob.modifiers.new('Authored surface thickness','SOLIDIFY');sol.thickness={2:.40,9:.16,11:.3}.get(label,.28);sol.offset=-1
  bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.modifier_apply(modifier=sol.name);ob.select_set(False)

# Fill the genuinely occluded ground/wall behind each cutout, so approaching views
# never look through missing illustration pixels to the ocean.
for label in [0,2,3]:
 vv=[];ff=[];uv=[]
 for y in range(0,400,STEP):
  for x in range(0,640,STEP):
   if base[y+1,x+1]!=label or reg[y+1,x+1]==label:continue
   start=len(vv)
   for px,py in [(x,y),(x+STEP,y),(x+STEP,y+STEP),(x,y+STEP)]:
    p=position(px,py,label)
    front=position(px,py,int(reg[y+1,x+1]))
    # Backfill must remain behind the owning foreground surface along its ray.
    if (p-camera).length<(front-camera).length:p=front
    p+=(p-camera).normalized()*.055
    vv.append(bcoord(p));uv.append((px/640,1-py/400))
   ff.extend([(start,start+2,start+1),(start,start+3,start+2)])
 if ff:mesh('Spring_Backfill_%d'%label,vv,ff,uv,backmat)
# Join the slope, wall crown, wall foot and pool edge with real connecting faces.
vv=[];ff=[];uv=[]
for y in range(0,398,STEP):
 for x in range(0,638,STEP):
  a=int(base[y+1,x+1])
  for b,e1,e2 in [(int(base[y+1,x+3]),(x+2,y),(x+2,y+2)),(int(base[y+3,x+1]),(x,y+2),(x+2,y+2))]:
   if a==b or set((a,b))!=set((0,3)):continue
   start=len(vv)
   for label,pixel in [(a,e1),(a,e2),(b,e2),(b,e1)]:
    vv.append(bcoord(position(*pixel,label)));uv.append((pixel[0]/640,1-pixel[1]/400))
   ff.append(tuple(range(start,start+4)))
if ff:mesh('Spring_Terrain_Seams',vv,ff,uv,backmat)
# Deep forest backs the open spaces between trees, rather than a near sloping
# inpaint surface crossing in front of their trunks during the approach.
vv=[];ff=[];uv=[]
for i in range(19):
 for j in range(5):
  vv.append((8+i*3.1,29.0, -2+j*6.0));uv.append((i/18,j/4))
for i in range(18):
 for j in range(4):
  a=i*5+j;ff.append((a,a+1,a+6,a+5))
mesh('Spring_Deep_Forest',vv,ff,uv,material('Spring_Deep_Forest_Paint',image('deep_forest.png')))
# Extend foreground turf beyond the review frame; the ground does not end at the image edge.
vv=[];ff=[];uv=[]
for i in range(161):
 px=i*4
 for j in range(7):
  p=ground(px,400);p.z+=j*.65;p.x+=(px/640-.5)*j*.12;p.y-=.012*j
  vv.append(bcoord(p));uv.append((px/640,(.06+j*.037)%1))
for i in range(160):
 for j in range(6):
  a=i*7+j;ff.append((a,a+1,a+8,a+7))
mesh('Spring_Front_Turf',vv,ff,uv,mats[0])

# A solid landing and approach join the existing eastern land; paint blends only here.
island=bpy.data.scenes['Island_Refined'];east=island.objects['Fish_East_Continuous_Land']
worldpts=[east.matrix_world@v.co for v in east.data.vertices];bvh=BVHTree.FromPolygons(worldpts,[p.vertices[:] for p in east.data.polygons])
def old_height(x,z):
 hit=bvh.ray_cast(Vector((x,-z,12)),Vector((0,0,-1)))
 return hit[0].z if hit[0] else 1.24
def route(x):
 if x<=24.2:return .4+math.sin(x*.25)*.44
 if x<29:
  t=smooth(24.2,29,x);return (.4+math.sin(24.2*.25)*.44)*(1-t)+3.24*t
 return 3.24+(.8-3.24)*smooth(29,34,x)
vv=[];uv=[];ff=[];nx=90;nz=16
for i in range(nx+1):
 x=23.35+(35-23.35)*i/nx
 for j in range(nz+1):
  cross=-1+2*j/nz;z=route(x)+cross*(1.45+1.6*smooth(24,29,x));blend=smooth(24.1,27.1,x)
  y=old_height(x,z)*(1-blend)+H*blend
  # Bury the connector wherever the reconstructed clearing already covers it.
  y-=.08*smooth(25.0,27.0,x)
  vv.append((x,-z,y));uv.append((i/nx,j/nz))
for i in range(nx):
 for j in range(nz):
  a=i*(nz+1)+j;b=a+nz+1;ff.append((a,a+1,b+1,b))
connector=mesh('Spring_Approach_Ground',vv,ff,uv,material('Spring_Approach',bpy.data.images.load(str(R/'assets/full_island_ink/east_ground.png'),check_existing=True)))
sol=connector.modifiers.new('Earth foundation','SOLIDIFY');sol.thickness=4;sol.offset=-1
bpy.context.view_layer.objects.active=connector;connector.select_set(True);bpy.ops.object.modifier_apply(modifier=sol.name);connector.select_set(False)
# Reuse the existing eastern island's closed bedrock volume as the clearing's
# buried physical foundation, reshape it here in Blender and retain its materials.
foundation=east.copy();foundation.data=east.data.copy();foundation.name='East_Spring_Bedrock_Foundation';col.objects.link(foundation)
foundation.matrix_world.identity()
for v in foundation.data.vertices:
 p=east.matrix_world@v.co
 p.x=36+(p.x-20)*1.7;p.y=8+p.y*3.3
 if p.z>.6:p.z=H-.12
 v.co=p

# Author a reference camera, saved in the editable source but excluded from GLB.
camd=bpy.data.cameras.new('Spring_Reference_Camera');cam=bpy.data.objects.new('Spring_Reference_Camera',camd);s.collection.objects.link(cam)
cam.location=bcoord(camera);direction=Vector(bcoord(focus))-cam.location;cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();camd.type='PERSP';camd.lens=50
s.camera=cam;s.render.resolution_x=1280;s.render.resolution_y=720
meta={'camera':list(camera),'focus':list(focus),'hero':list(HERO),'focus_delta':[.87513503,3.68952392,0],'offset':list(off),'fov':38,'projection':'perspective, fixed exploration direction','route':[[x,route(x)] for x in [23.7,24.2,26,28,29,30,32,34]],'components':stats}
(O/'authoring.json').write_text(json.dumps(meta,indent=2),encoding='utf8')
bpy.ops.object.select_all(action='DESELECT')
for o in col.objects:o.select_set(True)
bpy.data.libraries.write(str(A/'east_spring.blend'),{s},path_remap='ABSOLUTE',fake_user=True,compress=True)
bpy.ops.export_scene.gltf(filepath=str(A/'east_spring.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_extras=True)
print('EAST_SPRING_EXPORTED',json.dumps(meta))
