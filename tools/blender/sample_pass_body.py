# All geometry in this file is authored in the live Blender scene via MCP.
# Re-runnable: remove this pass's named assets before replacing them.
import math, json, bpy, bmesh
from mathutils import Vector
SAMPLE='13_HD2D_Sample'
if SAMPLE not in COL:
 c=bpy.data.collections.get(SAMPLE) or bpy.data.collections.new(SAMPLE)
 if c.name not in scene.collection.children:scene.collection.children.link(c)
 COL[SAMPLE]=c
for ob in list(COL[SAMPLE].objects):bpy.data.objects.remove(ob,do_unlink=True)

def pixelmat(key,file,cutout=False):
 m=MAT.get(key) or material(key,'ffffff');MAT[key]=m
 p=m.node_tree.nodes.get('Principled BSDF')
 for n in list(m.node_tree.nodes):
  if n.type=='TEX_IMAGE':m.node_tree.nodes.remove(n)
 img=bpy.data.images.load(str(OUT/'pixel'/file),check_existing=True);img.reload();img.pack()
 tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img;tex.interpolation='Closest'
 m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
 p.inputs['Roughness'].default_value=1
 if cutout:
  m.node_tree.links.new(tex.outputs['Alpha'],p.inputs['Alpha'])
  if hasattr(m,'surface_render_method'):m.surface_render_method='DITHERED'
  m['pixel_cutout']=True
 return m

for key,file in [('rock','stone_fracture.png'),('rock_light','stone_fracture.png'),('wet_rock','stone_fracture.png'),
 ('grass','grass_cluster.png'),('moss','moss_cluster.png'),('path','trail_dust.png'),('bark','bark_plates.png'),('wood','wood_grain.png')]:pixelmat(key,file)
for key,file in [('PX_Pine_A','pine_bough_a.png'),('PX_Pine_B','pine_bough_b.png'),('PX_Fern','fern_spray.png'),('PX_Grass','grass_tuft.png')]:pixelmat(key,file,True)

# Reset UV scale on retained ground: 128 pixels per four world units.
for name in ['West_Island_Grass_Soil','East_Island_Grass_Soil']:
 ob=bpy.data.objects.get(name)
 if ob:
  uv=ob.data.uv_layers.active
  for li,loop in enumerate(ob.data.loops):
   v=ob.data.vertices[loop.vertex_index].co;uv.data[li].uv=(v.x*.25,-v.y*.25)

# Retire obsolete surfaces only in the western sample; keep backups in .blend copy.
for ob in list(scene.objects):
 n=ob.name
 remove=n.startswith(('Cliff_Ledged_Slab','Eroded_Vertical_Buttress','West_Island_Sedimentary','Granite_Hairline','Trail_Edge_Grass'))
 remove=remove or (n.startswith('Pine_') and int(n.split('_')[1])<4)
 remove=remove or (n.startswith('Granite_Outcrop_') and int(n.split('_')[2])<8)
 remove=remove or n in ['West_Eroded_Walking_Trail','Cliff_Trailing_Leaves','Exposed_Cliff_Rootlets']
 if remove:bpy.data.objects.remove(ob,do_unlink=True)

# Lower the regular horizontal band emphasis on the underlying sea cliff.
cliff=bpy.data.objects['West_Island_Stratified_Sea_Cliff']
cliff.data.materials.clear();cliff.data.materials.append(MAT['rock'])
for p in cliff.data.polygons:p.material_index=0;p.use_smooth=True
uv=cliff.data.uv_layers.active
for li,loop in enumerate(cliff.data.loops):
 v=cliff.data.vertices[loop.vertex_index].co;uv.data[li].uv=((v.x-v.y*.27)*.25,v.z*.25)

# Three different fracture footprints, selected deliberately for each bank section.
profiles=[
 [(-1,-.57),(-.63,-.95),(.31,-.88),(.91,-.49),(1,.2),(.58,.82),(-.23,1),(-.91,.59)],
 [(-.94,-.83),(-.22,-1),(.75,-.77),(1,-.13),(.74,.69),(.05,.94),(-.75,.65),(-1,.05)],
 [(-1,-.29),(-.65,-.93),(.14,-.98),(.85,-.61),(.96,.45),(.32,.99),(-.44,.78),(-.89,.3)]]
