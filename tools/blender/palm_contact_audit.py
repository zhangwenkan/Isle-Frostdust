"""Check authored geometry through Blender MCP without mutating it."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Island_Refined']
bpy.context.window.scene=scene;bpy.context.view_layer.update()
ground=[]
for name in ['Fish_West_Continuous_Land','Fish_East_Continuous_Land']:
    ob=scene.objects[name]
    ground.append(BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons]))
def ray(x,z):
    hits=[b.ray_cast(Vector((x,-z,30)),Vector((0,0,-1))) for b in ground]
    return max((p.z for p,n,i,d in hits if p is not None),default=None)
def height(x,z):
    if x>10:return 1.15+math.sin(x*.37)*.18+max(0,-z)*.16
    return 1.65+(4.5-x)*.127+math.sin(x*.39)*.16+math.cos(z*1.3+x*.21)*.10+max(0,-z-.3)*.23
errors=[]
for lo,hi in [(-18,4.1),(14.7,23.7)]:
    for i in range(80):
        x=lo+(hi-lo)*i/79;z=.25 if 4.5<=x<=14 else .4+math.sin(x*.25)*.44
        y=ray(x,z);errors.append(abs(y-height(x,z)) if y is not None else 100)
palms=[]
for ob in scene.objects:
    if not ob.name.startswith('Coast_Palm_') or not ob.name.endswith('_Body'):continue
    x,z=ob.location.x,-ob.location.y;terrain=ray(x,z)
    metadata=json.loads((ROOT/'artifacts/palm-style-review/reference-lod-metadata.json').read_text())
    source=ob['source_mesh'].rsplit('_',1)[0]
    expected=metadata[source]['lod_info']['m_SubMeshes'][0]['m_Levels'][0]['m_IndexCount']//3
    ob.data.calc_loop_triangles()
    assert len(ob.data.loop_triangles)==expected,(ob.name,len(ob.data.loop_triangles),expected)
    palms.append({'name':ob.name,'origin_vs_ground':ob.location.z-terrain,'burial':ob.get('root_burial',.035),'uv_layers':len(ob.data.uv_layers),'vertices':len(ob.data.vertices),'lod0_triangles':expected})
materials=[]
for m in bpy.data.materials:
    if not m.name.startswith(('Fish_Rock_','Coast_Palm','Coast_Ground')):continue
    for n in m.node_tree.nodes:
        if n.type=='TEX_IMAGE' and n.image and ('Normal' in n.image.name):
            assert 'OpenGL' in n.image.name or 'Island_Ground_Normal' in n.image.name,n.image.name
            assert n.image.colorspace_settings.name=='Non-Color'
            materials.append({'material':m.name,'normal':n.image.name,'color_space':n.image.colorspace_settings.name})
old=[o.name for o in scene.objects if o.name.startswith(('Fish_Tree_','Fish_Tuft_'))]
assert max(errors)<.035,max(errors)
assert len(palms)==8 and all(abs(p['origin_vs_ground']+p['burial'])<.003 for p in palms)
assert not old,old
report={'path_samples':len(errors),'max_path_gap_m':max(errors),'palms':palms,'normal_maps':materials,'old_trees_and_grass':old}
(ROOT/'artifacts/palm-style-review/contact-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PALM_CONTACT_PASS',len(errors),'path samples, max gap',max(errors),'m; 8 grounded palms; corrected normal maps.')
