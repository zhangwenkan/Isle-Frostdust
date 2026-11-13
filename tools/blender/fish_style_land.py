"""Author the island in the live Blender session through Blender MCP.

Use the supplied reference trees/rocks with their matched UVs and material maps.
The continuous island terrain, slope painting and composition are authored here.
No Godot or external process creates mesh geometry.
"""
import bpy,bmesh,math,json,random
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
OUT=ROOT/'assets/island_blender'
REF=Path('D:/steam/steamapps/common/I Just Wanted to Fish Demo/analysis/exported_all')
MAPS=OUT/'fish_reference'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
WATER=-2.1

def G(p):return Vector((p[0],-p[2],p[1]))
def h(x,z):
 if x>10:return 1.15+math.sin(x*.37)*.18+max(0,-z)*.16
 return 1.65+(4.5-x)*.127+math.sin(x*.39)*.16+math.cos(z*1.3+x*.21)*.10+max(0,-z-.3)*.23
def path_z(x):return .25 if 4.5<=x<=14 else .4+math.sin(x*.25)*.44
def smooth(a,b,t):
 t=max(0,min(1,(t-a)/(b-a)));return t*t*(3-2*t)
def linear(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
def color(s):return tuple(linear(int(s[i:i+2],16)/255) for i in [0,2,4])+(1,)
def blend(a,b,t):return tuple(x*(1-t)+y*t for x,y in zip(a,b))

# Retire the previous trees, isolated cliff blocks and scattered surface cards.
# Keep the bridge, sea, birds, lens and character-contact asset.
keep=[];retired=[]
for ob in list(scene.objects):
 if ob.type!='MESH':continue
 n=ob.name
 if n in ['Open_Sea','HD2D_Lens_Surface','ContactShadow'] or n.startswith(('Bridge_','Seabird_')):
  keep.append(n);continue
 if any(c.name.startswith('90_') for c in ob.users_collection):continue
 retired.append(n);bpy.data.objects.remove(ob,do_unlink=True)
collection=bpy.data.collections.get('14_Fish_Landscape') or bpy.data.collections.new('14_Fish_Landscape')
if collection.name not in scene.collection.children:scene.collection.children.link(collection)
def link(ob):
 for c in list(ob.users_collection):c.objects.unlink(ob)
 collection.objects.link(ob)

def material(name,hexcolor='ffffff',albedo=None,normal=None,leaf=False,vertex=False):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
 m.node_tree.nodes.clear();n=m.node_tree.nodes
 p=n.new('ShaderNodeBsdfPrincipled');o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(p.outputs['BSDF'],o.inputs['Surface'])
 p.inputs['Base Color'].default_value=color(hexcolor);p.inputs['Roughness'].default_value=.9
 m.diffuse_color=color(hexcolor)
 if albedo:
  image=bpy.data.images.load(str(MAPS/albedo),check_existing=True);image.pack()
  t=n.new('ShaderNodeTexImage');t.image=image;t.interpolation='Linear';t.extension='EXTEND'
  m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
  if leaf:
   m.node_tree.links.new(t.outputs['Alpha'],p.inputs['Alpha']);m.surface_render_method='DITHERED'
 if normal:
  image=bpy.data.images.load(str(MAPS/normal),check_existing=True);image.colorspace_settings.name='Non-Color';image.pack()
  t=n.new('ShaderNodeTexImage');t.image=image;t.interpolation='Linear'
  nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.55
  m.node_tree.links.new(t.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],p.inputs['Normal'])
 if vertex:
  v=n.new('ShaderNodeVertexColor');v.layer_name='LandscapeColor';m.node_tree.links.new(v.outputs['Color'],p.inputs['Base Color'])
 m['reference']='I Just Wanted to Fish Demo / user-supplied local study'
 return m
ground_mat=material('Fish_Terrain_Painted',vertex=True)
cliff_mat=material('Fish_Bedrock_Painted',vertex=True)
leaf_mat=material('Fish_Leaves',albedo='T_Leaves_619.png',leaf=True)
flora_file=next(MAPS.glob('T_FloraAtlas_*.png')).name
flora_mat=material('Fish_Grass',albedo=flora_file,leaf=True)
tree_mats={k:material('Fish_Bark_'+k,albedo=a,normal=n) for k,a,n in [('A','T_Tree_A_Albedo_481.png','T_Tree_A_Normal_612.png'),('B','T_Tree_B_Albedo_475.png','T_Tree_B_Normal_694.png')]}
rock_mats={k:material('Fish_Rock_'+k,albedo=a,normal=n) for k,a,n in [('A','T_Rock_A_Albedo_667.png','T_Rock_A_Normal_494.png'),('B','T_Rock_B_Albedo_460.png','T_Rock_B_Normal_534.png'),('C','T_Rock_C_Albedo_564.png','T_Rock_C_Normal_401.png'),('D','T_Rock_D_Albedo_540.png','T_Rock_D_Normal_435.png')]}

