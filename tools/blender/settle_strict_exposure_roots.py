"""Settle vegetation after the three final attached rock exposures."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/strict_coast_common.py',encoding='utf8').read(),'strict_coast_common.py','exec'))
assert not state.get('exposure_roots_done')
ts=[ground_tree()]+[tree(SCENE.objects[n]) for n in state['rocks']]
def support(x,y):return max([h for h in [sample(t,x,y) for t in ts] if h is not None],default=None)
for name in ['Forest_Strict_Grass','Forest_Strict_Understory']:
    o=SCENE.objects[name]
    for start in range(0,len(o.data.vertices),15):
        vs=[o.data.vertices[start+j] for j in range(15)];base=(vs[0].co+vs[2].co)*.5;h=support(base.x,base.y)
        if h is None:continue
        delta=h+.008-base.z
        for v in vs:v.co.z+=delta
    o.data.update()
state['exposure_roots_done']=True;save('final-contact-review')
