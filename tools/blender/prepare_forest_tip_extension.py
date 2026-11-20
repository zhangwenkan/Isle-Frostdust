"""Restore the pre-ramp forest meshes and read the true attachment edge in Blender."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
O=ROOT/'artifacts/forest-tip-extension-review';assert not LAYOUT['reference_cape'].get('tip_prepared')
baseline=json.loads((ROOT/'artifacts/cape-forest-continuity-review/before/layout.json').read_text(encoding='utf-8'))
rejected=bpy.data.collections.new('90_Rejected_Separate_Forest_Ramp');SCENE.collection.children.link(rejected)
for name in LAYOUT['reference_cape']['forest_continuity']['changed_meshes']:
    ob=SCENE.objects[name];saved=ob.copy();saved.data=ob.data.copy();saved.name='RejectedRamp_'+name;rejected.objects.link(saved);saved.hide_set(True);saved.hide_render=True
    old=SCENE.objects.get('Continuity_Before_'+name)
    assert old,name
    ob.data=old.data.copy()
bank=SCENE.objects.get('Cape_Forest_Backbank')
if bank:
    for c in list(bank.users_collection):c.objects.unlink(bank)
    rejected.objects.link(bank);bank.hide_set(True);bank.hide_render=True
LAYOUT['anchors']=baseline['anchors'];LAYOUT['edges']=baseline['edges'];LAYOUT['forest_extension']=baseline['forest_extension']
LAYOUT['reference_cape']=baseline['reference_cape'];LAYOUT['reference_cape']['tip_prepared']=True
report={}
for name,x in [('WALK_Forest_Ground',-61.24),('WALK_Forest_NearSlope',-63.04)]:
    me=SCENE.objects[name].data
    points=sorted([list(v.co) for v in me.vertices if abs(v.co.x-x)<.005],key=lambda p:p[1])
    report[name]=points
(O/'attachment-edges.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
export('forest-tip-prepared')
print(json.dumps({k:{'count':len(v),'points':v} for k,v in report.items()}))