def mesh(name,verts,faces,mats,indices=None,colors=None,smooth_shading=True):
 me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata([G(p) for p in verts],[],faces);me.update()
 ob=bpy.data.objects.new(name,me);collection.objects.link(ob)
 for m in mats:me.materials.append(m)
 for p in me.polygons:
  p.use_smooth=smooth_shading
  if indices:p.material_index=indices[p.index]
 if colors:
  ca=me.color_attributes.new(name='LandscapeColor',type='FLOAT_COLOR',domain='POINT')
  for i,c in enumerate(colors):ca.data[i].color=c
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 return ob

# Authored cross-sections: one continuous land mass, wider behind the trail and
# progressively narrower towards both cliff/bridge endpoints.
WEST=[(-19.05,-1.65,.9),(-18.1,-3.0,1.7),(-16,-4.8,2.5),(-13,-5.6,3.0),(-10,-6.2,3.5),(-7,-5.7,3.7),(-4,-5.0,3.45),(-1,-4.0,2.95),(2,-2.8,2.25),(4.65,-.8,1.1)]
EAST=[(14.25,-.75,1.1),(15.5,-2.8,2.35),(18,-4.2,3.2),(21,-4.8,3.8),(24,-3.5,3.1),(26.5,-.4,1.7)]
def bounds(x,east=False):
 sections=EAST if east else WEST
 for a,b in zip(sections,sections[1:]):
  if a[0]<=x<=b[0]:
   t=(x-a[0])/(b[0]-a[0]);return a[1]*(1-t)+b[1]*t,a[2]*(1-t)+b[2]*t
 return sections[0][1:] if x<sections[0][0] else sections[-1][1:]
def surface(x,z):
 y=h(x,z);pz=path_z(x)
 # Broad raised rear hills: coherent large forms, no noisy displacement.
 if z<pz-.7:
  back= max(0,1-math.exp(-(pz-z-.7)*.75))
  ridge=(1.65*math.exp(-((x+12.8)/5.3)**2)+1.0*math.exp(-((x+3)/3.5)**2)) if x<10 else .75*math.exp(-((x-21)/5)**2)
  y+=ridge*back
 if z>pz+.7:y-=.45*smooth(pz+.7,bounds(x,x>10)[1],z)
 return y

