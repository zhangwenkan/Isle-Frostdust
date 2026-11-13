"""Run inside Blender ONLY through blender-mcp execute_blender_code.
Shared authoring primitives, original texture work, and scene setup.
"""
import bpy, bmesh, math, random, json
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = Path('D:/自己做着玩的/孤屿霜尘')
OUT = ROOT/'assets/island_blender'
R = random.Random(73611)
WATER = -2.1
if 'Island_Refined' not in bpy.data.scenes:
    if not (ROOT/'artifacts/blender/pre-existing-session.blend').exists():
        bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'artifacts/blender/pre-existing-session.blend'),copy=True)
    scene = bpy.data.scenes.new('Island_Refined')
    bpy.context.window.scene = scene
else:
    scene = bpy.data.scenes['Island_Refined']
    bpy.context.window.scene = scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.world = bpy.data.worlds.new('Maritime_Ambient')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.44,0.68,0.76,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.35

COL = {}
for name in ['01_Terrain','02_Cliff_Strata','03_Weathered_Rocks','04_Pine_Trees','05_Bamboo','06_Ferns_Grass','07_Bridge','08_Sea_Reefs','09_Distant_Isles','10_Foreground','11_Sea_Surface','12_Birds','90_Presentation']:
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    COL[name] = c

def G(p):
    return Vector((p[0],-p[2],p[1]))

def height(x,z):
    if x>10: return 1.15+math.sin(x*.37)*.18+max(0,-z)*.16
    return 1.65+(4.5-x)*.127+math.sin(x*.39)*.16+math.cos(z*1.3+x*.21)*.1+max(0,-z-.3)*.23

def path_z(x):
    return .25 if 4.5<=x<=14 else .4+math.sin(x*.25)*.44

def bridge_y(x):
    f=max(0,min(1,(x-4.2)/10.3))
    return height(4.2,.25)*(1-f)+height(14.5,.25)*f-math.sin(f*math.pi)*.48

def srgb(v):
    return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4

def rgb(hexcode):
    return tuple(srgb(int(hexcode[i:i+2],16)/255) for i in (0,2,4))+(1,)

def material(name,color,rough=0.92):
    m=bpy.data.materials.new(name); m.diffuse_color=rgb(color); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=m.diffuse_color
    p.inputs['Roughness'].default_value=rough
    m.use_backface_culling=False
    return m

MAT={}
for name,color in {
    'rock':'9eaa9d','rock_light':'b8b8a1','rock_dark':'657970','wet_rock':'405e5b',
    'earth':'918365','grass':'617e3c','moss':'647f40','moss_light':'879c50',
    'path':'c7ba92','bark':'665342','bark_light':'8b7760','bark_dark':'3d3c31',
    'wood':'a08a61','wood_end':'c0ab7c','wood_dark':'61533e','rope':'b7a579','rope_dark':'8b7c59',
    'pine_dark':'193e31','pine':'2f5c35','pine_light':'537b3e','pine_tip':'7a9b4b',
    'bamboo':'517e48','bamboo_light':'86a15d','bamboo_node':'c0bc85',
    'leaf_dark':'235637','leaf':'43824a','leaf_tip':'79a354',
    'grass_dark':'3b622e','grass_mid':'6e8c3e','grass_tip':'9fae58','dry_grass':'b9ae75',
    'bird_white':'e4e7da','bird_grey':'8aa2a0','bird_dark':'354d52',
    'ocean':'258d9c','foam':'d9f1e2','distant':'8bb5b5',
}.items(): MAT[name]=material(name,color)

