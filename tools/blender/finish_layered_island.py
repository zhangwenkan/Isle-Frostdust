"""Framing, cave depth and coast finish; execute in Blender through MCP."""
import bpy, math, json
import numpy as np
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'assets/layered_island'
scene=bpy.data.scenes['Layered_Island_20261116'];previous=bpy.context.window.scene;bpy.context.window.scene=scene
collection=next(c for c in scene.collection.children if c.name.startswith('Layered_Island_Authored'))
C=Vector((0,-32,24));F=(Vector((0,4,3))-C).normalized();R=Vector((1,0,0));U=R.cross(F).normalized();T=math.tan(math.radians(32)/2)
def ray(u,v):return F+R*((u/2048-.5)*2*T*4/3)+U*((.5-v/1536)*2*T)
def point(u,v,z):
    d=ray(u,v);return C+d*((z-C.z)/d.z)
def project(p):
    q=p-C;d=q.dot(F);return (1024+q.dot(R)/d/(T*4/3)*1024,768-q.dot(U)/d/T*768)
def uv_vertices(ob):
    uv=ob.data.uv_layers[0];seen=set()
    for loop in ob.data.loops:
        if loop.vertex_index in seen:continue
        seen.add(loop.vertex_index);q=uv.data[loop.index].uv
        yield ob.data.vertices[loop.vertex_index],q.x*2048,(1-q.y)*1536

for name in ['Foreground_Right_Rock','Foreground_Right_Leaves','Foreground_Bottom','Trees_Cave_Back']:
    ob=scene.objects[name]
    for vert,u,v in uv_vertices(ob):
        depth=(vert.co-C).dot(F)
        if name.startswith('Foreground_Right'):
            u=2048+(u-2048)*1.62+360;v=1536+(v-1536)*1.15+45
        elif name=='Foreground_Bottom':v+=90
        vert.co=C+ray(u,v)*depth
    ob.data.update()
base=scene.objects['Trees_Cave_Back']
old=scene.objects.get('Trees_Right_Extension')
if old:bpy.data.objects.remove(old,do_unlink=True)
ob=base.copy();ob.data=base.data.copy();ob.name='Trees_Right_Extension';collection.objects.link(ob)
for vert,u,v in uv_vertices(ob):
    depth=(vert.co-C).dot(F)+1.3;vert.co=C+ray(u+370,v+60)*depth
ob.data.update()

outer=scene.objects['Cave_Outer_Relief']
for vert,u,v in uv_vertices(outer):
    depth=(vert.co-C).dot(F)
    if u>1850:u+=(u-1850)*2.15
    if v>965:v+=(v-965)*2.7
    vert.co=C+ray(u,v)*depth
outer.data.update()
# The interior is a recessed wall behind the last traversable step, not a
# projected wall that cuts through the sprite at arbitrary body heights.
inner=scene.objects['Cave_Inner_Relief']
for vert,u,v in uv_vertices(inner):
    d=ray(u,v);vert.co=C+d*((7.0-C.y)/d.y)
inner.data.update()

# Extend the left cliff behind the extra edge bamboo, using a flipped strip of
# the supplied cliff texture. Only untraversable frame-edge rock uses this strip.
land=scene.objects['Land_Relief'];vs=[];uvs=[];fs=[];nx=30;ny=74
for j in range(ny+1):
    v=230+j/ny*1030
    for i in range(nx+1):
        u=-440+i/nx*452;source_u=300*(1-i/nx)+6*i/nx
        h=max(.12,2.85-(v-1090)*.0122) if v>1090 else 2.85+max(0,880-v)*.0085
        vs.append(point(u,v,h));uvs.append((source_u/2048,1-v/1536))
for j in range(ny):
    for i in range(nx):
        n=j*(nx+1)+i;fs.append((n,n+nx+1,n+nx+2,n+1))
old=scene.objects.get('Land_Left_Extension')
if old:bpy.data.objects.remove(old,do_unlink=True)
me=bpy.data.meshes.new('Land_Left_Extension');me.from_pydata(vs,[],fs);me.update()
ob=bpy.data.objects.new('Land_Left_Extension',me);collection.objects.link(ob);me.materials.append(land.data.materials[0]);uv=me.uv_layers.new(name='UVMap')
for poly in me.polygons:
    for li in poly.loop_indices:uv.data[li].uv=uvs[me.loops[li].vertex_index]

# A shoreline polyline is exported for the water shader; it is measured from
# the beach edge in the painting and lies on the authored near-coast terrain.
im=next(im for im in bpy.data.images if im.name.startswith('land.png'))
a=np.flipud(np.array(im.pixels[:],dtype=np.float32).reshape(im.size[1],im.size[0],4)[:,:,3])
shore=[]
for u in np.linspace(120,1030,32):
    x=int(u);ys=np.where(a[:,x]>.6)[0];v=float(ys[-1]);p=point(u,v,.15)
    shore.append([round(p.x,5),round(-p.y,5)])
layout=json.loads((OUT/'layout.json').read_text(encoding='utf-8'));layout['shoreline']=shore;layout['revision']='resume-pass3'
layout['objects']=[{'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons)} for o in scene.objects if o.type=='MESH']
(OUT/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),encoding='utf-8')
for im in bpy.data.images:
    if im.name.startswith('wood_plank'):
        im.filepath=str(OUT/'textures/wood_plank.png');im.reload();im.pack()
bpy.data.libraries.write(str(OUT/'layered_island.blend'),{scene},fake_user=True,compress=True)
bpy.ops.object.select_all(action='DESELECT')
for ob in scene.objects:
    if ob.type=='MESH':ob.select_set(True)
bpy.context.view_layer.objects.active=land
bpy.ops.export_scene.gltf(filepath=str(OUT/'layered_island.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
bpy.context.window.scene=previous
print(json.dumps({'revision':'resume-pass3','meshes':len(layout['objects']),'shore_points':len(shore)}))
