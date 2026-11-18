"""Targeted MCP framing correction following the prior bamboo atmosphere study."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
roles=LAYOUT['forest_extension']['layer_roles']
assert 'study_framing_correction' not in roles,'Inspect the saved correction; do not repeat it.'
changes=[]
for name,target in [('Forest_Paint_Near',5.6),('Forest_Paint_Middle',-1.3),('Forest_Mist_Front',7.5)]:
    rows=roles['painted_layers'] if name.startswith('Forest_Paint_') else roles['mist_layers']
    row=next(r for r in rows if r['name']==name)
    previous=row['center'][2];delta=target-previous
    ob=SCENE.objects[name]
    for vertex in ob.data.vertices:vertex.co.z+=delta
    ob.data.update();row['center'][2]=target
    changes.append({'name':name,'previous_z':previous,'z':target,'delta':delta})
roles['study_framing_correction']={'source':'artifacts/bamboo-atmosphere-source-study/README.md','changes':changes,'intent':'readable dark silhouettes in front of and behind local mist, not only faded stem ends'}
for im in bpy.data.images:
    if '/forest_layers/' in bpy.path.abspath(im.filepath).replace('\\','/'):im.reload();im.pack()
(ROOT/'artifacts/forest-wind-mist-review/blender-framing.json').write_text(json.dumps(roles['study_framing_correction'],indent=2),encoding='utf-8')
export('study-forest-layer-framing')
