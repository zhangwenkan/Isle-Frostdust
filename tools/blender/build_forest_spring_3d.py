"""Editable volumetric forest spring. Execute ONLY inside Blender via blender-mcp.
Reference informs layout; no screenshot projections or imported reference geometry.
"""
import bpy,bmesh,math,json,random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/forest_spring_3d';O=R/'artifacts/forest-spring-3d-review'
r=random.Random(1711)
source=bpy.data.scenes.get('Island_Refined')
assert source and source.objects.get('Fish_East_Continuous_Land'), 'Expected island session on MCP 9881'
east=source.objects['Fish_East_Continuous_Land']
tree=BVHTree.FromPolygons([east.matrix_world@v.co for v in east.data.vertices],[p.vertices[:] for p in east.data.polygons])
name='Forest_Spring_Volumetric'
s=bpy.data.scenes.get(name)
if s:
 for ob in list(s.objects):bpy.data.objects.remove(ob,do_unlink=True)
else:s=bpy.data.scenes.new(name)
bpy.context.window.scene=s
col=bpy.data.collections.get('40_Forest_Spring_3D') or bpy.data.collections.new('40_Forest_Spring_3D')
if col.name not in s.collection.children:s.collection.children.link(col)
# Old relief remains in its prior scene and files for problem comparison only.

