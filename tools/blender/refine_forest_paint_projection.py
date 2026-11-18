"""Correct painted forest coverage in the established camera projection via MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
REVIEW=ROOT/'artifacts/forest-layer-role-review';COL=bpy.data.collections['45_Forest_Layer_Roles']
report=json.loads((REVIEW/'build-report.json').read_text(encoding='utf-8'))
new_heights={'Near':1.4,'Middle':-6.3,'Depth':-20.4}
assert SCENE.objects['Forest_Paint_Depth'].get('projection_refined') is None
for key,z in new_heights.items():
    ob=SCENE.objects['Forest_Paint_'+key]
    old=next(c for c in report['carriers'] if c['name']==ob.name)
    delta=z-old['center'][2]
    for v in ob.data.vertices:v.co.z+=delta
    ob.data.update();ob['projection_refined']=True
    old['center'][2]=z
    for row in LAYOUT['forest_extension']['layer_roles']['painted_layers']:
        if row['name']==ob.name:row['center'][2]=z
# The old low-branch clumps at the joint still obscure the new horizontal band.
arch=bpy.data.collections['90_Rejected_Dense_Valley_Forest']
for name in ['Forest_Bamboo_06','Forest_Bamboo_Canopy_06','Forest_Bamboo_10','Forest_Bamboo_Canopy_10']:
    ob=SCENE.objects[name]
    for c in list(ob.users_collection):c.objects.unlink(ob)
    arch.objects.link(ob);ob.hide_render=True;ob.hide_set(True)
    report['archived'].append(name)
LAYOUT['forest_extension']['groves']=[g for g in LAYOUT['forest_extension']['groves'] if g['name'] not in report['archived']]
report['projection_correction']='Paint carriers descend into the valley with depth, instead of sitting above the current view.'
(REVIEW/'build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
export('forest-paint-projection')
