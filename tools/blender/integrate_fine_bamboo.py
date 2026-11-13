"""Replace only western card carriers/materials, through Blender MCP."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/bamboo_fine';O=R/'artifacts/bamboo-fine-atlas-review'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
def active():return [o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
def signature(o):
    h=hashlib.sha256()
    for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
    for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
    for uv in o.data.uv_layers:
        for d in uv.data:h.update(str(tuple(d.uv)).encode())
    h.update(str(o.matrix_world).encode());return h.hexdigest()
signatures={o.name:signature(o) for o in active()}
manifest=json.loads((A/'atlas-manifest.json').read_text(encoding='utf-8'));variants={v['name']:v for v in manifest['variants']}
placements={p['name']:p for p in json.loads((R/'artifacts/pixel-bamboo-west-review/authoring.json').read_text(encoding='utf-8'))['placements']}
mapping={8:'slender_a',7:'slender_b',6:'slender_c',9:'cluster_a',11:'cluster_b'}
archive=bpy.data.collections.get('90_Before_Fine_Bamboo_Atlas') or bpy.data.collections.new('90_Before_Fine_Bamboo_Atlas')
if archive.name not in scene.collection.children:scene.collection.children.link(archive)
archive.hide_render=True
materials={}
for key,entry in variants.items():
    mat=bpy.data.materials.get('FineBamboo_'+key) or bpy.data.materials.new('FineBamboo_'+key);mat.use_nodes=True
    ns=mat.node_tree.nodes;ns.clear();lk=mat.node_tree.links
    out=ns.new('ShaderNodeOutputMaterial');bs=ns.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.95;lk.new(bs.outputs['BSDF'],out.inputs['Surface'])
    tex=ns.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(A/(key+'_color.png')),check_existing=True);tex.image.reload()
    lk.new(tex.outputs['Color'],bs.inputs['Base Color']);lk.new(tex.outputs['Alpha'],bs.inputs['Alpha'])
    norm=ns.new('ShaderNodeTexImage');norm.image=bpy.data.images.load(str(A/(key+'_normal.png')),check_existing=True);norm.image.colorspace_settings.name='Non-Color';norm.image.reload()
    nm=ns.new('ShaderNodeNormalMap');lk.new(norm.outputs['Color'],nm.inputs['Color']);lk.new(nm.outputs[0],bs.inputs['Normal'])
    mat.surface_render_method='DITHERED';mat.use_backface_culling=False;materials[key]=mat
floor=scene.objects['PixelForest_Low_Floor'];ft=BVHTree.FromPolygons([floor.matrix_world@v.co for v in floor.data.vertices],[tuple(p.vertices) for p in floor.data.polygons])
def ground(x,y):
    p=ft.ray_cast(Vector((x,y,50)),Vector((0,0,-1)))[0];return p.z if p else None
report=[]
for ob in list(active()):
    if not ob.name.startswith('PixelBamboo_'):continue
    saved=bpy.data.objects.get('FineAtlasBaseline_'+ob.name)
    if saved is None:
        saved=ob.copy();saved.data=ob.data.copy();saved.name='FineAtlasBaseline_'+ob.name;archive.objects.link(saved);saved.hide_render=True;saved.hide_set(True)
    p=placements[ob.name];key=mapping[p['source']];entry=variants[key]
    xmin,xmax,zmin,zmax=entry['plane_bounds'];nx=8;ny=30
    verts=[];faces=[]
    for j in range(ny+1):
        z=zmin+(zmax-zmin)*j/ny
        for i in range(nx+1):verts.append((xmin+(xmax-xmin)*i/nx,0,z))
    for j in range(ny):
        for i in range(nx):
            a=j*(nx+1)+i;b=a+nx+1;faces.append((a,a+1,b+1,b))
    me=bpy.data.meshes.new('FineCard_'+ob.name);me.from_pydata(verts,[],faces);me.materials.append(materials[key]);me.update()
    uv=me.uv_layers.new(name='FineAtlasUV');wind=me.uv_layers.new(name='WindWeight')
    for loop in me.loops:
        v=me.vertices[loop.vertex_index].co;uv.data[loop.index].uv=((v.x-xmin)/(xmax-xmin),(v.z-zmin)/(zmax-zmin))
        wind.data[loop.index].uv=(max(0,min(1,v.z/6)),0)
    ob.data=me
    width=saved.scale.x/saved.scale.z
    s=p['height']/6.0
    ob.scale=(s*width*(.60 if key.startswith('slender') else .78),s,s)
    ob.matrix_world.translation=saved.matrix_world.translation
    bpy.context.view_layer.update();matrix=ob.matrix_world.copy();inv=matrix.inverted();base=ob.location.z+.035
    for v in me.vertices:
        w=1-min(1,max(0,v.co.z/1.8))
        if w==0:continue
        pos=matrix@v.co;h=ground(pos.x,pos.y)
        if h is not None:pos.z+=(h-base)*w;v.co=inv@pos
    me.update();ob['fine_atlas_variant']=key;ob['fine_atlas_source']='Project eastern bamboo bake'
    report.append(dict(object=ob.name,variant=key,root=list(p['root']),target_height=p['height'],triangles=nx*ny*2))
preserved=[o for o in active() if not o.name.startswith('PixelBamboo_')]
assert all(signatures[o.name]==signature(o) for o in preserved)
(O/'integration.json').write_text(json.dumps(dict(cards=report,preserved_mesh_count=len(preserved),positions_and_layers_preserved=True,workflow='Blender MCP'),indent=2),encoding='utf-8')
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export','exec'))
print('FINE_ATLAS_INTEGRATED',len(report),'OTHER_MESHES_PRESERVED',len(preserved))
