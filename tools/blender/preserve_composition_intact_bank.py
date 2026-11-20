"""Keep the intact review surface: local lip deletion exposed an unacceptable slit."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf8').read(),'left_finish_common.py','exec'))
R=ROOT/'artifacts/rock-stair-composition-review';state=LAYOUT['reference_cape']['rock_stair_composition']
assert not state.get('intact_bank_preserved')
SCENE.objects['WALK_Forest_Ground'].data=SCENE.objects['Before_Picked_Lip_Trim_Ground'].data.copy()
state['intact_bank_preserved']=True;state['local_lip_trimmed']=False
state['remaining_visual_limits']=['Broad faces remain simplified','Near bank retains a long-wall impression','Local ground/rock lip remains; failed deletion was reverted to retain intact terrain']
export('rock-stair-composition-visual-review')
(R/'authoring-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf8')
