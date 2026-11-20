"""Remove only the visually picked duplicate steep lip; keep valid hillside."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf8').read(),'left_finish_common.py','exec'))
R=ROOT/'artifacts/rock-stair-composition-review';state=LAYOUT['reference_cape']['rock_stair_composition']
assert not state.get('local_lip_trimmed')
o=SCENE.objects['WALK_Forest_Ground'];archive=bpy.data.collections[state['archive']]
cp=o.copy();cp.data=o.data.copy();cp.name='Before_Picked_Lip_Trim_Ground';archive.objects.link(cp);cp.hide_set(True);cp.hide_render=True
bm=bmesh.new();bm.from_mesh(o.data);bad=[]
for f in bm.faces:
 c=f.calc_center_median()
 if -55.9<c.x<-54.25 and -.1<c.y<2.1 and abs(f.normal.x)>.72 and f.normal.z<.72:bad.append(f)
assert len(bad)<200,'Scope too broad: leave source intact and inspect.'
bmesh.ops.delete(bm,geom=bad,context='FACES');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
state['local_lip_trimmed']=True;state['local_lip_removed_faces']=len(bad)
export('rock-stair-composition-local-lip-review')
(R/'authoring-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'localized_removed_faces':len(bad)}))
