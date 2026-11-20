"""Fresh cape study, executed ONLY inside Blender via blender-mcp.

No prior cape mesh, material, dimensions, layout or author script is loaded.
Design coordinates below are authored for this sample from a 1.8 m human scale.
"""
import bpy, bmesh, math, random, json
from pathlib import Path
from mathutils import Vector

ROOT = Path('D:/自己做着玩的/孤屿霜尘')
OUT = ROOT / 'assets/fresh_pixel_cape'
REVIEW = ROOT / 'artifacts/fresh-pixel-cape-review'
OUT.mkdir(parents=True, exist_ok=True)
REVIEW.mkdir(parents=True, exist_ok=True)
SCENE_NAME = 'Fresh_Pixel_Cape'

if SCENE_NAME in bpy.data.scenes:
    raise RuntimeError('Fresh scene already exists; use an explicit revision script.')
scene = bpy.data.scenes.new(SCENE_NAME)
bpy.context.window.scene = scene
scene.unit_settings.system = 'METRIC'
scene['provenance'] = 'Empty scene; authored through Blender MCP. No imported geometry.'
scene['revision'] = 'fresh-cape-color-study-1'
scene['reference_basis'] = 't3ssel8r modeling and rendering study; recent-reference/README.md'
scene['scope'] = 'New cape, stairs, grass, bamboo, shore and water sample; external 2D hero only in Godot.'
rng = random.Random(251120)

def collection(name):
    c = bpy.data.collections.new('Fresh_' + name)
    scene.collection.children.link(c)
    return c

land = collection('01_Landform')
rockcol = collection('02_Rock_Faces')
stepscol = collection('03_Stairway')
green = collection('04_Grass')
bamboo = collection('05_Bamboo')
shore = collection('06_Shore')
stage = collection('90_Stage')

def mat(name, hex_color):
    h=hex_color.lstrip('#')
    rgb=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    # Store sRGB color in metadata, linear shader albedo for glTF export.
    linear=[v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    m=bpy.data.materials.new('Fresh_'+name)
    m.use_nodes=True
    m.diffuse_color=(*linear,1)
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*linear,1)
    bs.inputs['Roughness'].default_value=.94
    m['srgb']=hex_color
    return m

rockm=[mat('Rock_Base','899587'),mat('Rock_Pale','a3ad99'),mat('Rock_Cool','697f7b'),mat('Rock_Dark','526b69')]
grassm=[mat('Grass_Main','778b4b'),mat('Grass_Light','91a05a'),mat('Grass_Shade','556f44')]
soilmat=mat('Earth_Bank','79785b')
pathmat=mat('Path','aca181')
stepsm=[mat('Step','a6ab94'),mat('Step_Variant','959e8d')]
stemm=[mat('Bamboo_Stem','637b51'),mat('Bamboo_Node','93a475')]
leafm=[mat('Bamboo_Leaf','4a704e'),mat('Bamboo_Leaf_Light','64865a'),mat('Bamboo_Leaf_Dark','375e49')]
sandmat=mat('Shore_Silt','b6b190')
watermat=mat('Water','427f80')

def mesh(name, verts, faces, coll, materials, indices=None):
    data=bpy.data.meshes.new(name+'_mesh')
    data.from_pydata(verts,[],faces); data.update()
    ob=bpy.data.objects.new(name,data); coll.objects.link(ob)
    for m in materials: data.materials.append(m)
    if indices:
        for p,ix in zip(data.polygons,indices): p.material_index=ix
    bm=bmesh.new(); bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(data); bm.free()
    uv=data.uv_layers.new(name='UVMap')
    for p in data.polygons:
        normal=p.normal
        axes=(0,1) if abs(normal.z)>.55 else ((0,2) if abs(normal.y)>abs(normal.x) else (1,2))
        for li in p.loop_indices:
            co=data.vertices[data.loops[li].vertex_index].co
            uv.data[li].uv=(co[axes[0]]*.22,co[axes[1]]*.22)
    ob['authored_from']='empty Blender scene, fresh coordinate design'
    return ob

def prism(name, poly, bottom, top, coll, materials):
    n=len(poly)
    verts=[(x,y,bottom) for x,y in poly]+[(x,y,top) for x,y in poly]
    faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,verts,faces,coll,materials)

def active(ob):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True); bpy.context.view_layer.objects.active=ob

