"""Reference-led shape/color revision, executed inside Blender through MCP only.
Works exclusively on Fresh_Pixel_Cape, built from an empty scene this session.
"""
import bpy,bmesh,math,random,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Fresh_Pixel_Cape'];bpy.context.window.scene=scene
assert scene['revision']=='fresh-cape-color-study-4'
rng=random.Random(90261120)
rockcol=bpy.data.collections['Fresh_02_Rock_Faces']
green=bpy.data.collections['Fresh_04_Grass']
bamboo=bpy.data.collections['Fresh_05_Bamboo']
land=bpy.data.collections['Fresh_01_Landform']
shore=bpy.data.collections['Fresh_06_Shore']
steps=bpy.data.collections['Fresh_03_Stairway']

def active(ob):
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
def color(name,h):
    mat=bpy.data.materials.get('Fresh_'+name) or bpy.data.materials.new('Fresh_'+name)
    mat.use_nodes=True;rgb=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    c=[v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    mat.diffuse_color=(*c,1);mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1)
    mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.95
    mat['srgb']='#'+h;return mat
rockm=[color('Rock_Base','9ca9a4'),color('Rock_Pale','b4bca9'),color('Rock_Cool','84969b'),color('Rock_Dark','526b74')]
grassm=[color('Grass_Main','6d9160'),color('Grass_Light','8da568'),color('Grass_Shade','537a60')]
leafm=[color('Bamboo_Leaf','4e7c68'),color('Bamboo_Leaf_Light','729576'),color('Bamboo_Leaf_Dark','3d655c')]
stemm=color('Bamboo_Stem','678a69');nodem=color('Bamboo_Node','899c70')
color('Step','b7bba7');color('Step_Variant','aab4a5');color('Path','aaa18a')
color('Earth_Bank','6f7a66');color('Shore_Silt','a6aa91')

def mesh(name,vs,fs,col,mats,ids=None):
    me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(vs,[],fs);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);col.objects.link(ob)
    for m in mats:me.materials.append(m)
    if ids:
        for f,i in zip(me.polygons,ids):f.material_index=i
    uv=me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        a,b=(0,1) if abs(p.normal.z)>.6 else (0,2)
        for li in p.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[a]*.2,v[b]*.2)
    ob['fresh_sample']=True;ob['authored_from']='new empty-scene sample, refined via Blender MCP'
    return ob

# Replace the first sample's repeated prism-like rocks with individually
# proportioned, oblique fracture beds. Polygon clipping creates real cut faces.
for ob in list(rockcol.objects):bpy.data.objects.remove(ob,do_unlink=True)
for name in ['Lower_Stair_Rock_Apron','Landing_Outer_Buttress']:
    ob=bpy.data.objects.get(name)
    if ob:bpy.data.objects.remove(ob,do_unlink=True)

def cutstone(name,center,scale,tilt,cuts,palette=0):
    bm=bmesh.new();bmesh.ops.create_cube(bm,size=2)
    # Every object receives its own authored fractures in normalized space.
    for normal,dist in cuts:
        n=Vector(normal).normalized()
        res=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
            plane_co=n*dist,plane_no=n,dist=.00001,clear_outer=True,clear_inner=False)
        boundary=[e for e in bm.edges if e.is_boundary]
        if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
    # Rotate bedding and scale before bevel: widths are actual world units.
    co,si=math.cos(tilt),math.sin(tilt)
    for v in bm.verts:
        x,y,z=v.co; x*=scale[0];y*=scale[1];z*=scale[2]
        v.co=(center[0]+x*co-z*si,center[1]+y,center[2]+x*si+z*co)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    # Small two-plane chips make arrises read without chamfering every edge equally.
    candidates=[e for e in bm.edges if len(e.link_faces)==2 and e.calc_face_angle()>.65 and e.calc_length()>.45]
    if candidates:bmesh.ops.bevel(bm,geom=candidates,offset=.055,segments=1,affect='EDGES')
    bm.normal_update();me=bpy.data.meshes.new(name+'_sculpt');bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);rockcol.objects.link(ob)
    for m in rockm:me.materials.append(m)
    for p in me.polygons:
        p.material_index=1 if p.normal.z>.65 else (2 if palette==2 else 0)
    uv=me.uv_layers.new(name='UVMap')
    for li,loop in enumerate(me.loops):
        p=me.vertices[loop.vertex_index].co;uv.data[li].uv=(p.x*.2,p.z*.2+p.y*.05)
    ob['fresh_sample']=True;ob['authored_from']='individually clipped fracture bed in new sample'
    return ob

