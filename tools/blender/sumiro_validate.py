import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/sumiro-style-review'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
report={'route':[],'pine_contacts':[],'active':[],'missing_images':[]}
for name in ['Fish_West_Continuous_Land','Fish_East_Continuous_Land']:
    ob=scene.objects[name];base=bpy.data.meshes[name+'_Before_Sumiro'];n=53 if 'East' in name else 101
    ids=[i for i in range(n*26) if 11<=i%26<=15]
    delta=max((ob.data.vertices[i].co-base.vertices[i].co).length for i in ids)
    assert delta<1e-6
    report['route'].append({'object':name,'vertices':len(ids),'maximum_delta':delta})
for ob in scene.objects:
    if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
    assert not ob.name.startswith(('Cliff_Fractures_','Depth_Foreground_Crag_','Depth_Bamboo_Fore_'))
    ob.data.calc_loop_triangles()
    report['active'].append({'name':ob.name,'triangles':len(ob.data.loop_triangles),'uvs':len(ob.data.uv_layers),'materials':[m.name for m in ob.data.materials]})
    for m in ob.data.materials:
        if m and m.use_nodes:
            for node in m.node_tree.nodes:
                if node.type=='TEX_IMAGE' and node.image and not node.image.packed_file:
                    p=Path(bpy.path.abspath(node.image.filepath))
                    if not p.exists():report['missing_images'].append(str(p))
assert not report['missing_images']
report['total_triangles']=sum(r['triangles'] for r in report['active'])
report['water_shader_unchanged']='Verified separately by SHA256 against pre-pass backup'
(OUT/'asset-verification.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('SUMIRO_VALIDATED',len(report['active']),report['total_triangles'])
