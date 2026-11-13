"""Island west forest, authored exclusively in the live Blender via MCP.

Original Wandering Sword subdivided sprite meshes/UVs, new island placement.
"""
import bpy, math, json, random, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/pixel-bamboo-west-review';A=R/'assets/pixel_bamboo_west'
S=Path('D:/Y 逸jian风yun决 v1.23.26 全DLC xg器/WanderingSword/analysis/12_followup/20261109-bamboo-scene')
assert Path(bpy.data.filepath)==R/'assets/island_blender/nameless_island.blend'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
def col(name):
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in scene.collection.children:scene.collection.children.link(c)
    return c
archive=col('90_Before_Pixel_Bamboo_West');archive.hide_render=True
current=col('33_Pixel_Bamboo_West')
for o in list(current.objects):bpy.data.objects.remove(o,do_unlink=True)
removed=[]
for o in list(scene.objects):
    if o.name.startswith('ForestVisibility_') and not any(c.name.startswith('90_') for c in o.users_collection):
        removed.append(o.name)
        for c in list(o.users_collection):c.objects.unlink(o)
        archive.objects.link(o);o.hide_render=True;o.hide_set(True)
def G(x,h,z):return Vector((x,-z,h))
def clamp(v):return max(0,min(1,v))
def smooth(a,b,v):
    t=clamp((v-a)/(b-a));return t*t*(3-2*t)
land=scene.objects['Fish_West_Continuous_Land']
lt=BVHTree.FromPolygons([land.matrix_world@v.co for v in land.data.vertices],[tuple(p.vertices) for p in land.data.polygons])
def hit(t,x,z):
    p=t.ray_cast(G(x,50,z),Vector((0,0,-1)))[0];return p.z if p else None
def front_z(x):return -1.65-.16*math.sin(x*.64)
def floor_y(x,z):
    d=max(0,front_z(x)-z)
    h=hit(lt,max(-18,min(2.7,x)),front_z(x))
    if h is None:h=4.8 if x<-13 else 2.2
    rear=2.8+.018*(-x)+.18*math.sin(x*.32+d*.21)+.14*math.sin(d*.68+x*.4)
    y=h+(rear-h)*smooth(0,8,d)
    old=hit(lt,x,z)
    if old is not None and d<2.8:y=max(y,old+.012)
    return y
def simplemat(name,color):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=1
    return m
floor_mat=simplemat('PixelForest_Ground',(.19,.24,.12,1))
tex=floor_mat.node_tree.nodes.get('FloorPaint') or floor_mat.node_tree.nodes.new('ShaderNodeTexImage');tex.name='FloorPaint'
tex.image=bpy.data.images.load(str(A/'forest_floor.png'),check_existing=True)
floor_mat.node_tree.links.new(tex.outputs['Color'],floor_mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
rock=bpy.data.materials.get('InkIsland_Rock_Wash') or bpy.data.materials['Coast_Sculpted_Bedrock']
nx=80;nz=34;verts=[]
for j in range(nz+1):
    d=j*.56
    left=-18.6-5.8*smooth(0,10,d)
    right=2.7-5.0*smooth(0,17,d)+.40*math.sin(d*.5)*smooth(0,4,d)
    for i in range(nx+1):
        x=left+(right-left)*i/nx;z=front_z(x)-d
        edge=min(x-left,right-x)
        edge_drop=(1-smooth(0,1.5,edge))*(.7+.22*math.sin(d*.63))*smooth(0,4,d)
        rear_drop=1.1*smooth(16.5,19.1,d)
        verts.append(G(x,floor_y(x,z)-(.015 if j==0 else 0)-edge_drop-rear_drop,z))
faces=[];mids=[]
for j in range(nz):
    for i in range(nx):
        a=j*(nx+1)+i;b=a+nx+1;faces.extend([(a,a+1,b+1),(a,b+1,b)]);mids.extend([0,0])
# The island-side closure recedes behind the trees, using the existing bedrock material.
per=[j*(nx+1) for j in range(nz+1)]+[nz*(nx+1)+i for i in range(1,nx+1)]+[j*(nx+1)+nx for j in range(nz-1,-1,-1)]
prev=per
for fraction,outward in [(.16,.12),(.46,.48),(.76,.33),(1.0,.65)]:
    ring=[]
    for vi in per:
        v=verts[vi];normal=Vector((v.x+10,v.y-10,0)).normalized()
        shift=outward*(.82+.18*math.sin(v.x*1.7+v.y*.8))
        p=v+normal*shift;p.z=v.z+(-3.6-v.z)*fraction
        ring.append(len(verts));verts.append(p)
    for k in range(len(per)-1):
        faces.extend([(prev[k],ring[k],ring[k+1]),(prev[k],ring[k+1],prev[k+1])]);mids.extend([1,1])
    prev=ring
me=bpy.data.meshes.new('PixelForest_Low_Floor');me.from_pydata(verts,[],faces);me.update()
me.materials.append(floor_mat);me.materials.append(rock)
floor=bpy.data.objects.new('PixelForest_Low_Floor',me);current.objects.link(floor)
uv=me.uv_layers.new(name='ForestFloorUV')
for p,mi in zip(me.polygons,mids):
    p.material_index=mi;p.use_smooth=mi==0
    for li in p.loop_indices:
        v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x/12,v.y/12)