# A broad terrace with an asymmetric projecting end; top height is independent
# of the shoreline envelope. The front recess is reserved for the new stairway.
outline=[(-10.6,-3.1),(-7.0,-3.45),(-4.3,-3.15),(-2.15,-2.85),
         (-1.0,-2.5),(-.75,-1.15),(1.6,-.85),(3.6,-.95),(5.05,.35),
         (5.3,2.15),(3.1,3.65),(-.6,4.05),(-5.1,3.65),(-10.6,2.7)]
n=len(outline)
bottom=[(x*1.025-.12,y*1.07,-.65) for x,y in outline]
mid=[(x+.14*math.sin(i*1.9),y-.16*math.cos(i*1.4),1.65+.2*math.sin(i)) for i,(x,y) in enumerate(outline)]
upper=[(x,y,2.96+.05*math.sin(i*1.5)) for i,(x,y) in enumerate(outline)]
verts=bottom+mid+upper
faces=[tuple(reversed(range(n)))]
for ring in range(2):
    for i in range(n): faces.append((ring*n+i,ring*n+(i+1)%n,(ring+1)*n+(i+1)%n,(ring+1)*n+i))
faces.append(tuple(range(n*2,n*3)))
core=mesh('Cape_Continuous_Core',verts,faces,land,[rockm[2]])
bank=prism('Terrace_Earth_Thickness',outline,2.87,3.10,land,[soilmat])
top=prism('Terrace_Grass_Surface',outline,3.08,3.13,green,[grassm[0]])

# Each major face has its own authored footprint and upper fracture profile.
# Narrow bevels are edge chips; large-scale variation is in the control mesh.
def stone(name,foot,low,high,lean=(0,0),phase=0,coll=rockcol):
    n=len(foot)
    cx=sum(x for x,y in foot)/n;cy=sum(y for x,y in foot)/n
    vs=[]
    for i,(x,y) in enumerate(foot):vs.append((x,y,low-.08*math.cos(i*1.1+phase)))
    for i,(x,y) in enumerate(foot):
        f=.92+.09*math.sin(i*1.6+phase)
        vs.append((cx+(x-cx)*f+lean[0],cy+(y-cy)*f+lean[1],high+.16*math.sin(i*1.8+phase)))
    vs.append((cx+lean[0]-.15,cy+lean[1]+.12,high+.15))
    fs=[tuple(reversed(range(n)))]
    for i in range(n):
        fs.append((i,(i+1)%n,(i+1)%n+n,i+n))
        fs.append((i+n,(i+1)%n+n,n*2))
    ob=mesh(name,vs,fs,coll,rockm)
    active(ob)
    bevel=ob.modifiers.new('Small broken arrises','BEVEL');bevel.width=.045;bevel.segments=1
    bevel.affect='EDGES';bevel.angle_limit=.68
    for p in ob.data.polygons:
        p.material_index=1 if p.normal.z>.45 else (2 if p.normal.y>.2 else 0)
    return ob

stone('West_Buried_Long_Face',[(-10.8,-3),(-8.9,-3.7),(-6.8,-3.4),(-6.4,-2.5),(-8.5,-2.15),(-10.7,-2.2)],-.7,2.73,(.16,.08),.4)
stone('West_Lower_Fracture',[(-8.4,-3.3),(-6.7,-3.85),(-5,-3.65),(-4.8,-2.7),(-6.1,-2.5),(-7.8,-2.7)],-.75,1.50,(-.16,0),1.8)
stone('Central_Upper_Overhang',[(-6.5,-3.1),(-4.8,-3.46),(-3.45,-3.22),(-3.05,-2.5),(-4.5,-2.1),(-6.3,-2.4)],1.25,2.93,(.10,-.20),2.6)
stone('Central_Deep_Face',[(-4.7,-3.26),(-3,-3.56),(-1.8,-2.9),(-1.5,-2.0),(-3,-1.9),(-4.7,-2.4)],-.72,2.69,(-.18,.05),.9)
stone('Cape_End_Tall_Face',[(3.3,-.98),(4.9,-.6),(5.55,.55),(5.35,2.4),(4.6,2.85),(3.8,1.6)],-.7,3.05,(-.15,.04),1.4)
stone('Cape_End_Low_Toe',[(4.8,-.6),(6.15,-.2),(6.55,.95),(5.7,1.8),(4.8,1.1)],-.65,1.10,(.0,.15),3.0)
stone('Upper_Terrace_Exposed_Slab',[(1.8,1.35),(3.1,1.1),(4.0,1.65),(3.7,2.6),(2.45,2.75),(1.6,2.1)],2.90,3.50,(-.12,0),2.2)
stone('Back_Bamboo_Buried_Rock',[(-6.3,2.25),(-4.8,1.8),(-3.65,2.25),(-3.85,3.15),(-5.65,3.5)],2.9,3.70,(0,.1),.2)

