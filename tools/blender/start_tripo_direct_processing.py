"""Import user's Tripo asset as the actual editable baseline via Blender MCP."""
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/tripo-direct-rock-review';OUT.mkdir(exist_ok=True)
ASSET=ROOT/'assets/layered_island/tripo_coast';ASSET.mkdir(exist_ok=True)
FILE=Path('C:/Users/51440/Downloads/bccfc00f-d7ae-4bae-abab-5cc7e8c254e6.glb')
assert hashlib.sha256(FILE.read_bytes()).hexdigest()=='e51a58a5a6d60e8c2c3334d44a0509e16c6475ac73c2bed97051d74d05679bd2'
NAME='Tripo_Coast_Processing_20261119';assert not bpy.data.scenes.get(NAME),'Inspect already-created editable scene.'
old=bpy.context.window.scene;s=bpy.data.scenes.new(NAME);bpy.context.window.scene=s
bpy.ops.import_scene.gltf(filepath=str(FILE))
objects=[o for o in s.objects if o.type=='MESH'];assert len(objects)==1
o=objects[0];o.name='Tripo_Coast_Original_Surface';o['source']='User-supplied Tripo GLB'
col=bpy.data.collections.new('Tripo_Coast_Editable');s.collection.children.link(col)
for c in list(o.users_collection):c.objects.unlink(o)
col.objects.link(o)
bm=bmesh.new();bm.from_mesh(o.data)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000002)
bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table();bm.faces.ensure_lookup_table()
unseen=set(bm.verts);components=[]
while unseen:
    todo=[unseen.pop()];part=[]
    while todo:
        v=todo.pop();part.append(v)
        for e in v.link_edges:
            q=e.other_vert(v)
            if q in unseen:unseen.remove(q);todo.append(q)
    if len(part)>2:
        coords=[v.co for v in part]
        components.append({'vertices':len(part),'bounds':[[min(v[k] for v in coords) for k in range(3)],[max(v[k] for v in coords) for k in range(3)]]})
bound=[e for e in bm.edges if e.is_boundary]
boundary_vertices=set(v for e in bound for v in e.verts);loops=[]
while boundary_vertices:
    todo=[boundary_vertices.pop()];part=[]
    while todo:
        v=todo.pop();part.append(v)
        for e in v.link_edges:
            if not e.is_boundary:continue
            q=e.other_vert(v)
            if q in boundary_vertices:boundary_vertices.remove(q);todo.append(q)
    loops.append({'vertices':len(part),'bounds':[[min(v.co[k] for v in part) for k in range(3)],[max(v.co[k] for v in part) for k in range(3)]]})
report={'source':str(FILE),'source_sha256':hashlib.sha256(FILE.read_bytes()).hexdigest(),
 'original_vertices':len(o.data.vertices),'original_faces':len(o.data.polygons),
 'diagnostic_welded_vertices':len(bm.verts),'boundary_edges':len(bound),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
 'components':sorted(components,key=lambda a:-a['vertices'])[:30],
 'boundary_loops':sorted(loops,key=lambda a:-a['vertices'])[:40],
 'textures':[{'name':n.image.name,'size':list(n.image.size)} for m in o.data.materials for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image],
 'scope':'Direct editable Tripo original. Inspection only, no visible geometry altered.'}
bm.free();(OUT/'original-inspection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
for m in o.data.materials:
    for n in m.node_tree.nodes:
        if n.type=='TEX_IMAGE' and n.image:n.image.pack()
o['original_faces']=len(o.data.polygons);s['revision']='pristine-user-tripo-import'
bpy.data.libraries.write(str(ASSET/'tripo_coast_editable.blend'),{s},fake_user=True,compress=True)
bpy.context.window.scene=old
print(json.dumps(report,ensure_ascii=False))