# Slanted crown, undercut body, and wider submerged apron, with staggered seams.
cutstone('Rock_West_Crown',(-9.20,-2.71,2.54),(2.05,.90,.62),-.11,
 [((1,-1,.3),1.05),((-1,-1,.2),1.12),((.1,-.35,1),.92),((-.8,.1,-1),1.17),((-.1,-1,-.5),1.02)])
cutstone('Rock_West_Undercut',(-9.1,-2.99,1.38),(2.19,.95,.80),-.05,
 [((1,-1,.5),1.12),((-1,-1,.5),1.09),((0,-1,-.5),.88),((.1,-.3,1),1.02)],2)
cutstone('Rock_West_Tidal_Foot',(-9.1,-3.40,.22),(2.55,1.12,.76),-.07,
 [((1,-1,.2),1.08),((-1,-1,.5),1.08),((0,-.75,1),.86),((.35,0,-1),1.08)])
cutstone('Rock_Center_Long_Crown',(-5.69,-2.89,2.51),(2.1,.93,.59),.10,
 [((1,-1,.35),1.08),((-1,-1,.5),1.10),((.15,-.4,1),.92),((-.4,-1,-.2),1.04)])
cutstone('Rock_Center_Deep_Plane',(-5.70,-3.19,1.31),(1.92,.96,.88),.12,
 [((1,-1,.4),1.13),((-1,-1,.3),1.08),((-.1,-1,-.6),.93),((.7,-.2,1),1.05)],2)
cutstone('Rock_Center_Low_Bed',(-6.30,-3.57,.22),(2.48,.96,.64),.11,
 [((1,-1,.3),1.12),((-1,-1,.3),1.16),((-.1,-.7,1),.9)])
cutstone('Rock_Entry_Lifted_Shoulder',(-2.62,-2.49,2.42),(1.62,.92,.73),-.15,
 [((1,-1,.2),1.13),((-1,-1,.4),1.04),((.1,-.35,1),.87),((.3,-1,-.3),1.04)])
cutstone('Rock_Entry_Split_Front',(-2.60,-3.13,1.05),(1.48,.88,1.0),-.12,
 [((1,-1,.4),.96),((-1,-1,.25),1.15),((.6,-.3,1),.97),((-.2,-1,-.4),.91)],2)
cutstone('Rock_Entry_Low_Toe',(-1.37,-2.92,.18),(1.5,1.02,.61),-.12,
 [((1,-1,.35),1.02),((-1,-1,.4),1.11),((0,-.55,1),.88)])
# The cape crown behind the stairway reads as two slanting fractures.
cutstone('Rock_Cape_High_Crown',(4.05,.12,2.68),(1.25,1.67,.74),-.18,
 [((1,-1,.2),1.03),((-1,-1,.4),1.1),((0,-.4,1),.88),((1,.5,.5),1.16)])
cutstone('Rock_Cape_Lower_Wall',(4.43,.14,1.22),(1.31,1.65,1.08),-.11,
 [((1,-1,.45),1.05),((-1,-1,.4),1.13),((0,-1,-.2),.91),((1,.3,-.5),1.08)],2)
cutstone('Rock_Tide_Low_Edge',(5.73,-.12,.19),(1.20,1.16,.61),-.23,
 [((1,-1,.4),.99),((-1,-1,.6),1.13),((.2,-.5,1),.9)])
# Stair flank follows the descent; crown remains below the actual treads.
cutstone('Rock_Stair_Upper_Side',(.65,-2.73,.87),(1.57,.70,.82),-.18,
 [((1,-1,.3),1.03),((-1,-1,.4),1.08),((0,-.4,1),.91)])
cutstone('Rock_Stair_Landing_Side',(2.49,-3.03,.54),(1.16,.66,.73),-.15,
 [((1,-1,.4),1.0),((-1,-1,.2),1.1),((0,-.4,1),.86)])
cutstone('Rock_Stair_Lower_Bed',(4.40,-3.55,-.05),(1.55,.72,.43),-.09,
 [((1,-1,.3),1.05),((-1,-1,.5),1.13),((0,-.4,1),.86)])