# Two short runs separated by a full landing. Every tread is backed by a solid
# wedge; the lower flight sits on an interlocking coastal rock apron.
step_records=[]
def stair_run(name,start,direction,count,run,rise,width,start_h):
    d=Vector((direction[0],direction[1]));d.normalize();p=Vector((-d.y,d.x))
    s=Vector(start)
    # Continuous solid volume below the entire staircase.
    end=s+d*(count*run)
    corners=[s-p*width*.53,s+p*width*.53,end+p*width*.53,end-p*width*.53]
    h_end=start_h-count*rise-.08
    vs=[(c.x,c.y,-.4) for c in corners]+[(corners[0].x,corners[0].y,start_h-.10),(corners[1].x,corners[1].y,start_h-.10),(corners[2].x,corners[2].y,h_end),(corners[3].x,corners[3].y,h_end)]
    mesh(name+'_Buried_Support',vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],stepscol,[rockm[2]])
    for i in range(count):
        center=s+d*((i+.5)*run)
        z=start_h-i*rise
        # The front arris alternates a few cm, never changing the overall walk rhythm.
        local=[(-run*.51,-width*.50),(-run*.55,width*.43),(-run*.39,width*.51),
               (run*.52,width*.47),(run*.56,width*.22),(run*.50,-width*.49),(run*.10,-width*.53)]
        poly=[tuple(center+d*a+p*b) for a,b in local]
        ob=prism(name+'_Tread_%02d'%i,poly,z-rise-.10,z,stepscol,[stepsm[i%2]])
        active(ob);m=ob.modifiers.new('Worn stone lip','BEVEL');m.width=.024;m.segments=1
        step_records.append({'name':ob.name,'center':[center.x,center.y,z],'width':width,'run':run})
    return end

prism('Upper_Entry_Landing',[(-1.75,-2.66),(-.5,-2.62),(-.35,-1.25),(-1.5,-1.15)],2.62,3.12,stepscol,stepsm[:1])
end=stair_run('Upper_Flight',(-.6,-2.0),(1,-.09),5,.55,.245,1.48,3.08)
landing=[(end.x-.12,end.y-.84),(end.x+.95,end.y-.90),(end.x+1.12,end.y+.53),(end.x+.03,end.y+.74)]
prism('Turn_Landing',landing,.72,1.855,stepscol,[stepsm[0]])
stair_run('Lower_Flight',(end.x+.92,end.y-.20),(1,-.48),6,.56,.245,1.42,1.61)
stone('Lower_Stair_Rock_Apron',[(3.5,-3.5),(4.9,-4.1),(6.7,-4.65),(7.25,-3.7),(6.4,-2.9),(5.0,-2.65),(4.2,-2.8)],-.7,.38,(0,0),2.0,shore)
stone('Landing_Outer_Buttress',[(1.45,-3.1),(2.8,-3.34),(3.25,-2.95),(3.1,-2.3),(1.8,-2.3)],-.55,1.42,(-.12,.06),.5,shore)
prism('Lower_Shore_Shelf',[(4.6,-4.45),(6.5,-5.1),(8,-4.4),(8.4,-3.3),(7.3,-2.4),(5.4,-2.8)],-.55,.12,shore,[sandmat])

def ribbon(name,points,width,z,coll,material):
    vs=[]
    for i,p in enumerate(points):
        prev=Vector(points[max(0,i-1)]);nxt=Vector(points[min(len(points)-1,i+1)])
        delta=(nxt-prev).normalized();side=Vector((-delta.y,delta.x))
        for s in (-1,1):
            q=Vector(p)+side*width*.5*s
            vs.append((q.x,q.y,z+.012*math.sin(i*1.6)))
    return mesh(name,vs,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(points)-1)],coll,[material])

ribbon('Quiet_Earth_Path',[(-11,-.60),(-8.7,-.48),(-6.6,-.64),(-4.7,-.83),(-3,-1.25),(-1.4,-1.82)],1.35,3.153,land,pathmat)

