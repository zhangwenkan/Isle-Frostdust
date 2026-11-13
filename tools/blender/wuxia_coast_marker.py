"""Blender MCP only: a small hand-set stone waymarker beside the western landing."""
import bpy, bmesh, json, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path('D:/自己做着玩的/孤屿霜尘')
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
name='16_Wuxia_Shore_Marker'
col=bpy.data.collections.get(name)
if col:
    for ob in list(col.objects):bpy.data.objects.remove(ob,do_unlink=True)
else:
    col=bpy.data.collections.new(name);scene.collection.children.link(col)

def rgb(s):
    vals=[int(s[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals)+(1,)

def material(name,color):
    mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=rgb(color)
    bsdf.inputs['Roughness'].default_value=.94
    return mat

stone=material('Wuxia_Marker_Stone','92968a')
edge=material('Wuxia_Marker_Base','737b70')
ink=material('Wuxia_Marker_Lettering','ffffff')
image=bpy.data.images.load(str(ROOT/'assets/wuxia_coast/Tingchao_Stone.png'),check_existing=True)
bsdf=ink.node_tree.nodes.get('Principled BSDF')
tex=next((n for n in ink.node_tree.nodes if n.type=='TEX_IMAGE'),None) or ink.node_tree.nodes.new('ShaderNodeTexImage')
tex.image=image;ink.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])

ground=scene.objects['Fish_West_Continuous_Land']
bvh=BVHTree.FromPolygons([ground.matrix_world@v.co for v in ground.data.vertices],[list(p.vertices) for p in ground.data.polygons])
x,y=2.65,-1.85
hit,normal,idx,distance=bvh.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))
assert hit is not None, 'Marker must sit on actual land'
base_z=hit.z-.07

def mesh(name,verts,faces,mat,bevel=0):
    me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);col.objects.link(ob);ob.location=(x,y,base_z)
    me.materials.append(mat)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    if bevel:
        mod=ob.modifiers.new('Worn stone edges','BEVEL');mod.width=bevel;mod.segments=2
        mod=ob.modifiers.new('Broad chisel faces','WEIGHTED_NORMAL');mod.keep_sharp=True
    return ob

# Slightly irregular shoulder and chamfered edges, readable without crack noise.
outline=[(-.39,-.04),(.34,-.04),(.30,.76),(.20,1.32),(-.17,1.23),(-.31,.82)]
verts=[(a,b,c) for b in [-.14,.14] for a,c in outline]
n=len(outline);faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]
faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
slab=mesh('Wuxia_Tingchao_Waymarker',verts,faces,stone,.028)
slab['purpose']='Original Tingchao coastal waymarker; hand-set beside the path, outside the walk corridor'
# A flush inset stone face carries original Kai-style lettering; it casts no extra silhouette.
face=mesh('Wuxia_Tingchao_Inscription',[(-.20,-.141,.20),(.20,-.141,.20),(.20,-.141,1.02),(-.20,-.141,1.02)],[(0,1,2,3)],ink)
uv=face.data.uv_layers.new(name='UVMap')
for loop,coords in zip(face.data.loops,[(0,0),(1,0),(1,1),(0,1)]):uv.data[loop.index].uv=coords

report={'authoring':'Blender 5.1 through blender-mcp','location_godot':[x,base_z,-y],
    'top_m':1.32,'width_m':.73,'new_objects':[ob.name for ob in col.objects],
    'terrain_hit_height':hit.z,'new_meshes':len(col.objects)}
(ROOT/'artifacts/wuxia-style-review/marker-authoring.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
manifest_path=ROOT/'assets/island_blender/asset_manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['revision']='Muted wuxia coast with original Blender-authored Tingchao stone marker; continuous sea retained'
manifest['source_manifests'].append('../wuxia_coast/SOURCES.md')
manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('WUXIA_MARKER_COMPLETE',json.dumps(report))
