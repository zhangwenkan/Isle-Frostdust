"""Update only the existing rock material through Blender MCP; preserve meshes."""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path('D:/自己做着玩的/孤屿霜尘');REVIEW_DIR=ROOT/'artifacts/rock-wash-review'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
def signatures():
    results={}
    for ob in scene.objects:
        if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
        data={'positions':[list(v.co) for v in ob.data.vertices],'polygons':[list(p.vertices) for p in ob.data.polygons],
              'smooth':[p.use_smooth for p in ob.data.polygons],'uv':[[list(d.uv) for d in u.data] for u in ob.data.uv_layers]}
        results[ob.name]=hashlib.sha256(json.dumps(data).encode()).hexdigest()
    return results
before=signatures()
mat=bpy.data.materials['InkSample_Rock_Angular']
tex=next(n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE')
tex.image=bpy.data.images.load(str(ROOT/'assets/colored_ink_sample/rock_watercolor_planes.png'),check_existing=True);tex.image.reload()
assert signatures()==before
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
p=ROOT/'assets/island_blender/asset_manifest.json';m=json.loads(p.read_text(encoding='utf-8'))
m['revision']='Accepted angular rock shapes retained; softer face palette and broken watercolor edge marks'
ref='../../artifacts/rock-wash-review/README.md'
if ref not in m['source_manifests']:m['source_manifests'].append(ref)
p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
(REVIEW_DIR/'blender-material-verification.json').write_text(json.dumps({'unchanged_geometry_uv_and_smooth_flags':True,'mesh_count':len(before),'material':mat.name,'texture':tex.image.filepath},ensure_ascii=False,indent=2),encoding='utf-8')
print('ROCK_WASH_MATERIAL_EXPORTED; geometry unchanged')