grass_low=color('5b813c');grass_high=color('78994b');grass_shade=color('57743b')
soil=color('b7a27b');trail_color=color('c5b38a');stone_top=color('a1ada2');stone_bottom=color('718b86')
for east in [False,True]:
 sec=EAST if east else WEST;n=52 if east else 100
 xs=[sec[0][0]+(sec[-1][0]-sec[0][0])*i/n for i in range(n+1)]
 verts=[];faces=[];colors=[];rows=26
 for x in xs:
  back,front=bounds(x,east);pz=path_z(x)
  # Align sample rows with the trail's actual edges, avoiding a floating ribbon.
  zs=[back+(pz-.58-back)*i/11 for i in range(12)]+[pz-.58+(1.16)*i/4 for i in range(1,5)]+[pz+.58+(front-pz-.58)*i/10 for i in range(1,11)]
  for z in zs:
   y=surface(x,z);verts.append((x,y,z))
   field=.5+.21*math.sin(x*.41+z*.51)+.16*math.cos(x*.69-z*.36)
   col=blend(grass_low,grass_high,field)
   # Broad, low-contrast brush islands break up turf without a repeated texture.
   for px,pz0,rx,rz,weight in [(-16,1.0,1.7,.8,.14),(-11,-1,2.4,.9,.12),(-7.4,2.5,2.2,.7,.18),(-3,-2.2,2.0,1.1,.12),(.6,1.4,1.7,.6,.15),(19,1.8,2.0,.9,.16)]:
    patch=math.exp(-((x-px)/rx)**4-((z-pz0)/rz)**4)*weight
    col=blend(col,grass_shade,patch)
   # Two restrained patches follow the terrain contours, not tiled surface noise.
   shade=math.exp(-((x+11.5)/3.5)**2-((z+3.7)/2)**2)*.28
   col=blend(col,grass_shade,shade)
   path_weight=1-smooth(.42,.69+math.sin(x*.75)*.04,abs(z-pz))
   col=blend(col,trail_color,path_weight*.97)
   # Exposed bedrock belongs to the rear ridge itself. It stays clear of roots.
   ridge_mask=1-smooth(back+.3,back+1.25,z)
   ridge_mask*=smooth(.6,1.8,y-h(x,z))
   col=blend(col,stone_top,ridge_mask*.75)
   colors.append(col)
 for i in range(n):
  for j in range(rows-1):
   a=i*rows+j;faces.append((a,a+rows,a+rows+1,a+1))
 # Walk the perimeter. Exact same vertices close the top and cliff shell.
 boundary=[i*rows for i in range(n+1)]+[n*rows+j for j in range(1,rows)]+[i*rows+rows-1 for i in range(n-1,-1,-1)]+list(range(rows-2,0,-1))
 indices=[0]*len(faces);center=Vector(((sec[0][0]+sec[-1][0])/2,0))
 previous=boundary
 for ring,(frac,off) in enumerate([(0.016,.04),(.055,.20),(.22,.10),(.54,.05),(.76,.44),(1.0,.95)]):
  current=[]
  for bid in boundary:
   x,top,z=verts[bid];delta=Vector((x,z))-center;delta.normalize()
   # Broad slant keeps one cliff connected rather than a necklace of blocks.
   buttress=sum(strength*max(0,1-abs((x-cx)/width)) for cx,width,strength in ([(-17.4,1.3,.90),(-12.1,1.8,1.10),(-6.5,2.0,.95),(-.8,1.5,.80)] if not east else [(18.1,1.6,.85),(23.1,1.4,.75)]))
   front_weight=smooth(0,1.0,z)
   longwave=buttress*front_weight*math.sin(frac*math.pi)+.035*math.sin(x*.55+z*.31)*math.sin(frac*math.pi)
   nx=x+delta.x*(off+longwave);nz=z+delta.y*(off+longwave)
   y=top*(1-frac)+(WATER-.65)*frac
   current.append(len(verts));verts.append((nx,y,nz))
   if ring==0:col=blend(colors[bid],soil,.48)
   elif ring==1:col=blend(stone_top,soil,.06)
   else:
    col=blend(stone_top,stone_bottom,smooth(.2,1,frac)*.65)
    col=blend(col,color('96a69a'),(.5+.5*math.sin(x*.38+z*.22))*.14)
    col=blend(col,color('bbc0af'),min(1,buttress)*front_weight*.37)
    col=blend(col,color('658780'),front_weight*(1-min(1,buttress))*.13)
   colors.append(col)
  for j in range(len(boundary)):
   faces.append((previous[j],previous[(j+1)%len(boundary)],current[(j+1)%len(boundary)],current[j]));indices.append(1)
  previous=current
 faces.append(tuple(reversed(previous)));indices.append(1)
 ob=mesh('Fish_East_Continuous_Land' if east else 'Fish_West_Continuous_Land',verts,faces,[ground_mat,cliff_mat],indices,colors)
 ob['source']='Original Blender terrain, reference regional painting/continuous-slope method'

# Import original source objects through Blender; retain authored UVs/normals.
templates={};imported_sources=[]
def import_parts(key,file):
 bpy.ops.object.select_all(action='DESELECT')
 bpy.ops.wm.obj_import(filepath=str(REF/'meshes'/file),forward_axis='NEGATIVE_Z',up_axis='Y',use_split_objects=False,use_split_groups=True)
 parts=[]
 for ob in list(bpy.context.selected_objects):
  # The importer carries axis conversion in the object matrix. Bake it before
  # composing game-space transforms to avoid double rotation.
  ob.data.transform(ob.matrix_world);ob.matrix_world=Matrix.Identity(4)
  link(ob);parts.append(ob)
 imported_sources.append(file);templates[key]=parts
 return parts
for key,file in [('A','Tree_A_3939.obj'),('B','Tree_B_5160.obj')]:
 for ob in import_parts('Tree'+key,file):
  original_name=ob.name
  ob.data.materials.clear();ob.data.materials.append(leaf_mat if '_0' in original_name else tree_mats[key])
  ob['part']='Leaves' if '_0' in original_name else 'Bark'
for key,file in [('A','Rock_A_4518.obj'),('B','Rock_B_4192.obj'),('C','Rock_C_3602.obj'),('D','Rock_D_6272.obj')]:
 for ob in import_parts('Rock'+key,file):ob.data.materials.clear();ob.data.materials.append(rock_mats[key])
for ob in import_parts('Grass','Flora_GrassTufts_3650.obj'):
 ob.data.materials.clear();ob.data.materials.append(flora_mat)
 # Imported scatter prototype has an authoring offset; anchor roots at zero.
 min_z=min(v.co.z for v in ob.data.vertices);cx=sum(v.co.x for v in ob.data.vertices)/len(ob.data.vertices);cy=sum(v.co.y for v in ob.data.vertices)/len(ob.data.vertices)
 for v in ob.data.vertices:v.co-=Vector((cx,cy,min_z))