def broken_rock(name,pos,size,profile=0,tilt=0,moss=True):
 ring=profiles[profile%3];verts=[]
 # Bottom, broad fracture shoulder, recessed crown. Unequal levels avoid cylinders.
 for lev,(scale,yy,shift) in enumerate([(.87,-.75,-.06),(1,-.06,0),(.78,.74,.16)]):
  for j,(xx,zz) in enumerate(ring):
   dy=[-.10,.06,-.04,.12,.02,-.10,.08,-.03][(j+profile)%8]
   verts.append((pos[0]+(xx*scale+shift+tilt*yy)*size[0],pos[1]+(yy+dy)*size[1],pos[2]+zz*scale*size[2]))
 faces=[tuple(reversed(range(8))),tuple(range(16,24))]
 for k in range(2):
  for j in range(8):faces.append((k*8+j,k*8+(j+1)%8,(k+1)*8+(j+1)%8,(k+1)*8+j))
 ob=mesh('Sample_'+name,verts,faces,['rock'],SAMPLE,uv_scale=.25)
 bevel(ob,min(.10,size[0]*.09),2)
 # Plane-weighted normals preserve the fracture planes without triangular speckle.
 bpy.context.view_layer.objects.active=ob;ob.select_set(True)
 mod=ob.modifiers.new('Weighted fracture normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=35
 bpy.ops.object.modifier_apply(modifier=mod.name);ob.select_set(False)
 if moss:
  # A lopsided shallow turf cap, with several exposed stone edges.
  top=[Vector(v) for v in verts[16:24]];center=sum(top,Vector())/8
  cap=[]
  for j,v in enumerate(top):
   q=center.lerp(v,[.62,.83,.90,.58,.4,.67,.84,.78][j]);q.y+=.025;cap.append(q)
  mesh('Sample_'+name+'_Moss',cap,[tuple(range(8))],['moss'],SAMPLE,uv_scale=.25)
 return ob

# A continuous bank assembled from unequal interlocking jointed masses.
bank=[(-17.7,1.85,1.25,1.65,.65,0),(-15.55,2.5,1.33,2.3,.73,1),(-13.1,2.96,1.47,1.9,.67,2),
 (-10.65,3.35,1.32,2.35,.76,1),(-8.35,3.6,1.39,1.78,.68,0),(-5.85,3.65,1.62,2.15,.75,2),
 (-3.05,3.38,1.25,1.65,.64,1),(-.82,2.97,1.18,1.96,.70,0),(1.35,2.42,1.1,1.72,.68,2),(3.13,1.75,.93,1.5,.62,1)]
for i,(x,z,sx,sy,sz,p) in enumerate(bank):
 y=height(x,z)-sy*.71-.14
 broken_rock('Coastal_Joint_%02d'%i,(x,y,z),(sx,sy,sz),p,(-.12,.17,-.06)[i%3])
 # Embedded lower wedge, offset rather than stacked evenly.
 if i in [1,3,4,6,8]:broken_rock('Tidal_Buttress_%02d'%i,(x+.55,WATER+1.0,z+.14),(sx*.66,1.35,sz*.9),(p+1)%3,-.18,False)

# Four deliberately composed outcrop groups behind the path.
for name,x,z,sx,sy,sz,p,t in [
 ('Split_Monolith',-5.05,-2.35,1.38,1.65,1.04,1,-.24),
 ('Split_Fallen_Slab',-3.43,-2.0,.98,.72,.77,2,.28),
 ('Split_Footstone',-6.26,-1.65,.64,.45,.54,0,.07),
 ('West_Shelf',-12.8,-2.25,1.6,1.02,1.02,0,.25),
 ('West_Upright',-14.1,-2.66,.76,1.5,.72,2,-.1),
 ('Pine_Footrock',-8.65,-2.88,.93,.73,.67,1,.2),
 ('Bridgehead_Stone',1.02,-1.32,1.04,1.04,.81,2,-.22),
 ('Bridgehead_Fallen',2.45,-.96,.59,.48,.54,0,.20)]:
 broken_rock(name,(x,height(x,z)+sy*.38,z),(sx,sy,sz),p,t)

# Trail: uneven shoulders and exposed bedrock patches, still matching the walk height.
v=[];f=[]
for j in range(116):
 x=-18.3+j*22.8/115;w=.53+.09*math.sin(x*1.35)+.035*math.sin(x*4.1)
 for s in [-1,1]:
  z=path_z(x)+s*w;v.append((x,height(x,z)+.048,z))
 if j:f.append(((j-1)*2,j*2,j*2+1,(j-1)*2+1))
trail=mesh('Sample_Eroded_Trail',v,f,['path'],SAMPLE,smooth=True,uv_scale=.25)
for i,(x,z,sx,sz) in enumerate([(-9.9,.12,.45,.24),(-8.9,.20,.32,.19),(-4.2,.54,.40,.27),(2.4,.3,.32,.25),(3.1,.28,.46,.35)]):
 broken_rock('Trail_Exposed_Stone_%02d'%i,(x,height(x,z)-.065,z),(sx,.11,sz),i%3,0,False)

def card(name,center,w,h,mat,angle=0,roll=0):
 # Slightly bowed 3D leaf spray; silhouettes and interior detail come from pixel art.
 verts=[];uvs=[];faces=[]
 for j in range(3):
  for i in range(5):
   u=i/4;v=j/2;xx=(u-.5)*w;yy=(v-.5)*h
   xx,yy=xx*math.cos(roll)-yy*math.sin(roll),xx*math.sin(roll)+yy*math.cos(roll)
   dz=-yy*.24+math.sin(u*math.pi)*.10*w
   verts.append((center[0]+xx*math.cos(angle)+dz*math.sin(angle),center[1]+yy,center[2]-xx*math.sin(angle)+dz*math.cos(angle)))
   uvs.append((u,v))
 for j in range(2):
  for i in range(4):
   a=j*5+i;faces.append((a,a+1,a+6,a+5))
 ob=mesh('Sample_'+name,verts,faces,[mat],SAMPLE,smooth=True)
 uv=ob.data.uv_layers.active
 for li,loop in enumerate(ob.data.loops):uv.data[li].uv=uvs[loop.vertex_index]
 return ob

def coastal_pine(name,x,z,s=1,mirror=1):
 y=height(x,z)
 def pt(v):return Vector((x+v[0]*s*mirror,y+v[1]*s,z+v[2]*s))
 wood=Batch()
 trunk=[(0,0,0),(-.19,.62,.05),(-.28,1.37,.02),(-.12,2.2,.12),(.27,3.0,.06),(.47,3.75,.1),(.39,4.42,.03),(.58,4.95,0)]
 tube(wood,[pt(v) for v in trunk],[r*s for r in [.32,.25,.21,.18,.15,.12,.075,.025]],12)
 branches=[([(-.16,1.95,.1),(-.72,2.32,.1),(-1.43,2.5,.0),(-2.03,2.83,-.03)],[.15,.10,.065,.018]),
 ([(.10,2.65,.06),(.83,2.59,.09),(1.49,2.94,.04),(2.10,3.2,-.12)],[.14,.10,.07,.018]),
 ([(.38,3.52,.1),(-.22,3.63,-.06),(-.85,3.99,-.05),(-1.44,4.12,.07)],[.11,.075,.045,.01]),
 ([(.42,4.12,.05),(1.13,4.18,-.01),(1.64,4.53,-.05)],[.08,.05,.015]),
 ([(.42,3.7,.1),(.34,3.43,.65),(.03,3.27,1.02)],[.09,.05,.015]),
 ([(-.26,1.2,.03),(-.67,1.56,-.02),(-.89,1.93,-.04)],[.09,.045,.004])]
 for pts,r in branches:tube(wood,[pt(v) for v in pts],[q*s for q in r],9)
 for pts in [[(0,.38,0),(-.50,.13,.25),(-1.03,.01,.44)],[(.02,.32,.03),(.52,.10,.34),(.95,-.03,.51)],[(0,.23,-.04),(.15,.08,-.52),(.39,0,-.89)]]:
  points=[pt(v) for v in pts];points[-1].y=height(points[-1].x,points[-1].z)+.04;tube(wood,points,[.18*s,.10*s,.012],10)
 ob=wood.finish('Sample_'+name+'_Rooted_Trunk',['bark'],SAMPLE,True)
 # Texture around bark uses horizontal distance and elevation, no per-needle geometry.
 uv=ob.data.uv_layers.active
 for li,loop in enumerate(ob.data.loops):
  co=ob.data.vertices[loop.vertex_index].co;uv.data[li].uv=((co.x+co.y)*.7,co.z*.30)
 crowns=[(-1.70,2.98,.05,2.70,1.38,-.06),(.1,3.32,-.30,2.18,1.25,.05),(1.77,3.39,-.12,2.8,1.45,.02),
 (-1.07,4.21,.02,2.54,1.32,-.08),(.41,4.60,-.30,2.45,1.32,.02),(1.42,4.62,-.02,2.17,1.22,.08),
 (.52,5.06,.02,2.48,1.32,-.07),(.02,3.45,.86,2.20,1.22,.08)]
 for i,(cx,cy,cz,w,h,roll) in enumerate(crowns):
  card(name+'_Leaves_%02d'%i,pt((cx,cy,cz)),w*s,h*s,'PX_Pine_A' if i%2 else 'PX_Pine_B',angle=.1*mirror,roll=roll*mirror)

coastal_pine('Hero_Pine',-10.35,-2.65,1.06,1)
coastal_pine('Cliff_Pine',-16.2,-2.45,.91,-1)
coastal_pine('Bridge_Pine',-.72,-2.18,.83,-1)
# Background younger tree establishes depth without repeating the hero silhouette.
coastal_pine('Rear_Pine',-7.6,-4.15,.69,-1)

# Art-directed vegetation groupings at roots, rock feet and uneven trail shoulders.
groups=[(-15.3,-1.2,1.05),(-13.7,-1.0,.9),(-11.3,-1.1,1.1),(-9.65,-1.2,.85),(-8.7,-.9,.65),
 (-6.2,-1.05,.9),(-4.6,-1.0,1.05),(-3.45,-.5,.65),(-1.7,-.6,.8),(1.4,-.54,.7),
 (-16,1.28,.8),(-13.3,1.83,1.0),(-10.9,2.15,1.2),(-8.3,2.4,.9),(-5.6,2.65,1.1),(-2.2,2.3,.9),(1.2,1.62,.75)]
for i,(x,z,s) in enumerate(groups):
 y=height(x,z)+.04
 card('Fern_Leaves_%02d'%i,(x,y+.36*s,z),1.45*s,.96*s,'PX_Fern',angle=(i%3-1)*.23)
 for j,(dx,dz,k) in enumerate([(-.52,.06,.68),(.45,-.12,.8),(.15,.28,.6)]):
  xx=x+dx*s;zz=z+dz*s;hh=height(xx,zz)
  card('Grass_Leaves_%02d_%d'%(i,j),(xx,hh+.24*k,zz),.88*k,.72*k,'PX_Grass',angle=(j-1)*.22)

# Broader turf tufts along selected shoulder stretches, leaving some bare soil.
for i,x in enumerate([-17.4,-16.7,-15.6,-14.5,-12.5,-11.9,-10.3,-9.1,-7.9,-6.4,-5.1,-3.3,-2.8,-1.1,.25,1.7,3.1]):
 for side in [-1,1]:
  z=path_z(x)+side*(.61+.08*math.sin(x));y=height(x,z)
  card('Trail_Grass_Leaves_%02d_%d'%(i,side),(x,y+.20,z),.79,.56,'PX_Grass',roll=.07*side)

# Frame the lower corners with foliage at a genuinely nearer distance.
for i,(x,z,y,w) in enumerate([(-15.5,6.8,.6,3.8),(-13.4,7.2,.25,3.1),(3.7,6.2,-.2,3.4)]):
 card('Foreground_Fern_Leaves_%02d'%i,(x,y,z),w,w*.67,'PX_Fern',roll=(-.16 if i<2 else .18))

# Bridgehead joins: weathered end beam, stone footing and asymmetric worn approach.
for i,(x,z) in enumerate([(3.9,-.72),(3.85,1.16)]):
 broken_rock('Bridge_Anchor_%d'%i,(x,height(x,z)-.12,z),(.48,.43,.41),i,0,False)
beam=Batch();tube(beam,[(4.18,bridge_y(4.18)-.03,-.9),(4.18,bridge_y(4.18)-.03,1.37)],[.11,.10],8)
beam.finish('Sample_Bridge_Threshold_Beam',['wood'],SAMPLE)
# Align the board grain with their long direction and avoid the old cross-grain noise.
for ob in COL['07_Bridge'].objects:
 if ob.name.startswith('Bridge_Plank_') and 'Grooves' not in ob.name:
  idx=int(ob.name.split('_')[-1]);uv=ob.data.uv_layers.active
  for li,loop in enumerate(ob.data.loops):
   co=ob.data.vertices[loop.vertex_index].co;uv.data[li].uv=((co.x-(4.15+idx*10.5/38))/.27+.5,-co.y*.5)

# Fullscreen postprocess surface is also an imported Blender mesh, never a Godot QuadMesh.
mesh('HD2D_Lens_Surface',[(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)],[(0,1,2,3)],['path'],SAMPLE)
save()
print('Sample assets authored: jointed coastal rocks, four asymmetrical rooted pines, pixel leaf sprays, trail, bridge threshold, depth lens surface.')
