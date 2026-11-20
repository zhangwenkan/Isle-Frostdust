"""Finish small plant contact and record actual final substrate roots."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/strict_coast_common.py',encoding='utf8').read(),'strict_coast_common.py','exec'))
assert not state.get('flower_contact_done')
ts=[ground_tree()]+[tree(SCENE.objects[n]) for n in state['rocks']]
def support(x,y):return max([h for h in [sample(t,x,y) for t in ts] if h is not None],default=None)
o=SCENE.objects['Forest_Strict_Flowers']
for start in range(0,len(o.data.vertices),28):
    vs=[o.data.vertices[start+j] for j in range(28)];base=sum((v.co for v in vs[:4]),Vector())/4;h=support(base.x,base.y)
    if h is None:continue
    for v in vs:v.co.z+=h+.008-base.z
o.data.update();state['flower_contact_done']=True
save('final-root-contact-review')