ft=BVHTree.FromPolygons([v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
D=json.loads((S/'scene-manifest.json').read_text(encoding='utf-8'))
sources={};materials={};imports=[]
for index in [1,3,5,6,7,8,9,11]:
    entry=next(v for k,v in D['meshes'].items() if k.endswith('/SM_zhuzi%03d.uasset'%index))
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=entry['gltf'])
    added=set(bpy.data.objects)-before
    ob=next(o for o in added if o.type=='MESH');me=ob.data.copy();me.transform(ob.matrix_world)
    bottom=min(v.co.z for v in me.vertices)
    rootverts=[v.co for v in me.vertices if v.co.z<bottom+.12]
    rx=sum(v.x for v in rootverts)/len(rootverts)
    for v in me.vertices:v.co-=Vector((rx,0,bottom))
    H=max(v.co.z for v in me.vertices)
    while len(me.uv_layers)>1:me.uv_layers.remove(me.uv_layers[-1])
    wind=me.uv_layers.new(name='WindWeight')
    for li in me.loops:wind.data[li.index].uv=(clamp(me.vertices[li.vertex_index].co.z/H),0)
    # A soft upward-facing foliage normal supports illumination while texture
    # pigment retains the authored pixel shading. Depth remains the real mesh.
    for p in me.polygons:p.use_smooth=True
    me.normals_split_custom_set([(0,-.88,.475)]*len(me.loops))
    tex_name=Path(D['materials'][entry['material_refs'][0]]['textures']['贴图']['png']).name
    if tex_name not in materials:
        mat=simplemat('PixelBamboo_'+tex_name.removesuffix('.png'),(1,1,1,1))
        nodes=mat.node_tree.nodes;bs=nodes.get('Principled BSDF')
        ti=nodes.get('PixelAtlas') or nodes.new('ShaderNodeTexImage');ti.name='PixelAtlas';ti.image=bpy.data.images.load(str(A/tex_name),check_existing=True);ti.interpolation='Closest'
        mat.node_tree.links.new(ti.outputs['Color'],bs.inputs['Base Color']);mat.node_tree.links.new(ti.outputs['Alpha'],bs.inputs['Alpha'])
        mat.surface_render_method='DITHERED';mat.diffuse_color=(1,1,1,1);mat.use_backface_culling=False
        materials[tex_name]=mat
    me.materials.clear();me.materials.append(materials[tex_name]);me.update()
    sources[index]=(me,H)
    imports.append(dict(source=entry['source'],triangles=entry['triangles'],texture=tex_name,root_offset=rx,height=H))
    for o in added:bpy.data.objects.remove(o,do_unlink=True)
rng=random.Random(911);placements=[]
def bamboo(index,x,z,height,width,layer,i):
    me,H=sources[index];y=hit(ft,x,z)
    if y is None:return
    ob=bpy.data.objects.new('PixelBamboo_L%d_%03d'%(layer,i),me);current.objects.link(ob)
    ob.location=G(x,y-.035,z)
    ob.rotation_euler.z=-.102+rng.uniform(-.09,.09)
    s=height/H;ob.scale=(s*width,s,s)
    ob['pixel_bamboo_layer']=layer;ob['reference_mesh']='SM_zhuzi%03d'%index
    ob['root_godot']=[x,y-.035,z]
    ob['pigment_variation']=rng.uniform(.88,1.08)
    # Set the bases of clustered culms onto the actual sloping forest floor.
    # Only the lower stem segment bends to meet it; crowns keep their artwork.
    bpy.context.view_layer.update()
    world=ob.matrix_world.copy();inverse=world.inverted()
    local=me.copy();ob.data=local
    for v in local.vertices:
        weight=1-smooth(.02*H,.32*H,v.co.z)
        if weight<=0:continue
        p=world@v.co;support=hit(ft,p.x,-p.y)
        if support is None:continue
        p.z+=(support-y)*weight
        v.co=inverse@p
    local.update()
    placements.append(dict(name=ob.name,source=index,root=[x,y-.035,z],height=height,layer=layer))
# Staggered bands deliberately overlap in height, with open roots at the path.
front=[(-18,-2.45),(-16.9,-3.2),(-15.5,-2.6),(-13.2,-2.2),(-12.7,-4.0),(-10.8,-3.0),(-9.5,-2.1),(-7.0,-2.8),(-6.3,-4.2),(-4.7,-2.4),(-2.7,-3.3),(-.9,-2.2),(.4,-3.2),(1.5,-2.8)]
for i,(x,z) in enumerate(front):
    bamboo([8,7,8,6][i%4],x,z,rng.uniform(5.5,6.6),rng.uniform(.98,1.25),0,i)
for layer,(depth,spacing,start,end) in enumerate([(4.9,1.04,-19.6,.7),(8.0,1.32,-21.2,-.4),(11.8,1.42,-22.8,-1.6),(16.4,1.38,-23.3,-3.0)],start=1):
    x=start;i=0
    while x<end:
        z=-depth+rng.uniform(-.56,.5)
        index=([8,7,8,6][i%4] if layer<2 else [9,8,11,7][i%4])
        height=(rng.uniform(5.5,6.6) if layer<2 else rng.uniform(6.0,7.5))
        bamboo(index,x,z,height,rng.uniform(.90,1.19),layer,i)
        x+=spacing*rng.uniform(.72,1.30);i+=1
report=dict(removed=[o.name for o in archive.objects],imported_sources=imports,placements=placements,collection=current.name,tree_count=len(placements),geometry_workflow='Blender MCP; original glTF meshes imported and arranged in Blender')
(O/'authoring.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export','exec'))
print('PIXEL_FOREST_EXPORTED',len(placements),'REMOVED',len(removed))