# A restrained buried outcrop at the bamboo roots, not a second focal point.
cutstone('Rock_Bamboo_Buried',(-5.35,2.28,3.30),(1.10,.62,.47),.15,
 [((1,-1,.3),1.03),((-1,-1,.3),1.01),((0,-.4,1),.84)])

# Face two treads with subtle separate chips rather than equal repeated bevels.
for ob in steps.objects:
    if '_Tread_' in ob.name:
        for mod in ob.modifiers:
            if mod.type=='BEVEL':mod.width=.035
        ob.data.materials[0]=bpy.data.materials['Fresh_Step' if int(ob.name[-2:])%4!=2 else 'Fresh_Step_Variant']

# New grass patches are low, overlapping, and share upward shading normals.
for ob in list(green.objects):
    if 'Clump' in ob.name or 'Turf_Tongue' in ob.name:bpy.data.objects.remove(ob,do_unlink=True)

def groundpatch(name,x,y,rx,ry,z,mi,seed):
    pr=random.Random(seed);n=32;vs=[(x,y,z+.002)]
    for i in range(n):
        a=i*math.tau/n;f=pr.uniform(.82,1.08)
        vs.append((x+math.cos(a)*rx*f,y+math.sin(a)*ry*f,z))
    fs=[(0,i+1,(i+1)%n+1) for i in range(n)]
    return mesh(name,vs,fs,green,[grassm[mi]])

patches=[(-9.4,-2.25,1.3,.58,1),(-7.4,-2.4,1.45,.65,0),(-4.8,-2.2,1.25,.57,1),
 (-2.5,-2.02,.68,.30,0),(-9.3,1.2,1.3,.7,2),(-7.2,1.6,1.7,.87,2),
 (-4.6,1.65,1.4,.81,2),(-2.5,2,1.3,.8,0),(.0,2.4,1.5,.7,1),
 (2.1,1.1,1.1,.66,0),(-8.7,.42,.7,.21,0),(-5.9,.22,.8,.24,1)]
for j,(x,y,rx,ry,mi) in enumerate(patches):
    groundpatch('Grass_Patch_%02d'%j,x,y,rx,ry,3.146+j*.0002,mi,220+j)
    vs=[];fs=[]
    # Short broad blades concentrate at the edge of a larger color mass.
    count=int((rx+ry)*23)
    for i in range(count):
        a=rng.uniform(0,math.tau);r=rng.uniform(.45,1.0)
        bx=x+math.cos(a)*rx*r;by=y+math.sin(a)*ry*r
        h=rng.uniform(.10,.26);w=rng.uniform(.033,.065);lean=rng.uniform(.04,.11)
        d=Vector((math.cos(a),math.sin(a),0));s=Vector((-d.y,d.x,0))
        base=Vector((bx,by,3.14));k=len(vs)
        vs.extend([tuple(base-s*w),tuple(base+s*w),tuple(base+d*lean+s*w*.45+Vector((0,0,h*.5))),tuple(base+d*lean+Vector((0,0,h))),tuple(base+d*lean-s*w*.5+Vector((0,0,h*.55)))])
        fs.append(tuple(range(k,k+5)))
    ob=mesh('Grass_Patch_Blades_%02d'%j,vs,fs,green,[grassm[mi]])
    ob.data.normals_split_custom_set([(0,0,1)]*len(ob.data.loops))

# Rebuild bamboo from bent culms and volume-shaded lanceolate leaf sprays.
for ob in list(bamboo.objects):bpy.data.objects.remove(ob,do_unlink=True)

def rod(name,points,radii,mat,sides=7):
    vs=[];fs=[]
    for j,(p,r) in enumerate(zip(points,radii)):
        d=Vector(points[min(len(points)-1,j+1)])-Vector(points[max(0,j-1)])
        d.normalize();u=d.cross(Vector((0,1,0))).normalized();v=d.cross(u).normalized()
        for i in range(sides):vs.append(tuple(Vector(p)+r*(u*math.cos(i*math.tau/sides)+v*math.sin(i*math.tau/sides))))
    fs=[tuple(reversed(range(sides))),tuple(range((len(points)-1)*sides,len(points)*sides))]
    for j in range(len(points)-1):
        for i in range(sides):fs.append((j*sides+i,j*sides+(i+1)%sides,(j+1)*sides+(i+1)%sides,(j+1)*sides+i))
    return mesh(name,vs,fs,bamboo,[mat])

