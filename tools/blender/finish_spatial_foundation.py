"""Close the sample's structural joints and the exposed cave backing via Blender MCP."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
root=Path('D:/自己做着玩的/孤屿霜尘');out=root/'assets/layered_island'
scene=bpy.data.scenes['Layered_Island_20261116'];bpy.context.window.scene=scene
assert not scene.get('spatial_finish',False)
col=bpy.data.collections['40_Spatial_Foundation'];cliff=scene.objects['Space_Continuous_Cliff']
bm=bmesh.new();bm.from_mesh(cliff.data);bm.verts.ensure_lookup_table()
mark=bm.faces.layers.int.new('Cap')
top_faces=[f for f in bm.faces if all(v.index>=45 for v in f.verts)]
for f in top_faces:f[mark]=1
edges=set(e for f in top_faces for e in f.edges)
bmesh.ops.subdivide_edges(bm,edges=list(edges),cuts=6,use_grid_fill=True)
for v in {v for f in bm.faces if f[mark]==1 for v in f.verts}:
    v.co.z=2.85+.72*max(0,min(1,(v.co.y-2.70)/1.24))-.024
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cliff.data);bm.free();cliff.data.update()
for name,height,old in [('West',1.72,2.45),('Main',2.05,2.64),('Stair',1.47,2.32),('Bridge',1.88,2.55)]:
    ob=scene.objects['Space_Rock_'+name]
    for v in ob.data.vertices:v.co.z=-.25+(v.co.z+.25)*(height+.25)/(old+.25)
    ob.data.update()
# Dark tunnel lining behind the existing painted opening. Its end is beyond
# the last playable anchor; no actor-depth hacks or transparent mountain walls.
mat=bpy.data.materials.new('SP_Cave_Lining');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.085,.103,.095,1);bs.inputs['Roughness'].default_value=1
center=Vector((10.574,1.519,2.96));axis=Vector((.961,1.305,0)).normalized();side=Vector((axis.y,-axis.x,0))
arch=[(-1.6,-.55),(-1.7,1.85),(-1.25,3.25),(-.35,3.8),(.65,3.65),(1.65,2.2),(1.65,-.55)]
vs=[center+axis*depth+side*x+Vector((0,0,z)) for depth in [.25,3.6] for x,z in arch]
fs=[(i,i+1,i+8,i+7) for i in range(6)]+[(6,0,7,13),tuple(range(7,14))]
mesh=bpy.data.meshes.new('Space_Cave_Lining');mesh.from_pydata(vs,[],fs);mesh.update()
ob=bpy.data.objects.new('Space_Cave_Lining',mesh);col.objects.link(ob);mesh.materials.append(mat)
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
uv=mesh.uv_layers.new(name='UVMap')
for loop in mesh.loops:
    p=mesh.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(p.x,p.z)
scene['spatial_finish']=True
layout=json.loads((out/'layout.json').read_text(encoding='utf-8'))
layout['camera']['physical_offset']=[0,20.5,35.14];layout['camera']['physical_fov']=16.3
live=[o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
layout['objects']=[{'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons)} for o in live]
(out/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.data.libraries.write(str(out/'layered_island.blend'),{scene},fake_user=True,compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in live:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=cliff
bpy.ops.export_scene.gltf(filepath=str(out/'layered_island.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
print('Closed top/side junction, lowered rock feet, added opaque cave lining')
