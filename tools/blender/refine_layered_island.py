"""Continue the supplied-layer scene inside Blender, via blender-mcp only."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector

ROOT=Path('D:/自己做着玩的/孤屿霜尘')
OUT=ROOT/'assets/layered_island'
NAME='Layered_Island_20261116'
previous=bpy.context.window.scene
if NAME not in bpy.data.scenes:
    with bpy.data.libraries.load(str(OUT/'layered_island.blend')) as (src,dst):
        dst.scenes=[NAME]
scene=bpy.data.scenes[NAME]
collection=next(c for c in scene.collection.children if c.name.startswith('Layered_Island_Authored'))
bpy.context.window.scene=scene
C=Vector((0,-32,24)); TARGET=Vector((0,4,3))
F=(TARGET-C).normalized(); R=Vector((1,0,0)); U=R.cross(F).normalized()
T=math.tan(math.radians(32)/2)
def ray(u,v):return F+R*((u/2048-.5)*2*T*4/3)+U*((.5-v/1536)*2*T)
def point(u,v,z):
    d=ray(u,v);return C+d*((z-C.z)/d.z)
def project(p):
    q=Vector(p)-C;d=q.dot(F)
    return (1024+q.dot(R)/d/(T*4/3)*1024,768-q.dot(U)/d/T*768)
def godot(p):return [round(p.x,6),round(p.z,6),round(-p.y,6)]
def mesh(name,vs,fs,mat):
    old=scene.objects.get(name)
    if old:bpy.data.objects.remove(old,do_unlink=True)
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
    ob=bpy.data.objects.new(name,me);collection.objects.link(ob);me.materials.append(mat)
    uv=me.uv_layers.new(name='UVMap')
    for poly in me.polygons:
        for li in poly.loop_indices:
            u,v=project(me.vertices[me.loops[li].vertex_index].co);uv.data[li].uv=(u/2048,1-v/1536)
    return ob

land=scene.objects.get('Land_Relief') or scene.objects['WALK_Land']
land.name='Land_Relief'
inner=scene.objects.get('Cave_Inner_Relief') or scene.objects['WALK_Cave_Interior']
inner.name='Cave_Inner_Relief'
landmat=land.data.materials[0]
outermat=scene.objects['Cave_Outer_Relief'].data.materials[0]
innermat=inner.data.materials[0]

# Points follow the painted tread centers, including each intervening landing.
screen={
 'beach':(460,1290,.15), 'stair_bottom':(625,1210,.15),
 'stair_top':(692,925,2.85), 'junction':(780,883,2.85),
 'bridge_left':(1040,865,2.85),'bridge_right':(1612,865,2.85),
 'cave_mouth':(1740,855,2.96),'cave_end':(1792,758,3.86),
 'forest_turn':(740,820,2.85),'forest_step1':(685,738,3.57),
 'forest_mid':(580,694,3.57),'forest_step2':(457,545,4.83),
 'forest_landing':(361,501,4.83),'forest_end':(276,400,5.91),
}
anchors={k:point(*v) for k,v in screen.items()}
edges=[('beach','stair_bottom'),('stair_bottom','stair_top'),('stair_top','junction'),('junction','bridge_left'),('bridge_left','bridge_right'),('bridge_right','cave_mouth'),('cave_mouth','cave_end'),('junction','forest_turn'),('forest_turn','forest_step1'),('forest_step1','forest_mid'),('forest_mid','forest_step2'),('forest_step2','forest_landing'),('forest_landing','forest_end')]

def route_strip(name,a,b,width,mat,steps=0):
    a,b=anchors[a],anchors[b]
    d=b-a;d.z=0;side=Vector((d.y,-d.x,0)).normalized()*width*.5
    vs=[];fs=[];count=steps or max(4,int(d.length*12))
    for j in range(count):
        p=a.lerp(b,j/count);q=a.lerp(b,(j+1)/count)
        if steps:
            h=q.z;corners=[p-side,p+side,q+side,q-side,p-side,p+side]
            for i in range(4):corners[i].z=h
            n=len(vs);vs+=corners;fs.extend([(n,n+1,n+2,n+3),(n+4,n+5,n+1,n)])
        else:
            n=len(vs);vs.extend([p-side,p+side,q+side,q-side]);fs.append((n,n+1,n+2,n+3))
    return mesh(name,vs,fs,mat)

old=scene.objects.get('WALK_Front_Stairs')
if old:bpy.data.objects.remove(old,do_unlink=True)
route_strip('WALK_Front_Stairs','stair_bottom','stair_top',1.76,landmat,15)
for idx,(a,b) in enumerate(edges):
    if (a,b) in [('stair_bottom','stair_top'),('bridge_left','bridge_right')]:continue
    cave=a in ['bridge_right','cave_mouth']
    steps={('forest_turn','forest_step1'):4,('forest_mid','forest_step2'):7,('forest_landing','forest_end'):6,('cave_mouth','cave_end'):6}.get((a,b),0)
    route_strip('WALK_Route_%02d'%idx,a,b,.98 if cave else (1.28 if a.startswith('forest') else 1.55),innermat if a=='cave_mouth' else outermat if cave else landmat,steps)

# Pull only the underlying path band a little below the authored treads.
# Broad relief remains for cliffs; it is no longer incorrectly sampled as floor.
route_segments=[(Vector(screen[a][:2]),Vector(screen[b][:2]),screen[a][2],screen[b][2]) for a,b in edges if not a.startswith('cave') and a!='bridge_right' and a!='bridge_left']
uv=land.data.uv_layers[0]
seen=set()
for loop in land.data.loops:
    vi=loop.vertex_index
    if vi in seen:continue
    seen.add(vi);u,v=uv.data[loop.index].uv;u*=2048;v=(1-v)*1536
    p=Vector((u,v));nearest=1e9;rh=.15
    for a,b,h1,h2 in route_segments:
        d=b-a;t=max(0,min(1,(p-a).dot(d)/d.length_squared));dist=(p-(a+d*t)).length
        if dist<nearest:nearest=dist;rh=h1+(h2-h1)*t
    if nearest<90:
        original=land.data.vertices[vi].co.z
        weight=max(0,min(1,(90-nearest)/25))
        h=original*(1-weight)+(rh-.22)*weight
        land.data.vertices[vi].co=point(u,v,h)
land.data.update()

# Interior painting includes wall art, so only its new floor is walkable.
# Recess the old painting under the new stair floor along that narrow corridor.
uv=inner.data.uv_layers[0];seen=set()
for loop in inner.data.loops:
    vi=loop.vertex_index
    if vi in seen:continue
    seen.add(vi);u,v=uv.data[loop.index].uv;u*=2048;v=(1-v)*1536
    if 1695<u<1840 and 750<v<875:
        h=2.96+max(0,min(1,(855-v)/97))*.9-.22
        inner.data.vertices[vi].co=point(u,v,h)
inner.data.update()

# Widen only frame-edge foliage/rock beyond the reference frame. The central
# beach, bridge and cave proportions remain unchanged in the 16:9 viewport.
for name in ['Trees_Cave_Back','Foreground_Right_Rock','Foreground_Right_Leaves','Foreground_Bottom']:
    ob=scene.objects[name]
    for vert in ob.data.vertices:
        u,v=project(vert.co);newu=u;newv=v
        if u>1830:newu=u+(u-1830)*2.25
        if name.startswith('Foreground') and v>1320:newv=v+(v-1320)*.65
        if newu!=u or newv!=v:
            old_depth=(vert.co-C).dot(F);vert.co=C+ray(newu,newv)*old_depth
    ob.data.update()

# Extend distant paintings to the wide viewport, avoiding exposed vertical edges.
for name in ['Mountain_Far','Mountain_Middle','Mountain_Near']:
    ob=scene.objects[name]
    for vert in ob.data.vertices:
        u,v=project(vert.co);depth=(vert.co-C).dot(F)
        vert.co=C+ray(1024+(u-1024)*1.36,v)*depth
    ob.data.update()

# The imported sprite stays upright; its shadow disk was already authored here.
# Save a Blender camera matching the actual 16:9 gameplay projection.
cam=scene.camera;cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL'
cam.data.sensor_height=24;cam.data.lens=24/(2*T)
scene.render.resolution_x=1280;scene.render.resolution_y=720
manifest=json.loads((OUT/'layout.json').read_text(encoding='utf-8'))
manifest['anchors']={k:godot(v) for k,v in anchors.items()};manifest['edges']=edges
manifest['revision']='resume-pass2';manifest['stairs']['forest_flights']=[4,7,6]
manifest['objects']=[{'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons)} for o in scene.objects if o.type=='MESH']
(OUT/'layout.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
scene.render.engine='BLENDER_EEVEE'
bpy.data.libraries.write(str(OUT/'layered_island.blend'),{scene},fake_user=True,compress=True)
bpy.ops.object.select_all(action='DESELECT')
for ob in scene.objects:
    if ob.type=='MESH':ob.select_set(True)
bpy.context.view_layer.objects.active=land
bpy.ops.export_scene.gltf(filepath=str(OUT/'layered_island.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
bpy.context.window.scene=previous
print(json.dumps({'revision':'resume-pass2','routes':len(edges),'scene':NAME,'meshes':len(manifest['objects'])}))