def spray(name,center,angle,length,depth,seed):
    pr=random.Random(seed);center=Vector(center);vs=[];fs=[];normals=[]
    # Arching central twig, with leaves overlapping into a readable aggregate.
    axis=Vector((math.cos(angle),math.sin(angle)*.45,-.22))
    side=Vector((-.20*math.sin(angle),-.58,.82)).normalized()
    for i in range(22):
        t=(i//2)/11;sign=-1 if i%2 else 1
        root=center+axis*length*(t-.40)+Vector((0,0,.14*math.sin(t*math.pi)))
        direction=(axis*.25+side*sign*.67+Vector((0,-.22,-.48))).normalized()
        # Lower drooping leaves are longer; outer tips retain narrow bamboo shape.
        ll=length*pr.uniform(.30,.49)*(1.1-.35*t)
        wide=ll*pr.uniform(.125,.18)
        tip=root+direction*ll
        mid=root.lerp(tip,.44)+Vector((0,-.055,.06))
        cross=Vector((direction.z,0,-direction.x)).normalized()
        k=len(vs);vs.extend([tuple(root),tuple(mid-cross*wide),tuple(tip),tuple(mid+cross*wide)])
        fs.append((k,k+1,k+2,k+3))
    ob=mesh(name,vs,fs,bamboo,[leafm[depth]])
    for p in ob.data.polygons:
        for li in p.loop_indices:
            q=ob.data.vertices[ob.data.loops[li].vertex_index].co-center
            # Proxy ellipsoid shades the spray as a volume, not isolated blades.
            n=Vector((q.x/(length*length),q.y*1.3-.35,q.z*1.25+.72)).normalized()
            normals.append(tuple(n))
    ob.data.normals_split_custom_set(normals)
    return ob

stems=[(-10.1,1.4,4.7,-.35),(-9.5,2.8,5.5,.30),(-8.8,1.7,4.8,-.10),
 (-8.0,3.0,5.7,.35),(-7.4,1.8,5.1,.28),(-6.5,2.9,5.2,-.25),
 (-5.9,1.7,4.5,.35),(-4.9,3.05,5.3,.12),(-3.8,2.9,4.65,-.22),
 (-2.8,3.15,4.0,.18),(-1.55,3.2,3.8,.2),(-.6,3.0,3.45,.26)]
for j,(x,y,h,lean) in enumerate(stems):
    base=Vector((x,y,3.12))
    def point(t):return base+Vector((lean*t*t,.28*t*t,h*t))
    ts=[i/7 for i in range(8)]
    rod('Bamboo_%02d_Culm'%j,[point(t) for t in ts],[.075*(1-.65*t) for t in ts],stemm)
    for n in range(1,int(h/.57)):
        t=n*.57/h;c=point(t)
        rod('Bamboo_%02d_Joint_%02d'%(j,n),[c-Vector((0,0,.018)),c+Vector((0,0,.018))],[.078*(1-.65*t)]*2,nodem)
    for k,t in enumerate([.38,.52,.66,.79,.90]):
        c=point(t);direction=-1 if (j+k)%2 else 1
        length=(1.15 if k<3 else .84)*(1+.1*math.sin(j))
        end=c+Vector((direction*length*.60,-.25,.13))
        rod('Bamboo_%02d_Bough_%02d'%(j,k),[c,c.lerp(end,.5)+Vector((0,0,.1)),end],[.024,.016,.006],stemm,5)
        angle=.12 if direction==1 else math.pi-.18
        spray('Bamboo_Leaves_%02d_%02d'%(j,k),end,angle,length,0 if y<2 else 2,j*99+k)
        # Small top-lit companion forms a clump, with gaps between larger boughs.
        if k in [1,3]:spray('Bamboo_Leaves_%02d_%02d_tip'%(j,k),end+Vector((direction*.32,.18,.24)),angle+.17,.78,1,j*99+k+777)

scene['revision']='fresh-cape-reference-polish-1'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/fresh_pixel_cape/fresh_pixel_cape.blend'))
print(json.dumps({'revision':scene['revision'],'meshes':sum(o.type=='MESH' for o in scene.objects),'old_geometry_imported':False}))