# Small patches are grouped; a few strokes articulate the grass edge while
# leaving most of the terrace as a calm color field.
def tuft_mesh():
    vs=[];fs=[];colors=[]
    for i in range(8):
        angle=i*2.399
        x=.16*math.cos(angle);y=.12*math.sin(angle)
        h=.22+.19*((i*7)%5)/5;w=.035+.025*(i%3)
        d=Vector((math.cos(angle),math.sin(angle),0));side=Vector((-d.y,d.x,0))
        root=Vector((x,y,0));k=len(vs)
        pts=[root-side*w,root+side*w,root+d*.06+Vector((0,0,h*.58))+side*w*.45,root+d*.20+Vector((0,0,h)),root+d*.06+Vector((0,0,h*.58))-side*w*.45]
        vs.extend([tuple(p) for p in pts]);fs.append(tuple(range(k,k+5)))
    return vs,fs

tv,tf=tuft_mesh()
grass_positions=[]
for i in range(84):
    t=i/83;x=-10.4+t*9.0
    y=-2.75+.45*math.sin(t*2.8)
    grass_positions.append((x+rng.uniform(-.14,.14),y+rng.uniform(-.18,.18),3.15))
for i in range(80):
    x=rng.uniform(-10,3.9);y=rng.uniform(.50,3.15)
    if -6.5<x<-3.5 and y>1.7:continue
    if 1.5<x<4 and y>1:continue
    grass_positions.append((x,y,3.15))
for i in range(20):
    x=rng.uniform(-8,-2);y=-.6+.2*math.sin(x)+rng.choice([-1,1])*.92
    grass_positions.append((x,y,3.15))
