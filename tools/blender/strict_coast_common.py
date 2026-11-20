"""Shared modelling operations. Execute inside Blender via blender-mcp only."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
import random
R=ROOT/'artifacts/strict-forest-coast-review';T=OUT/'strict_coast';rc=LAYOUT['reference_cape']
COL=bpy.data.collections.get('54_Strict_Reference_Coast')
if not COL:COL=bpy.data.collections.new('54_Strict_Reference_Coast');SCENE.collection.children.link(COL)
ARCH=bpy.data.collections.get('90_Before_Strict_Reference_Coast')
if not ARCH:ARCH=bpy.data.collections.new('90_Before_Strict_Reference_Coast');SCENE.collection.children.link(ARCH)
state=rc.setdefault('strict_reference',{'collection':COL.name,'reference':'artifacts/forest-rocky-terminus-study/reference/user-forest-coast.png','changed':[],'retired':[],'rocks':[],'plants':[]})
def live(o):return o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)
def keep(o):
    if o.name in state['changed']:return
    cp=o.copy();cp.data=o.data.copy();cp.name='Strict_Before_'+o.name;ARCH.objects.link(cp);cp.hide_set(True);cp.hide_render=True;state['changed'].append(o.name)
def retire(o):
    state['retired'].append(o.name)
    for c in list(o.users_collection):c.objects.unlink(o)
    ARCH.objects.link(o);o.hide_set(True);o.hide_render=True
def replace(name,built):
    o=SCENE.objects[name];keep(o);o.data=built.data;bpy.data.objects.remove(built,do_unlink=True);return o
def texture_mat(name,file,color=(1,1,1,1)):
    m=bpy.data.materials.get(name)
    if m:return m
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=color;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color;p.inputs['Roughness'].default_value=.88
    if file:
        im=bpy.data.images.load(str(T/file),check_existing=True);im.reload();im.pack();n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
    return m
for k,f,c in [('face','rock_faces.png',(1,1,1,1)),('cap','rock_caps.png',(1,1,1,1)),('moss','moss.png',(1,1,1,1)),('soil','soil.png',(1,1,1,1)),('leaf','leaf.png',(1,1,1,1)),('culm',None,(.23,.32,.085,1)),('node',None,(.35,.41,.14,1)),('branch',None,(.18,.25,.055,1)),('grass',None,(.28,.37,.075,1)),('flower',None,(.73,.70,.39,1))]:MATS['strict_'+k]=texture_mat('StrictCoast_'+k,f,c)
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
def sample(t,x,y):
    p=t.ray_cast(Vector((x,y,45)),Vector((0,0,-1)))[0];return p.z if p else None
def ground_tree():return tree(SCENE.objects['WALK_Forest_Ground'])
def height_at(t,x,y):
    h=sample(t,x,y);return h if h is not None else t.find_nearest(Vector((x,y,5)))[0].z
def soften(o,width=.035):
    bm=bmesh.new();bm.from_mesh(o.data)
    edges=[e for e in bm.edges if e.is_manifold and e.calc_face_angle()>.35]
    if edges:bmesh.ops.bevel(bm,geom=edges,offset=width,segments=2,affect='EDGES',clamp_overlap=True)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
def save(label):export('strict-reference-'+label)
