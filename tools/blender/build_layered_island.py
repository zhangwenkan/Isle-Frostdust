"""Run only through blender-mcp. Build the independent painted island scene."""
import bpy, math, json
import numpy as np
from pathlib import Path
from mathutils import Vector

ROOT=Path('D:/自己做着玩的/孤屿霜尘')
OUT=ROOT/'assets/layered_island'
TEX=OUT/'textures'
REVIEW=ROOT/'artifacts/layered-island-build'
REVIEW.mkdir(parents=True,exist_ok=True)
NAME='Layered_Island_20261116'
previous=bpy.context.window.scene
if NAME in bpy.data.scenes:
    old=bpy.data.scenes[NAME]
    for ob in list(old.objects): bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.scenes.remove(old)
scene=bpy.data.scenes.new(NAME)
scene.unit_settings.system='METRIC'
collection=bpy.data.collections.new('Layered_Island_Authored')
scene.collection.children.link(collection)

C=Vector((0,-32,24)); TARGET=Vector((0,4,3))
F=(TARGET-C).normalized(); R=Vector((1,0,0)); U=R.cross(F).normalized()
T=math.tan(math.radians(32)/2)
images={}; alphas={}; mats={}; objects=[]

def ray(u,v): return F+R*((u/2048-.5)*2*T*4/3)+U*((.5-v/1536)*2*T)
def point(u,v,z):
    d=ray(u,v)
    return C+d*((z-C.z)/d.z)
def plane_point(u,v,y):
    d=ray(u,v)
    return C+d*((y-C.y)/d.y)
def project(p):
    q=Vector(p)-C; depth=q.dot(F)
    return (1024+q.dot(R)/depth/(T*4/3)*1024,768-q.dot(U)/depth/T*768)
def godot(v): return [round(v[0],6),round(v[2],6),round(-v[1],6)]

def load(name):
    if name not in images:
        im=bpy.data.images.load(str(TEX/(name+'.png')),check_existing=True)
        im.reload()
        images[name]=im
        arr=np.array(im.pixels[:],dtype=np.float32).reshape(im.size[1],im.size[0],4)
        alphas[name]=np.flipud(arr[:,:,3])
    return images[name]

def material(name,texture=None,color=(.42,.32,.19,1)):
    if name in mats:return mats[name]
    m=bpy.data.materials.new('LI_'+name);m.diffuse_color=color;m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=.9
    if texture:
        n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=load(texture);n.interpolation='Linear'
        m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
        m.node_tree.links.new(n.outputs['Alpha'],bs.inputs['Alpha'])
        m.surface_render_method='DITHERED'
    mats[name]=m
    return m

def mesh(name,vs,fs,mat,uvs=None,weights=None):
    data=bpy.data.meshes.new(name);data.from_pydata(vs,[],fs);data.update()
    ob=bpy.data.objects.new(name,data);collection.objects.link(ob);objects.append(ob)
    data.materials.append(mat)
    uv=data.uv_layers.new(name='UVMap')
    wind=data.uv_layers.new(name='Wind')
    for poly in data.polygons:
        for li in poly.loop_indices:
            vi=data.loops[li].vertex_index
            uv.data[li].uv=uvs[vi] if uvs else (data.vertices[vi].co.x*.5,data.vertices[vi].co.z*.5)
            wind.data[li].uv=(weights[vi] if weights else 0,0)
    return ob