for i,point in enumerate(grass_positions):
    ob=mesh('Grass_Clump_%03d'%i,tv,tf,green,[grassm[(i//9)%3]])
    ob.location=point;ob.rotation_euler.z=rng.uniform(0,6.28)
    s=rng.uniform(.65,1.35);ob.scale=(s,s,s)
    ob['wind']='root anchored grass'

# Bamboo is authored as stems and elongated leaf fans, not borrowed tree blobs.
def rod(name,a,b,r0,r1,coll,material,sides=7):
    a=Vector(a);b=Vector(b);d=(b-a).normalized()
    u=d.cross(Vector((0,0,1)))
    if u.length<.1:u=d.cross(Vector((0,1,0)))
    u.normalize();v=d.cross(u)
    pts=[]
    for c,r in [(a,r0),(b,r1)]:
        for i in range(sides):pts.append(tuple(c+r*(u*math.cos(i*math.tau/sides)+v*math.sin(i*math.tau/sides))))
    faces=[tuple(reversed(range(sides))),tuple(range(sides,sides*2))]+[(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)]
    return mesh(name,pts,faces,coll,[material])

def leaf_fan(name,origin,heading,scale):
    origin=Vector(origin);vs=[];fs=[];ix=[]
    for i in range(9):
        spread=(i-4)*.22;angle=heading+spread
        d=Vector((math.cos(angle),math.sin(angle),-.25-abs(spread)*.12))
        side=Vector((-d.y,d.x,0));length=scale*(.65+.3*math.sin(i*1.8)**2)
        base=origin+Vector((math.cos(heading),math.sin(heading),.05))*scale*(i%3)*.18
        mid=base+d*length*.48+Vector((0,0,.08));end=base+d*length
        width=length*.075;k=len(vs)
        vs.extend([tuple(base),tuple(mid-side*width),tuple(mid+Vector((0,0,.025))),tuple(end),tuple(mid+side*width)])
        fs.extend([(k,k+1,k+2),(k+1,k+3,k+2),(k+2,k+3,k+4),(k,k+2,k+4)])
        ix.extend([i%3]*4)
    ob=mesh(name,vs,fs,bamboo,leafm,ix)
    ob['wind']='leaf fan'
    # Whole-fan lighting, avoiding tiny independent normal wedges.
    normals=[]
    for p in ob.data.polygons:
        for li in p.loop_indices:normals.append((-.15,-.4,.90))
    ob.data.normals_split_custom_set(normals)
    return ob

stems=[(-10.0,1.0,5.2,.32),(-9.4,2.4,5.8,-.22),(-8.8,1.2,4.9,.15),
       (-8.2,2.8,5.9,.30),(-7.8,1.4,5.4,-.18),(-7.0,2.7,5.0,.17),
       (-6.6,1.4,4.4,-.25),(-5.8,3.0,5.45,.15),(-4.8,3.25,4.7,-.22),
       (-3.8,3.2,4.1,.14),(-2.6,3.3,3.8,-.17),(-1.7,3.3,4.25,.24)]
for si,(x,y,h,lean) in enumerate(stems):
    base=Vector((x,y,3.12));tip=base+Vector((lean,.25,h))
    rod('Bamboo_%02d_Stem'%si,base,tip,.065,.025,bamboo,stemm[0])
    for j in range(1,int(h/.6)):
        t=j*.6/h;c=base+(tip-base)*t
        rod('Bamboo_%02d_Node_%02d'%(si,j),c-Vector((0,0,.016)),c+Vector((0,0,.016)),.066-.035*t,.066-.035*t,bamboo,stemm[1])
    for j in range(3):
        t=.57+j*.15;c=base+(tip-base)*t
        angle=(si%3)*.8+j*2.4
        end=c+Vector((math.cos(angle)*.65,math.sin(angle)*.65,.16))
        rod('Bamboo_%02d_Branch_%02d'%(si,j),c,end,.025,.007,bamboo,stemm[0],5)
        leaf_fan('Bamboo_%02d_Fan_%02d'%(si,j),end,angle,1.15+j*.12)
        leaf_fan('Bamboo_%02d_CounterFan_%02d'%(si,j),c,-angle+2.2,.88)

# Water is an authored plane. Godot only supplies its material and animation.
mesh('Sea_Surface',[(-65,-65,-.20),(65,-65,-.20),(65,65,-.20),(-65,65,-.20)],[(0,1,2,3)],shore,[watermat])

# A few discontinuous tide lines, with no geometry generated by the engine.
for i,(x,y,l) in enumerate([(-8,-4.1,1.2),(-5.9,-3.95,.65),(-2.8,-3.5,.62),(5.8,-4.7,.8),(7.4,-3.7,.55)]):
    ribbon('Tide_Edge_%02d'%i,[(x-l/2,y),(x,y-.07),(x+l/2,y+.02)],.045,-.175,shore,mat('Foam_%02d'%i,'a1c4b0'))

# Author-view camera and light, not exported as scene assets.
camera_data=bpy.data.cameras.new('Fresh_Review_Camera')
camera=bpy.data.objects.new('Fresh_Review_Camera',camera_data);stage.objects.link(camera)
camera.location=(10,-28,17);target=Vector((-1,0,3))
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.lens=45
scene.camera=camera
ld=bpy.data.lights.new('Fresh_Sun','SUN');lo=bpy.data.objects.new('Fresh_Sun',ld);stage.objects.link(lo)
ld.energy=2.4;ld.angle=.08;lo.rotation_euler=(math.radians(25),math.radians(-28),math.radians(-35))
world=bpy.data.worlds.new('Fresh_Sea_Air');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.28,.42,.43,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.5;scene.world=world
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.view_settings.view_transform='Standard'
scene.render.image_settings.file_format='PNG'

model_objects=[o for c in [land,rockcol,stepscol,green,bamboo,shore] for o in c.objects]
for ob in model_objects:
    ob['fresh_sample']=True
    if ob.type=='MESH':
        # Per-vertex height channel for future wind; geometry remains editable.
        attr=ob.data.color_attributes.new(name='Wind',type='BYTE_COLOR',domain='CORNER')
        for p in ob.data.polygons:
            for li in p.loop_indices:
                z=ob.data.vertices[ob.data.loops[li].vertex_index].co.z
                w=max(0,min(1,z/.5)) if ob.name.startswith('Grass_') else max(0,min(1,(z-3.2)/5.0)) if ob.name.startswith('Bamboo_') else 0
                attr.data[li].color=(1,1,1,w)
active(top)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'fresh_pixel_cape.blend'))
bpy.ops.object.select_all(action='DESELECT')
for ob in model_objects:ob.select_set(True)
bpy.context.view_layer.objects.active=top
bpy.ops.export_scene.gltf(filepath=str(OUT/'fresh_pixel_cape.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT')
(OUT/'design.json').write_text(json.dumps({'revision':scene['revision'],'source':'empty Blender scene via MCP','unit':'metre','top_height':3.13,'hero_blender':[-2.7,-1.15,3.16],'camera_blender':list(camera.location),'camera_target':list(target),'stairs':step_records,'mesh_objects':len(model_objects),'materials':len({m.name for o in model_objects for m in o.data.materials}),'imported_geometry':[]},indent=2),encoding='utf-8')
print(json.dumps({'saved':str(OUT),'objects':len(model_objects),'revision':scene['revision']}))
