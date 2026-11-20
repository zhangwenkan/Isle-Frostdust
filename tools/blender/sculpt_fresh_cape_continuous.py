"""Continuous stone sculpt and clustered bamboo shadows, via Blender MCP."""
import bpy,bmesh,math,json
from mathutils import Vector
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Fresh_Pixel_Cape'];bpy.context.window.scene=scene
assert scene['revision']=='fresh-cape-reference-polish-2'
rockcol=bpy.data.collections['Fresh_02_Rock_Faces'];bamboo=bpy.data.collections['Fresh_05_Bamboo']

def active(ob):
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob

# Fuse the same new sample's bedrock into a continuous sculpt. Editable
# pre-sculpt meshes are preserved outside the exporting scene.
archive=bpy.data.collections.new('Archive_New_Sample_Clipped_Beds')
selected=[o for o in rockcol.objects if o.type=='MESH' and 'Bamboo' not in o.name]
for ob in selected:
    saved=ob.copy();saved.data=ob.data.copy();saved.name='Archive_'+ob.name;archive.objects.link(saved);saved['fresh_sample']=False
active(selected[0])
for ob in selected:ob.select_set(True)
bpy.ops.object.convert(target='MESH');bpy.ops.object.join()
cliff=bpy.context.object;cliff.name='Rock_Continuous_Sculpted_Beds'
rem=cliff.modifiers.new('Fuse natural bedrock seams','REMESH');rem.mode='VOXEL';rem.voxel_size=.075;rem.use_smooth_shade=True
bpy.ops.object.modifier_apply(modifier=rem.name)
sm=cliff.modifiers.new('Round eroded arrises','SMOOTH');sm.factor=1.1;sm.iterations=5
bpy.ops.object.modifier_apply(modifier=sm.name)
tex=bpy.data.textures.new('Fresh_Medium_Stone_Relief',type='CLOUDS');tex.noise_scale=.47;tex.noise_depth=1
disp=cliff.modifiers.new('Mid scale chiseled erosion','DISPLACE');disp.texture=tex;disp.strength=.26;disp.mid_level=.5;disp.texture_coords='GLOBAL'
bpy.ops.object.modifier_apply(modifier=disp.name)
sm=cliff.modifiers.new('Remove subpixel bumps','SMOOTH');sm.factor=.5;sm.iterations=2
bpy.ops.object.modifier_apply(modifier=sm.name)
dec=cliff.modifiers.new('Retain sculpt planes','DECIMATE');dec.ratio=.24
bpy.ops.object.modifier_apply(modifier=dec.name)
cliff.data.materials.clear();cliff.data.materials.append(bpy.data.materials['Fresh_Rock_Base'])
for p in cliff.data.polygons:p.material_index=0;p.use_smooth=True
# Local directions remain hard only at genuine breaks.
bm=bmesh.new();bm.from_mesh(cliff.data)
for e in bm.edges:
    if len(e.link_faces)==2:e.smooth=e.calc_face_angle()<math.radians(47)
bm.to_mesh(cliff.data);bm.free()
uv=cliff.data.uv_layers.get('UVMap') or cliff.data.uv_layers.new(name='UVMap')
for li,l in enumerate(cliff.data.loops):
    p=cliff.data.vertices[l.vertex_index].co;uv.data[li].uv=(p.x*.2,p.z*.2+p.y*.05)
cliff['fresh_sample']=True;cliff['authored_from']='continuous sculpt of only this new sample'

# Leaf normal clusters do not cast thousands of small self-shadow flecks.
# Proxy meshes are Blender-authored and shown as shadows only in Godot.
for ob in list(bamboo.objects):
    if 'Bamboo_Leaf_Cluster' not in ob.name:continue
    c=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
    bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=2,radius=1)
    for v in bm.verts:v.co=Vector((v.co.x*.69,v.co.y*.29,v.co.z*.22))+c+Vector((0,.08,-.13))
    me=bpy.data.meshes.new(ob.name+'_shadowmesh');bm.to_mesh(me);bm.free()
    proxy=bpy.data.objects.new(ob.name.replace('Leaf_Cluster','Shadow_Proxy'),me);bamboo.objects.link(proxy)
    me.materials.append(bpy.data.materials['Fresh_Bamboo_Leaf_Dark'])
    uv=me.uv_layers.new(name='UVMap')
    for li,l in enumerate(me.loops):
        p=me.vertices[l.vertex_index].co;uv.data[li].uv=(p.x*.1,p.y*.1+p.z*.1)
    proxy['fresh_sample']=True;proxy['authored_from']='cluster shadow proxy'
    # Maintain outward/up normals even on a leaf seen from its reverse side.
    normals=[]
    for l in ob.data.loops:
        q=ob.data.vertices[l.vertex_index].co-c
        normals.append(tuple(Vector((q.x*.5,q.y*.8-.13,q.z*1.1+.85)).normalized()))
    ob.data.normals_split_custom_set(normals)

scene['revision']='fresh-cape-reference-polish-3'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/fresh_pixel_cape/fresh_pixel_cape.blend'))
print(json.dumps({'revision':scene['revision'],'cliff_vertices':len(cliff.data.vertices),'cliff_faces':len(cliff.data.polygons)}))