def projected(name,tex,hfn,step=16):
    load(tex); a=alphas[tex]; ys,xs=np.where(a>.025)
    x0=max(0,int(xs.min())//step*step);x1=min(2048,(int(xs.max())//step+1)*step)
    y0=max(0,int(ys.min())//step*step);y1=min(1536,(int(ys.max())//step+1)*step)
    xx=list(range(x0,x1+1,step)); yy=list(range(y0,y1+1,step))
    if xx[-1]!=x1:xx.append(x1)
    if yy[-1]!=y1:yy.append(y1)
    vs=[];uv=[];fs=[]
    for v in yy:
        for u in xx:
            vs.append(point(u,v,hfn(u,v)));uv.append((u/2048,1-v/1536))
    for j in range(len(yy)-1):
        for i in range(len(xx)-1):
            patch=a[yy[j]:max(yy[j]+1,yy[j+1]),xx[i]:max(xx[i]+1,xx[i+1])]
            if not patch.size or patch.max()<.025:continue
            n=j*len(xx)+i
            fs.extend([(n,n+len(xx),n+1),(n+1,n+len(xx),n+len(xx)+1)])
    return mesh(name,vs,fs,material('Paint_'+tex,tex),uv)

def card(name,tex,rect,anchor=None,depth=None,wind=0,uvbox=(0,0,1,1),tint=(1,1,1,1)):
    x0,y0,x1,y1=rect
    vs=[];uv=[];weights=[];fs=[];nx=10;ny=18
    py=point(*anchor).y if anchor else 0
    for j in range(ny+1):
        v=y0+(y1-y0)*j/ny
        for i in range(nx+1):
            u=x0+(x1-x0)*i/nx
            p=C+ray(u,v)*depth if depth else plane_point(u,v,py)
            vs.append(p);uv.append((uvbox[0]+(uvbox[2]-uvbox[0])*i/nx,1-(uvbox[1]+(uvbox[3]-uvbox[1])*j/ny)))
            weights.append(((1-j/ny)**1.8)*wind)
    for j in range(ny):
        for i in range(nx):
            n=j*(nx+1)+i;fs.append((n,n+nx+1,n+nx+2,n+1))
    return mesh(name,vs,fs,material('Plant_'+tex if wind else 'Paint_'+tex,tex,tint),uv,weights)

def box(name,center,scale,mat,angle=0):
    vs=[]
    co,si=math.cos(angle),math.sin(angle)
    for z in [-.5,.5]:
        for y in [-.5,.5]:
            for x in [-.5,.5]:
                xx=x*scale[0];yy=y*scale[1]
                vs.append((center[0]+co*xx-si*yy,center[1]+si*xx+co*yy,center[2]+z*scale[2]))
    fs=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    ob=mesh(name,vs,[tuple(reversed(f)) for f in fs],mat)
    uv=ob.data.uv_layers[0]
    for poly in ob.data.polygons:
        for k,li in enumerate(poly.loop_indices):uv.data[li].uv=[(0,0),(1,0),(1,1),(0,1)][k]
    return ob

def tube(name,pts,radius,mat,sides=8):
    vs=[];uv=[];fs=[]
    for j,p in enumerate(pts):
        p=Vector(p); tangent=(Vector(pts[min(j+1,len(pts)-1)])-Vector(pts[max(j-1,0)])).normalized()
        ax=tangent.cross(Vector((0,0,1)))
        if ax.length<.01:ax=Vector((1,0,0))
        ax.normalize();ay=tangent.cross(ax).normalized()
        for i in range(sides):
            a=i*2*math.pi/sides;vs.append(p+radius*(ax*math.cos(a)+ay*math.sin(a)));uv.append((i/sides,j/(len(pts)-1)))
    for j in range(len(pts)-1):
        for i in range(sides):
            n=j*sides+i;k=j*sides+(i+1)%sides
            fs.append((n,k,k+sides,n+sides))
    fs.append(tuple(range(sides-1,-1,-1)));fs.append(tuple((len(pts)-1)*sides+i for i in range(sides)))
    return mesh(name,vs,fs,mat,uv)

def edge(u):
    return float(np.interp(u,[0,250,420,590,760,950,1160],[1130,1110,1060,990,925,920,860]))
def land_h(u,v):
    if v>=1210:return .15+max(0,1-abs(u-963)/130)*max(0,1-abs(v-1245)/95)*.85
    if v<edge(u):return 2.85+max(0,880-v)*.0085*min(1,max(0,(900-u)/220))
    return max(.13,2.85-(v-edge(u))*.0122)

land=projected('WALK_Land', 'land',land_h,12)
outer=projected('Cave_Outer_Relief','cave_outer',lambda u,v: max(-.8,2.85+(895-v)*(.015 if v<895 else .017)),12)
inner=projected('WALK_Cave_Interior','cave_inner',lambda u,v: 2.85+(890-v)*(.006 if v>735 else .012),10)

# True stair treads and vertical risers are built between surveyed image anchors.
bottom=point(625,1210,.15); top=point(692,944,2.85)
stairdir=(top-bottom);stairdir.z=0;stairlen=stairdir.length;stairdir.normalize()
across=Vector((1,0,0)); stair_width=1.95;steps=15
vs=[];uv=[];fs=[]
for j in range(steps):
    a=bottom+(top-bottom)*(j/steps); b=bottom+(top-bottom)*((j+1)/steps)
    h=b.z
    corners=[Vector((a.x,a.y,h))-across*stair_width/2,Vector((a.x,a.y,h))+across*stair_width/2,
             Vector((b.x,b.y,h))+across*stair_width/2,Vector((b.x,b.y,h))-across*stair_width/2,
             Vector((a.x,a.y,a.z))-across*stair_width/2,Vector((a.x,a.y,a.z))+across*stair_width/2]
    n=len(vs);vs+=corners
    uv += [(project(p)[0]/2048,1-project(p)[1]/1536) for p in corners]
    fs += [(n,n+1,n+2,n+3),(n+4,n+5,n+1,n)]
mesh('WALK_Front_Stairs',vs,fs,material('Paint_land','land'),uv)

wood=material('Timber','wood_plank',(.57,.39,.19,1))
postmat=material('Posts','wood_post',(.43,.30,.18,1))
rope=material('Rope',None,(.49,.37,.23,1))
L=point(1040,865,2.85);E=point(1612,865,2.85)
span=E-L;span.z=0;length=span.length;tangent=span.normalized();side=Vector((-tangent.y,tangent.x,0));width=1.68
angle=math.atan2(tangent.y,tangent.x)
def deck(t):
    p=L.lerp(E,t);p.z-=math.sin(math.pi*t)*.52;return p
nboards=27
for j in range(nboards):
    t=(j+.5)/nboards;p=deck(t);p.z-=.055
    box('Bridge_Plank_%02d'%j,p,(length/nboards-.023,width,.11),wood,angle+.008*math.sin(j*2.1))
    # Wooden pegs visibly join the deck to its side bearers.
for sign in [-1,1]:
    s=side*(width*.50*sign)
    tube('Bridge_Bearer_%d'%sign,[deck(j/54)+s-Vector((0,0,.1)) for j in range(55)],.059,rope)
    tube('Bridge_Handrope_%d'%sign,[deck(j/54)+s+Vector((0,0,1.04)) for j in range(55)],.043,rope)
    for j in range(13):
        t=j/12;p=deck(t)+s;other=deck(min(1,t+.065))+s
        tube('Bridge_Hanger_%d_%02d'%(sign,j),[p+Vector((0,0,.01)),other+Vector((0,0,1.03))],.031,rope,6)
    for end in [0,1]:
        p=deck(end)+s
        tube('Bridge_Post_%d_%d'%(sign,end),[p-Vector((0,0,.15)),p+Vector((0,0,1.30))],.115,postmat,9)
        for dz in [.91,1.01,1.11]:
            loop=[p+Vector((math.cos(i*2*math.pi/20)*.134,math.sin(i*2*math.pi/20)*.134,dz)) for i in range(21)]
            tube('Bridge_Lashing_%d_%d_%02d'%(sign,end,int(dz*100)),loop,.027,rope,6)
        outward=tangent*(-.65 if end==0 else .65)
        anchor=p+outward+s*.3-Vector((0,0,.03))
        tube('Bridge_Anchor_%d_%d'%(sign,end),[p+Vector((0,0,1.0)),anchor],.044,rope)
        box('Bridge_Anchor_Peg_%d_%d'%(sign,end),anchor,(.13,.13,.26),postmat)
tube('Bridge_Hanging_Loose_End',[deck(.16)-side*width*.52-Vector((0,0,j*.13)) for j in range(8)],.029,rope,6)

# A continuous Blender-authored support surface bridges tiny board seams.
vs=[];uv=[];fs=[]
for j in range(109):
    for sign in [-1,1]:
        vs.append(deck(j/108)+side*(width*.46*sign)+Vector((0,0,.006)));uv.append((j/108,(sign+1)/2))
for j in range(108):fs.append((j*2,j*2+1,j*2+3,j*2+2))
mesh('SUPPORT_Bridge',vs,fs,wood,uv)

# Near vegetation has real front/back placement. Each section has UV2 wind
# weights, with immobile bases. All art is from the supplied layers.
card('Bamboo_Back','bamboo_back',(-90,45,970,840),anchor=(570,760,4.0),wind=.45)
card('Bamboo_Middle_Left','bamboo_middle',(-20,115,420,935),anchor=(280,972,3.25),wind=.65)
card('Bamboo_Middle_Deep','bamboo_middle',(320,110,685,750),anchor=(520,785,3.6),wind=.55)
card('Bamboo_Front_Left','bamboo_front',(-130,365,310,1260),anchor=(180,1220,.17),wind=.6)
card('Bamboo_Bridge','bamboo_bridge',(645,225,1010,946),anchor=(915,935,2.65),wind=.60)
card('Bamboo_Left_Extension','bamboo_middle',(-490,140,-65,985),anchor=(-110,1040,2.6),wind=.5)
card('Trees_Cave_Back','trees_back',(0,0,2048,1536),anchor=(1870,730,5.0),wind=.23)
card('Vine_Left','vine_left',(0,0,2048,1536),anchor=(1645,585,6.2),wind=.16)
card('Vine_Right','vine_right',(0,0,2048,1536),anchor=(1830,580,6.0),wind=.18)
card('Foreground_Bottom','foreground_bottom',(0,0,2048,1536),anchor=(1100,1480,.1),wind=0)
card('Foreground_Right_Rock','foreground_right_rock',(0,0,2048,1536),anchor=(1850,1450,1.0))
card('Foreground_Right_Leaves','foreground_right_leaves',(0,0,2048,1536),anchor=(1850,1450,1.0),wind=.24)

# Distant paintings stay at distinct depths; sea and atmosphere animate alone.
card('Sky_Painting','sky',(-600,-200,2648,1736),depth=245)
card('Mountain_Far','mountain_far',(0,0,2048,1536),depth=180)
card('Mountain_Middle','mountain_middle',(0,0,2048,1536),depth=138)
card('Mountain_Near','mountain_near',(0,0,2048,1536),depth=103)
water=mesh('Sea_Surface',[(-130,-40,-.18),(130,-40,-.18),(130,200,-.18),(-130,200,-.18)],[(0,1,2,3)],material('Water',None,(.16,.30,.38,1)),[(0,0),(1,0),(1,1),(0,1)])
card('Cloud_Sea_Front','sky',(-450,470,2450,1480),depth=74)
card('Cloud_Sea_Back','sky',(-450,360,2450,1190),depth=123)

# A small reusable ground-contact disk, authored here rather than generated in Godot.
vs=[(0,0,0)]+[(math.cos(i*2*math.pi/32)*.5,math.sin(i*2*math.pi/32)*.5,0) for i in range(32)]
uv=[(.5,.5)]+[(v[0]+.5,v[1]+.5) for v in vs[1:]]
mesh('Hero_Contact_Disk',vs,[(0,1+i,1+(i+1)%32) for i in range(32)],material('Contact',None,(.05,.05,.04,1)),uv)

# Paths are authoring guides exported as positions; movement code only follows
# and samples existing geometry, never creates environment meshes.
anchors={
 'beach':point(460,1290,.15), 'stair_bottom':bottom, 'stair_top':top,
 'junction':point(780,883,2.85),'bridge_left':L,'bridge_right':E,
 'cave_mouth':point(1740,855,3.06),'cave_end':point(1800,748,3.70),
 'forest_turn':point(645,817,3.3855),'forest_mid':point(505,674,4.601),
 'forest_end':point(195,445,6.5475),
}
edges=[('beach','stair_bottom'),('stair_bottom','stair_top'),('stair_top','junction'),('junction','bridge_left'),('bridge_left','bridge_right'),('bridge_right','cave_mouth'),('cave_mouth','cave_end'),('junction','forest_turn'),('forest_turn','forest_mid'),('forest_mid','forest_end')]
camdata=bpy.data.cameras.new('LI_ReferenceCamera');cam=bpy.data.objects.new('LI_ReferenceCamera',camdata);collection.objects.link(cam)
cam.location=C;cam.rotation_euler=(TARGET-C).to_track_quat('-Z','Y').to_euler();camdata.type='PERSP';camdata.lens=42;scene.camera=cam
scene.render.resolution_x=2048;scene.render.resolution_y=1536;scene.render.resolution_percentage=100

manifest={'camera':{'position':godot(C),'target':godot(TARGET),'fov':32,'reference_size':[2048,1536]},'anchors':{k:godot(v) for k,v in anchors.items()},'edges':edges,'bridge':{'length':length,'width':width,'sag':.52,'left':godot(L),'right':godot(E)},'stairs':{'count':steps,'width':stair_width,'rise':2.7/steps},'objects':[{'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons)} for o in objects]}
(OUT/'layout.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')

for im in images.values():im.pack()
bpy.data.libraries.write(str(OUT/'layered_island.blend'),{scene},fake_user=True,compress=True)
try:
    bpy.context.window.scene=scene
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objects:ob.select_set(True)
    bpy.context.view_layer.objects.active=land
    bpy.ops.export_scene.gltf(filepath=str(OUT/'layered_island.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
finally:
    bpy.context.window.scene=previous
print(json.dumps({'scene':NAME,'restored_scene':previous.name,'meshes':len(objects),'vertices':sum(len(o.data.vertices) for o in objects),'faces':sum(len(o.data.polygons) for o in objects),'bridge_length':length,'saved':str(OUT/'layered_island.blend')},ensure_ascii=False))
