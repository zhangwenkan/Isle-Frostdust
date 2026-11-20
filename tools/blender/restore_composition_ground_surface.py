"""Restore the intact pre-cleanup ground after visual diagnosis found over-removal."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf8').read(),'left_finish_common.py','exec'))
R=ROOT/'artifacts/rock-stair-composition-review';state=LAYOUT['reference_cape']['rock_stair_composition']
assert not state.get('ground_cleanup_reverted')
with bpy.data.libraries.load(str(R/'trimmed-authoring.blend'),link=False) as (src,dst):
 assert 'WALK_Forest_Ground' in src.objects;dst.objects=['WALK_Forest_Ground']
loaded=dst.objects[0];SCENE.objects['WALK_Forest_Ground'].data=loaded.data;bpy.data.objects.remove(loaded,do_unlink=True)
collection=bpy.data.collections[state['collection']]
for n in state['rocks']+['WALK_Cape_Stairs','Cape_Stair_Support']:
 o=SCENE.objects[n]
 if collection not in o.users_collection:collection.objects.link(o)
 for c in list(o.users_collection):
  if c!=collection:c.objects.unlink(o)
state['ground_cleanup_reverted']=True;state['cleanup_note']='The broad normal-based deletion removed valid sloped ground; restored exact intact pre-cleanup mesh.'
export('rock-stair-composition-intact-effect-review')
(R/'authoring-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf8')
