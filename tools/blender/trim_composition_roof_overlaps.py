"""Cut exact exposed-rock footprints out of the underlying platform via MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf8').read(),'left_finish_common.py','exec'))
R=ROOT/'artifacts/rock-stair-composition-review'
LAYOUT=json.loads((R/'refined-layout.json').read_text(encoding='utf8'));state=LAYOUT['reference_cape']['rock_stair_composition']
assert not state.get('roof_trimmed')
archive=bpy.data.collections.get(state['archive'])
counts={}
for name in ['WALK_Forest_Ground','Cape_Terminus_Bedrock']:
 o=SCENE.objects[name];cp=o.copy();cp.data=o.data.copy();cp.name='Before_Roof_Trim_'+name;archive.objects.link(cp);cp.hide_set(True);cp.hide_render=True
 before=len(o.data.polygons)
 bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
 for n in state['rocks']:
  rock=SCENE.objects[n]
  mod=o.modifiers.new('Exact exposed stone footprint','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=rock;mod.use_hole_tolerant=True
  bpy.ops.object.modifier_apply(modifier=mod.name)
 counts[name]=[before,len(o.data.polygons)]
 assert len(o.data.polygons)>before*.55,'Unexpected major loss: inspect and restore before proceeding.'
state['roof_trimmed']=True;state['trim_face_counts']=counts
(R/'authoring-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf8')
(R/'trimmed-layout.json').write_text(json.dumps(LAYOUT,ensure_ascii=False,indent=2),encoding='utf8')
bpy.data.libraries.write(str(R/'trimmed-authoring.blend'),{SCENE},fake_user=True,compress=True)
print(json.dumps(counts))