def texture(name,kind):
    n=256
    y,x=np.mgrid[0:n,0:n].astype(np.float32)
    nr=np.random.default_rng(123+len(name))
    coarse=nr.random((32,32)).repeat(8,0).repeat(8,1)
    fine=nr.random((n,n))
    if kind=='rock':
        bands=np.sin(y*.13+np.sin(x*.022)*2+np.sin(x*.09)*.5)
        shade=.90+coarse*.10+fine*.035+bands*.055
        crack=(np.mod(y+7*np.sin(x*.021)+2*np.sin(x*.13),45)<1.3)
        shade-=crack*.20
    elif kind=='wood':
        grain=np.sin(y*.58+np.sin(x*.025)*2+np.sin(x*.07+y*.016))
        shade=.82+coarse*.08+fine*.04+grain*.10
        for cx,cy in [(55,74),(184,192)]:
            ell=np.sqrt(((x-cx)/2.6)**2+((y-cy)*1.8)**2)
            shade-=np.exp(-ell*.18)*.28
    elif kind=='bark':
        ridge=np.sin(x*.38+np.sin(y*.06)*.8)
        shade=.78+coarse*.16+ridge*.13
        shade-=((ridge<-.85)&(fine>.3))*.14
    elif kind=='path':
        shade=.88+coarse*.12+fine*.06
        for _ in range(240):
            px,py=nr.integers(0,n,2); rx,ry=nr.integers(1,4,2)
            mask=((x-px)/rx)**2+((y-py)/ry)**2<1
            shade[mask]*=nr.uniform(.62,1.12)
    else:
        shade=.86+coarse*.17+fine*.06+np.sin(x*.08+y*.03)*.025
    # Generated image pixels are written directly to the sRGB PNG by Blender.
    linear=np.array(MAT[name].diffuse_color[:3])
    base=np.where(linear<=.0031308,linear*12.92,1.055*np.power(linear,1/2.4)-.055)
    arr=np.ones((n,n,4),dtype=np.float32)
    arr[:,:,:3]=np.clip(shade[:,:,None]*base,0,1)
    image=bpy.data.images.new('Handcrafted_'+name,n,n,alpha=True)
    image.pixels.foreach_set(arr.flatten())
    image.filepath_raw=str(OUT/'textures'/f'{name}.png'); image.file_format='PNG'; image.save(); image.pack()
    node=MAT[name].node_tree.nodes.new('ShaderNodeTexImage'); node.image=image; node.interpolation='Closest'
    MAT[name].node_tree.links.new(node.outputs['Color'],MAT[name].node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    return image

for key,kind in [('rock','rock'),('rock_light','rock'),('wet_rock','rock'),('grass','grass'),('moss','grass'),('path','path'),('bark','bark'),('wood','wood')]: texture(key,kind)

def mesh(name,verts,faces,matkeys,col,indices=None,smooth=False,uv_scale=.35):
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata([G(v) for v in verts],[],faces); me.update()
    ob=bpy.data.objects.new(name,me); COL[col].objects.link(ob)
    for key in matkeys: me.materials.append(MAT[key])
    if indices:
        me.polygons.foreach_set('material_index',indices)
    me.polygons.foreach_set('use_smooth',[smooth]*len(me.polygons))
    uv=me.uv_layers.new(name='UVMap')
    coords=np.empty((len(me.loops),2),dtype=np.float32)
    for p in me.polygons:
        normal=p.normal
        dominant=max(range(3),key=lambda k:abs(normal[k]))
        axes=((1,2),(0,2),(0,1))[dominant]
        for li in p.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co
            coords[li]=(co[axes[0]]*uv_scale,co[axes[1]]*uv_scale)
    uv.data.foreach_set('uv',coords.flatten())
    return ob

class Batch:
    def __init__(self): self.v=[]; self.f=[]; self.mi=[]
    def add(self,vs,fs,idx=0):
        off=len(self.v); self.v.extend([tuple(v) for v in vs]); self.f.extend([tuple(off+i for i in f) for f in fs]); self.mi.extend([idx]*len(fs))
    def finish(self,name,mats,col,smooth=False): return mesh(name,self.v,self.f,mats,col,self.mi,smooth)

def tube(batch,points,radii,sides=9,idx=0):
    points=[Vector(p) for p in points]; vs=[]
    for i,p in enumerate(points):
        axis=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized()
        ref=Vector((0,0,1)) if abs(axis.z)<.90 else Vector((1,0,0))
        u=axis.cross(ref).normalized(); v=axis.cross(u).normalized()
        for j in range(sides):
            a=j*math.tau/sides
            vs.append(p+(math.cos(a)*u+math.sin(a)*v)*radii[i])
    fs=[]
    for i in range(len(points)-1):
        for j in range(sides):
            a=i*sides+j;b=i*sides+(j+1)%sides
            fs.append((a,b,b+sides,a+sides))
    fs.append(tuple(reversed(range(sides))))
    fs.append(tuple((len(points)-1)*sides+j for j in range(sides)))
    batch.add(vs,fs,idx)

def leaf(batch,start,end,width,bend=.07,idx=0):
    a=Vector(start);b=Vector(end);axis=(b-a).normalized()
    u=axis.cross(Vector((0,1,0)))
    if u.length<.01: u=Vector((1,0,0))
    u.normalize(); mid=a.lerp(b,.48)+Vector((0,bend,0))
    batch.add([a,mid-u*width,mid+Vector((0,.025,0)),mid+u*width,b],[(0,1,2),(0,2,3),(1,4,2),(2,4,3)],idx)

def bevel(ob,amount=.04,segments=2):
    mod=ob.modifiers.new('Worn softened edges','BEVEL');mod.width=amount;mod.segments=segments
    bpy.context.view_layer.objects.active=ob
    ob.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    ob.select_set(False)
    return ob

def save():
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'nameless_island.blend'))

bpy.app.driver_namespace['island_authoring']=globals()
print('Blender scene, original texture images, UV helpers and material palette ready.')