def sm(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def route(x):
 t=sm(24.2,29,x);return (.4+math.sin(24.2*.25)*.44)*(1-t)+2.1*t+(.7*-1)*sm(29,34,x)
def previous(x,z):
 hit=tree.ray_cast(Vector((x,-z,15)),Vector((0,0,-1)))
 return hit[0].z if hit[0] else 1.26
def height(x,z):
 h=1.28+.055*math.sin(x*.9+z*.6)*sm(26,28,x)
 # Sunken pool, raised wooded bank, open level stopping area at its front.
 q=math.sqrt(((x-35.45)/(3.45*1.22))**2+((z+2.6)/(2.35*1.12))**2)
 h-=.73*(1-sm(.74,1.07,q))
 h+=2.3*sm(-4.6,-9.0,z)*sm(26,30,x)+.24*sm(38,43,x)
 t=sm(24.2,27.3,x)
 return previous(x,z)*(1-t)+h*t-.015*(1-t)
def gv(p):return (p[0],-p[1],p[2]) # x, depth, height -> Blender
def texture(name):
 im=bpy.data.images.load(str(A/name),check_existing=True);im.reload();return im
def material(name,file,alpha=False):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.9
 tx=m.node_tree.nodes.get('ComponentPaint') or m.node_tree.nodes.new('ShaderNodeTexImage');tx.name='ComponentPaint';tx.image=texture(file);tx.interpolation='Closest'
 m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
 if alpha:m.node_tree.links.new(tx.outputs['Alpha'],bs.inputs['Alpha']);m.surface_render_method='DITHERED'
 m.diffuse_color=(.3,.4,.25,1)
 return m
stone=material('FS_Stone','spring_stone_faces.png');bark=material('FS_Bark','spring_bark.png')
floor=material('FS_Floor','spring_floor.png');leaf=material('FS_Leaf','spring_leaf_sprays.png',True);grass=material('FS_Grass','spring_grass.png',True)
moss=material('FS_Moss','spring_moss.png',True)
water=bpy.data.materials.get('FS_Water') or bpy.data.materials.new('FS_Water');water.diffuse_color=(.08,.32,.29,.6)

def mesh(name,vs,fs,mat,uv=None,wind=None,closed=False):
 me=bpy.data.meshes.new(name);me.from_pydata([gv(p) for p in vs],[],fs);me.update()
 ob=bpy.data.objects.new('ForestSpring_'+name,me);col.objects.link(ob);me.materials.append(mat)
 layer=me.uv_layers.new(name='ComponentUV');weights=me.uv_layers.new(name='WindWeight')
 ids=np.empty(len(me.loops),dtype=np.int32);me.loops.foreach_get('vertex_index',ids)
 if uv is None:uv=[(p[0]*.3,p[2]*.4) for p in vs]
 layer.data.foreach_set('uv',np.asarray(uv,dtype=np.float32)[ids].reshape(-1))
 if wind:weights.data.foreach_set('uv',np.asarray([(w,0) for w in wind],dtype=np.float32)[ids].reshape(-1))
 if closed:
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob['authoring']='Blender MCP; volumetric component modeling';ob['reference_usage']='Composition only; no source screenshot pixels'
 return ob

# Closed land continuation, with a depressed basin and sloping wooded back bank.
vs=[];uv=[];fs=[];nx=112;nz=90
for i in range(nx+1):
 x=23.5+21.5*i/nx
 front=4.0+3*sm(24,30,x)-1.4*sm(41,45,x)
 back=-4.7-9.3*sm(24,29,x)+2*sm(41,45,x)
 for j in range(nz+1):
  z=back+(front-back)*j/nz;vs.append((x,z,height(x,z)));uv.append(((x-23.5)/21.5,1-(z+14)/21))
for i in range(nx):
 for j in range(nz):
  a=i*(nz+1)+j;b=a+nz+1;fs.append((a,a+1,b+1,b))
ground=mesh('Ground',vs,fs,floor,uv)
edge=[j for j in range(nz+1)]+[i*(nz+1)+nz for i in range(1,nx+1)]+[nx*(nz+1)+j for j in range(nz-1,-1,-1)]+[i*(nz+1) for i in range(nx-1,0,-1)]
nn=len(edge);vv=[]
for level in range(4):
 for i,k in enumerate(edge):
  x,z,y=vs[k];out=Vector((x-34,z+3));out.normalize()
  shift=[0,.18+math.sin(i*.12)*.19,-.10+math.sin(i*.12+.6)*.28,-.35][level]
  h=[y,y-.50-abs(math.sin(i*.12))*.28,-1.1+math.sin(i*.13)*.36,-3.3][level]
  vv.append((x+out.x*shift,z+out.y*shift,h))
ff=[(i+level*nn,(i+1)%nn+level*nn,(i+1)%nn+(level+1)*nn,i+(level+1)*nn) for level in range(3) for i in range(nn)]
ff.append(tuple(range(nn*3,nn*4)))
foundation=mesh('Land_Foundation',vv,ff,stone,closed=False)
for p in foundation.data.polygons:
 for j,li in enumerate(p.loop_indices):
  foundation.data.uv_layers[0].data[li].uv=((.02,.23,.23,.02)[j%4],(.06,.06,.45,.45)[j%4])

# Stone blocks have broad broken planes, bevels with unequal width and angled crowns.
def block(label,c,scale,rot=0,tile=0):
 w,d,h=scale
 outline=[(-.48,-.45),(.38,-.48),(.49,-.34),(.48,.41),(.32,.49),(-.42,.46),(-.51,.30),(-.49,-.28)]
 outline=[(x+r.uniform(-.025,.025),z+r.uniform(-.025,.025)) for x,z in outline]
 vs=[]
 for level in range(4):
  fac=[.95,1,1,.95][level];hh=[-.5,-.39,.40,.5][level]
  for x,z in outline:
   xx=x*w*fac+(level-1.5)*.035*h;zz=z*d*fac
   vs.append((c[0]+math.cos(rot)*xx+math.sin(rot)*zz,c[1]-math.sin(rot)*xx+math.cos(rot)*zz,c[2]+h*(hh+.08*x-.05*z)))
 fs=[]
 for k in range(3):
  for j in range(8):fs.append((k*8+j,k*8+(j+1)%8,(k+1)*8+(j+1)%8,(k+1)*8+j))
 fs.extend([tuple(range(7,-1,-1)),tuple(range(24,32))])
 ob=mesh(label,vs,fs,stone,closed=True)
 layer=ob.data.uv_layers[0]
 for p in ob.data.polygons:
  top=p.normal.z>.65;ti=(tile%4)+(4 if top else 0); ox=(ti%4)/4;oy=(ti//4)/2
  # Allocate full faces coherently; bevels follow adjacent top/side regions.
  for li in p.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co
   dx=v.x-c[0];dz=-v.y-c[1];dy=v.z-c[2]
   if top:u=dx/max(w,d)+.5;v=dz/max(w,d)+.5
   elif abs(p.normal.y)>.45:u=dx/max(w,d)+.5;v=dy/h+.5
   else:u=dz/max(w,d)+.5;v=dy/h+.5
   layer.data[li].uv=(ox+.008+max(0,min(1,u))*.234,oy+.016+max(0,min(1,v))*.468)
 return ob

# Uneven rear retaining wall: a low left entrance, tall offset central run, right return.
wall=[(31.0,-3.0,1.25,1.0),(32.05,-3.9,1.5,1.05),(33.5,-4.65,1.55,1.2),(35.05,-4.97,1.6,1.25),(36.6,-4.87,1.55,1.3),(38,-4.38,1.38,1.12),(39.0,-3.45,1.1,1.0)]
for row in range(3):
 for i,(x,z,w,d) in enumerate(wall):
  if row==2 and i==0:continue
  xx=x+([0,.17,-.07][row]);zz=z-.10*row;hh=.80+r.uniform(-.065,.065)
  block('Wall_%d_%02d'%(row,i),(xx,zz,1.25+row*.70+math.sin(i*1.7)*.055), (w, d,hh),rot=(i-3)*-.14,tile=i%4)
# Fallen shoulder at left and partial low right lip leave pool front unbuilt.
for i,(x,z,w,d,h) in enumerate([(30.4,-2.4,1.4,1.3,.85),(31.1,-3.8,1.7,1.5,.85),(39,-1.9,.7,1.3,.72),(38.8,-.7,.65,1.1,.54),(38.15,.15,1.0,.65,.43),(31.8,-.3,.9,.65,.32)]):
 block('Bank_Rock_%02d'%i,(x,z,height(x,z)+h*.15),(w,d,h),rot=.35*i,tile=i%4)

def tube(label,points,radii,mat=bark,sides=10):
 # Smooth the authored bends, keeping the trunk/branch silhouette intentional.
 old_points=[Vector(p) for p in points];old_r=radii[:];points=[];radii=[]
 for i in range(len(old_points)-1):
  a=old_points[max(0,i-1)];b=old_points[i];c=old_points[i+1];d=old_points[min(len(old_points)-1,i+2)]
  for j in range(4):
   t=j/4
   points.append(tuple(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)))
   radii.append(old_r[i]*(1-t)+old_r[i+1]*t)
 points.append(tuple(old_points[-1]));radii.append(old_r[-1])
 vv=[];uv=[]
 for k,cp in enumerate(points):
  p=Vector(cp);v=Vector(points[min(k+1,len(points)-1)])-Vector(points[max(0,k-1)])
  v.normalize();a=v.cross(Vector((0,0,1)))
  if a.length<.1:a=v.cross(Vector((0,1,0)))
  a.normalize();b=v.cross(a).normalized()
  for j in range(sides):
   angle=math.tau*j/sides;rr=radii[k]*(1+.07*math.sin(j*2.13+k*.7))
   vv.append(tuple(p+rr*(a*math.cos(angle)+b*math.sin(angle))));uv.append((j/(sides-1),k/(len(points)-1)))
 ff=[]
 for k in range(len(points)-1):
  for j in range(sides):ff.append((k*sides+j,k*sides+(j+1)%sides,(k+1)*sides+(j+1)%sides,(k+1)*sides+j))
 ff.extend([tuple(range(sides-1,-1,-1)),tuple(range((len(points)-1)*sides,len(points)*sides))])
 return mesh(label,vv,ff,mat,uv,closed=True)

# Each crown comprises bowed foliage sprays with different directions and depths.
def spray(label,c,size,tilt,azimuth,tile):
 vv=[];uv=[];ww=[];n=4
 for i in range(n+1):
  for j in range(n+1):
   u=i/n;v=j/n;xx=(u-.5)*size;yy=(v-.5)*size*.85
   lift=.28*size*(1-4*(u-.5)**2)*(1-4*(v-.5)**2)
   z=yy*math.cos(tilt);h=yy*math.sin(tilt)+lift
   vv.append((c[0]+xx*math.cos(azimuth)-z*math.sin(azimuth),c[1]+xx*math.sin(azimuth)+z*math.cos(azimuth),c[2]+h))
   uv.append(((tile%2+u)/2,(tile//2+v)/2));ww.append(.3+.65*v)
 ff=[]
 for i in range(n):
  for j in range(n):
   a=i*(n+1)+j;ff.append((a,a+1,a+n+2,a+n+1))
 return mesh(label,vv,ff,leaf,uv,ww)

trees=[(28.2,-2.6,6.6,.64,-.5),(31.8,-6.3,7.2,.60,.9),(36.2,-8.1,7.6,.58,-.7),(40.25,-4.2,7.1,.85,-.65),(41.8,1.5,6.6,.66,-.8),(27.4,-8.3,7.9,.47,.4),(43,-9.2,8.4,.6,-.5),(33.3,-11.9,8.4,.47,-.4),(38.8,-12.3,8.6,.44,.6),(26.5,-5.8,6.9,.37,.5)]
for ti,(x,z,hh,rad,lean) in enumerate(trees):
 base=height(x,z)-.13
 pts=[(x,z,base),(x+lean*.12,z-.1,base+.75),(x+lean*.43,z+.18,base+hh*.37),(x+lean,z-.13,base+hh*.71),(x+lean*1.3,z-.15,base+hh)]
 tube('Tree_%02d_Trunk'%ti,pts,[rad*1.45,rad,.74*rad,.50*rad,.22*rad])
 for ri in range(5):
  ang=ri*math.tau/5+ti*.61;length=rad*(2.5+(ri%3)*.6)
  ex=x+math.cos(ang)*length;ez=z+math.sin(ang)*length
  tube('Tree_%02d_Root_%d'%(ti,ri),[(x,z,base+.54),(x+math.cos(ang)*rad,z+math.sin(ang)*rad,base+.12),(ex,ez,height(ex,ez)+.035),(ex+math.cos(ang)*.38,ez+math.sin(ang)*.38,height(ex+math.cos(ang)*.38,ez+math.sin(ang)*.38)-.06)],[rad*.38,rad*.32,.095,.013],sides=7)
 for bi in range(3):
  a=bi*2.1+ti*.81;reach=2.0+rad;cx=x+lean+math.cos(a)*reach;cz=z+math.sin(a)*reach
  tube('Tree_%02d_Branch_%d'%(ti,bi),[pts[2],(x+lean*.8+math.cos(a)*reach*.48,z+math.sin(a)*reach*.4,base+hh*.70),(cx,cz,base+hh*.84),(cx+math.cos(a)*.8,cz+math.sin(a)*.8,base+hh*.93)],[rad*.38,rad*.24,.105,.03],sides=8)
  for fi in range(6):
   angle=fi*math.tau/6
   spray('Tree_%02d_Leaves_%d_%d'%(ti,bi,fi),(cx+math.cos(angle)*1.0,cz+math.sin(angle)*.9,base+hh*.86+(.35 if fi%2 else -.15)),3.2+rad, .35+(fi%3)*.24,angle, (fi+ti)%4)

# Layered woodland understorey closes the high sea horizon, using spatial crowns.
for si,(x,z) in enumerate([(26.7,-8.8),(29,-10.8),(31.5,-11.3),(34,-11.8),(36.6,-12),(39,-11.6),(41.4,-11),(43.3,-8.8),(41.6,-5.8)]):
 h=height(x,z)
 for fi in range(7):
  angle=fi*math.tau/7
  spray('Understorey_%02d_%d'%(si,fi),(x+math.cos(angle)*.75,z+math.sin(angle)*.65,h+1.0+(fi%3)*.65),3.8,.55+(fi%2)*.5,angle,si%4)
for si,(x,z) in enumerate([(26.6,-5),(28.4,-7),(30.5,-7.5),(33.2,-8),(35.6,-8.5),(38,-7.9),(40.3,-7)]):
 h=height(x,z)
 for fi in range(6):
  angle=fi*math.tau/6
  spray('Bank_Crown_%02d_%d'%(si,fi),(x+math.cos(angle)*.55,z+math.sin(angle)*.5,h+.8+(fi%2)*.9),3.5,1.0+(fi%2)*.25,angle,si%4)

# Foreground root curls remain outside the route, framing rather than hiding the hero.
tube('Wall_Overgrown_Root',[(32,-6.4,4.1),(32.3,-5.2,3.6),(32.45,-3.5,3.12),(32.1,-3.1,2.45),(32.25,-2.8,1.5)],[.29,.26,.22,.17,.055],sides=9)

# A joined wooden U-channel: a real bed and two cheeks, sloped down into the pool.
start=Vector((38.0,-5.3,3.08));end=Vector((36.85,-2.3,2.82));direction=(end-start).normalized()
side=direction.cross(Vector((0,0,1))).normalized()
def beam(label,a,b,width,depth):
 p=Vector(a);q=Vector(b);v=(q-p).normalized();side=v.cross(Vector((0,0,1)))
 if side.length<.1:side=Vector((1,0,0))
 side.normalize();up=side.cross(v).normalized()
 vv=[tuple(c+side*width*sx*.5+up*depth*sy*.5) for c in [p,q] for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 ob=mesh(label,vv,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],bark,closed=True)
 for face in ob.data.polygons:
  for li in face.loop_indices:
   vi=ob.data.loops[li].vertex_index;ob.data.uv_layers[0].data[li].uv=((vi%4)/3,0 if vi<4 else 1)
 return ob
beam('Trough_Bed',start,end,.74,.15)
for side_sign in [-1,1]:beam('Trough_Cheek_'+str(side_sign),start+side*(.40*side_sign)+Vector((0,0,.14)),end+side*(.40*side_sign)+Vector((0,0,.14)),.12,.36)
beam('Trough_Support',(37.35,-3.55,1.13),(37.35,-3.55,2.78),.17,.18)
beam('Trough_Brace',(37.35,-3.55,1.9),(36.94,-2.48,2.73),.13,.15)

# Water surface and pool-bed stones are independent modeled parts.
cx=35.45;cz=-2.6;vv=[(cx,cz,1.115)];uv=[(.5,.5)];N=80
for i in range(N):
 a=math.tau*i/N;rr=1+.025*math.sin(a*3)+.018*math.cos(a*7)
 vv.append((cx+3.32*math.cos(a)*rr,cz+2.28*math.sin(a)*rr,1.115));uv.append((.5+.5*math.cos(a),.5+.5*math.sin(a)))
mesh('Pool',vv,[(0,(i+1)%N+1,i+1) for i in range(N)],water,uv)
vv=[];uv=[]
for i in range(17):
 t=i/16;p=end+Vector((0,t*.25,-1.65*t));w=.30+.07*t
 for sign in [-1,1]:vv.append(tuple(p+side*sign*w));uv.append(((sign+1)/2,1-t))
mesh('Falling_Water',vv,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(16)],water,uv)
mesh('Channel_Water',[tuple(p+side*sign*.31+Vector((0,0,.091))) for p in [start,end] for sign in [-1,1]],[(0,1,3,2)],water,[(0,0),(1,0),(0,1),(1,1)])
for i,(x,z,w,d) in enumerate([(34.1,-1.5,.8,.55),(35.2,-3.2,.95,.70),(36.7,-1.3,.57,.78),(34.5,-2.6,.60,.38),(37.7,-3.2,.67,.48),(33.1,-2.4,.45,.75),(35.7,-.9,.44,.33)]):
 block('Submerged_Stone_%d'%i,(x,z,height(x,z)+.10),(w,d,.22),rot=i*.83,tile=i%4)

def grass_clump(i,x,z,scale,sedge=False):
 vv=[];ff=[];uv=[];ww=[];h=height(x,z)-.025;tile=(2+i%2) if sedge else i%2
 for k in range(3):
  a=k*math.pi/3+i;side=Vector((math.cos(a)*scale*.48,math.sin(a)*scale*.48,0));base=Vector((x,z,h));off=len(vv)
  for p in [base-side,base+side,base+side*.83+Vector((.08,0,scale)),base-side*.83+Vector((.08,0,scale))]:vv.append(tuple(p))
  ff.append(tuple(off+j for j in range(4)));uv.extend([(tile/4,0),((tile+1)/4,0),((tile+1)/4,1),(tile/4,1)]);ww.extend([0,0,1,1])
 return mesh(('Sedge_' if sedge else 'Grass_')+str(i),vv,ff,grass,uv,ww)
for i,(x,z,h) in enumerate([(32.4,-1.8,.92),(33.2,-.7,.72),(35.0,-4.15,1.05),(38.2,-1.1,.76),(36.7,-.2,.82)]):grass_clump(i,x,z,h,True)
for i in range(120):
 x=r.uniform(25.7,43.5);z=r.uniform(-9.5,4.6);q=math.sqrt(((x-35.45)/3.45)**2+((z+2.6)/2.35)**2)
 if abs(z-route(x))<.94 or q<1.13:continue
 grass_clump(i,x,z,r.uniform(.32,.64))

# Bring the basin and enclosing masonry into foreground scale, retaining a level
# pool and actual ground depression. These transforms are authored in Blender.
feature_prefixes=('Wall_','Bank_Rock_','Pool','Submerged_','Trough_','Falling_','Channel_','Sedge_')
for ob in list(col.objects):
 title=ob.name.removeprefix('ForestSpring_')
 if title.startswith(feature_prefixes) and title!='Wall_Overgrown_Root':
  for v in ob.data.vertices:
   v.co.x=35.45+(v.co.x-35.45)*1.22
   v.co.y=2.6+(v.co.y-2.6)*1.12
   v.co.z=1.115+(v.co.z-1.115)*1.18

# Moss follows selected joints and the curved crown; it does not blanket the wall.
for i,(x,z,w,h) in enumerate([(30.7,-3.1,.85,.6),(33.6,-4.34,1.1,1.05),(36.0,-4.3,.70,.55),(39.1,-3.85,.85,.76)]):
 top=3.43 if i else 2.50
 vv=[(x-w*.5,z-.10,top+.06),(x+w*.5,z-.10,top+.06),(x+w*.5,z+.09,top-h),(x-w*.5,z+.09,top-h)]
 mesh('Moss_Drape_%d'%i,vv,[(0,1,2,3)],moss,[(0,1),(1,1),(1,0),(0,0)],[0,0,.13,.13])

# A few grouped sedges and tiny woodland flowers, leaving the walking band clear.
for gi,(x,z) in enumerate([(29.8,.1),(30.7,3.0),(32.5,.25),(33.1,2.65),(35.0,2.6),(37.0,.75),(39,2.0)]):
 for j in range(3):grass_clump(300+gi*3+j,x+.17*j,z+.12*math.sin(j),.40+.10*(j%2))
 flower=bpy.data.materials.get('FS_Flower_'+str(gi%2)) or bpy.data.materials.new('FS_Flower_'+str(gi%2));flower.diffuse_color=((.68,.66,.43,1) if gi%2 else (.48,.46,.58,1))
 for j in range(3):
  bx=x+.16*j; bz=z-.1;h=height(bx,bz)+.30+.04*j
  tube('Flower_Stem_%d_%d'%(gi,j),[(bx,bz,h-.32),(bx+.015,bz,h)],[.013,.009],grass,sides=5)
  vv=[];ff=[]
  for k in range(5):
   a=k*math.tau/5;ox=math.cos(a)*.045;oz=math.sin(a)*.045;idx=len(vv)
   vv.extend([(bx,bz,h-.025),(bx+ox-oz*.5,bz+oz+ox*.5,h+.02),(bx+ox*1.6,bz+oz*1.6,h),(bx+ox+oz*.5,bz+oz-ox*.5,h+.02)])
   ff.append(tuple(range(idx,idx+4)))
  mesh('Flowers_%d_%d'%(gi,j),vv,ff,flower)

# Editable inspection camera, excluded from game export.
camd=bpy.data.cameras.new('Spring_3D_Inspection');cam=bpy.data.objects.new('Spring_3D_Inspection',camd);s.collection.objects.link(cam)
cam.location=gv((36.0,14.8,8.2));target=Vector(gv((34.9,-1.2,3.9)));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam
camd.lens=50;s.render.resolution_x=1280;s.render.resolution_y=720
bpy.ops.object.select_all(action='DESELECT')
for ob in col.objects:ob.select_set(True)
bpy.data.libraries.write(str(A/'forest_spring.blend'),{s},path_remap='ABSOLUTE',fake_user=True,compress=True)
bpy.ops.export_scene.gltf(filepath=str(A/'forest_spring.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_extras=True)
info={'scene':s.name,'objects':len(col.objects),'vertices':sum(len(o.data.vertices) for o in col.objects),'reference_image_pixels':False,'source':'All meshes built through Blender MCP','pool_center':[cx,1.115,cz],'route':[[x,route(x),height(x,route(x))] for x in [23.7,24.2,26,28,30,32,34]],'textures':[im.name for im in bpy.data.images if str(A) in bpy.path.abspath(im.filepath)]}
(O/'authoring.json').write_text(json.dumps(info,indent=2),encoding='utf8')
print('VOLUMETRIC_SPRING_EXPORTED',json.dumps(info))