placements=[]
def instance(kind,name,x,z,scale=1.0,angle=0,embed=0,y=None):
 if not isinstance(scale,(tuple,list)):scale=(scale,scale,scale)
 top=surface(x,z) if y is None else y
 made=[]
 for template in templates[kind]:
  ob=bpy.data.objects.new(name+'_'+template.get('part','Body'),template.data);collection.objects.link(ob)
  ob.location=G((x,top-embed,z));ob.rotation_euler.z=angle;ob.scale=(scale[0],scale[2],scale[1])
  ob['asset_role']=kind;ob['ground_contact']=(x,top,z);made.append(ob)
 placements.append({'name':name,'kind':kind,'x':x,'z':z,'ground_y':top,'embed':embed,'scale':scale})
 return made

# One family of broadleaf trees. Varied size/yaw, deliberate 4–6m rhythm,
# rear clusters and open stretches at the hero/trail and bridge landing.
for i,(key,x,z,s,a) in enumerate([
 ('A',-16.45,-2.65,.84,.35),('B',-12.5,-4.2,1.02,1.5),
 ('A',-8.4,-3.05,.94,3.1),('B',-3.2,-3.55,.96,4.5),('A',1.45,-1.7,.72,2.0),
 ('B',17.55,-2.0,.86,1.1),('A',22,-3.1,1.04,3.6),('B',24.4,-.7,.78,5.1)]):
 instance('Tree'+key,'Fish_Tree_%02d'%i,x,z,s,a,.035)

# Rocks share the source's restrained shapes and face-specific UVs. Three land
# groups use a large buried anchor + small companion, leaving clear intervals.
for i,(key,x,z,s,a,e) in enumerate([
 ('B',-17.7,-.85,1.0,.3,.32),('D',-16.55,-1.25,.48,1.2,.16),
 ('A',-11.4,-2.2,1.18,1.4,.40),('C',-10.15,-1.5,.53,3.5,.18),
 ('C',-4.75,-1.55,1.05,2.5,.36),('B',-3.65,-1.85,.48,.7,.18),
 ('D',2.5,-.8,.56,2.0,.20),('A',17.0,-1.0,.72,4.2,.25),('C',22.8,-1.2,.85,.9,.29),
 ('B',-14.8,1.7,.42,3.0,.18),('D',-8.1,2.4,.36,1.7,.14),('A',-.75,2.1,.34,2.4,.13)]):
 instance('Rock'+key,'Fish_Ground_Rock_%02d'%i,x,z,s,a,e)

# The cliff and upper ridge are continuous terrain above; don't attach separate
# boulders to vertical walls or put a boulder through a tree's root flare.

# Low tufts cluster near roots/stone shoulders; leave the broad turf calm.
r=random.Random(87)
centers=[(-17,-1.4),(-15.5,1),(-12.2,-1.8),(-10,-2.3),(-8.7,1.7),(-6.1,-1.3),(-4,-1.9),(-1,1.5),(2,-.9),(16.6,-1),(19,1.6),(22,-1.7),(24,1.2)]
for i,(cx,cz) in enumerate(centers):
 for j in range(4 if i%3 else 6):
  x=cx+r.uniform(-.65,.65);z=cz+r.uniform(-.45,.45)
  if abs(z-path_z(x))<.80:continue
  back,front=bounds(x,x>10)
  if z<back+.35 or z>front-.3:continue
  instance('Grass','Fish_Tuft_%02d_%02d'%(i,j),x,z,r.uniform(.65,1.02),r.random()*math.tau,.025)

# Reefs belong to the same rock family and cluster near the coast/bridge feet.
for i,(key,x,z,s) in enumerate([('A',-18.7,3.0,1.1),('C',-17.4,3.4,.55),('B',-9.7,5.5,1.0),('D',-8.5,5.8,.48),('C',7.8,1.8,.92),('A',10.7,-1.1,.68),('B',17.7,4.8,.8)]):
 instance('Rock'+key,'Fish_Tidal_Reef_%02d'%i,x,z,(s,s*.75,s),i*.71,.22,y=WATER)

# Delete template objects, retain shared meshes and packed material maps.
for parts in templates.values():
 for ob in parts:bpy.data.objects.remove(ob,do_unlink=True)
bpy.context.view_layer.update()
report={'source_meshes':imported_sources,'retired_objects':retired,'kept_objects':keep,'placements':placements,
 'terrain':'continuous cross-section mesh with broad vertex-painted regions; no tiled noise texture',
 'reference_tree_spacing_median':5.01,'trees':8,'water':'deferred until land review'}
(ROOT/'artifacts/fish-style-review/land-authoring.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'nameless_island.blend'))
print('Fish land stage authored:',len(collection.objects),'objects; eight unified broadleaf trees; continuous grounded land.')
