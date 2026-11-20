"""Reference proportion correction, spatial canopy and distant reef silhouettes."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/strict_coast_common.py',encoding='utf8').read(),'strict_coast_common.py','exec'))
import ast
assert not state.get('proportion_polish')
def factor(x):return .62+.38*sm(-61,-49,x)
# Environment proportions change; character source images and animations do not.
for name in ['WALK_Forest_Ground','Cape_Terminus_Bedrock','Forest_Near_Closed_Skirt']:
    o=SCENE.objects[name];keep(o)
    for v in o.data.vertices:
        if v.co.x<-49:v.co.z*=factor(v.co.x)
    o.data.update()
for o in list(SCENE.objects):
    if not live(o):continue
    if o.name.startswith(('Cape_Strict_','Cape_Fire_','Cape_Flame_','Cape_Smoke_','Cape_Ember_','Cape_Timber_')):
        keep(o)
        for v in o.data.vertices:v.co.z*=factor(v.co.x)
        o.data.update()
# Keep every bamboo's height and root attachment after changing the ground.
for row in state['plants']:
    old=Vector(row['root']);new=old.copy();new.z*=factor(old.x);delta=new-old;row['root']=list(new)
    num=row['name'].rsplit('_',1)[1]
    for kind in ['Bamboo','Leaves']:
        o=SCENE.objects['Forest_Strict_'+kind+'_'+num]
        for v in o.data.vertices:v.co+=delta
        if kind=='Leaves':
            for start in range(0,len(o.data.vertices),15):
                vs=[o.data.vertices[start+j] for j in range(15)];base=(vs[0].co+vs[2].co)*.5
                for v in vs:v.co=base+(v.co-base)*1.42
                for j in range(5):
                    mid=vs[j*3+1].co.copy()
                    for k in [0,2]:vs[j*3+k].co=mid+(vs[j*3+k].co-mid)*1.60
        o.data.update();LAYOUT['forest_extension']['layer_roles']['wind_bindings'][o.name]['root']=[new.x,new.z,-new.y]
# Rooted small plants move with their substrate; retain each blade's own height.
old_ground_tree=tree(SCENE.objects['Strict_Before_WALK_Forest_Ground'])
for name in ['Forest_Strict_Grass','Forest_Strict_Understory','Forest_Strict_Flowers']:
    o=SCENE.objects[name]
    # A smooth local ground drop applies to the entire plant at its own x.
    for v in o.data.vertices:
        p=v.co;f=factor(p.x);p.z-=height_at(old_ground_tree,p.x,p.y)*(1-f)
    o.data.update()
# Re-snap roots on cap planes after reducing their roof peaks.
new_support_trees=[ground_tree()]+[tree(SCENE.objects[n]) for n in state['rocks']]
for row in state['plants']:
    old=Vector(row['root']);hits=[h for h in [sample(t,old.x,old.y) for t in new_support_trees] if h is not None]
    new=old.copy();new.z=max(hits)+.012;delta=new-old;row['root']=list(new);num=row['name'].rsplit('_',1)[1]
    for kind in ['Bamboo','Leaves']:
        o=SCENE.objects['Forest_Strict_'+kind+'_'+num]
        for v in o.data.vertices:v.co+=delta
        o.data.update();LAYOUT['forest_extension']['layer_roles']['wind_bindings'][o.name]['root']=[new.x,new.z,-new.y]
for p in state['grass_roots']:p[2]*=factor(p[0])
for key,p in LAYOUT['anchors'].items():
    if p[0]<-49 and key!='cape_stair_bottom' and key not in ['cape_sand','cape_shore_end']:p[1]*=factor(p[0])
for key in ['fire_center','seat_center']:rc[key][1]*=factor(rc[key][0])
# Flatten conical cap centers into broad slant planes, keeping broken side faces.
for name in state['rocks']:
    o=SCENE.objects[name];zmax=max(v.co.z for v in o.data.vertices);zmin=min(v.co.z for v in o.data.vertices);limit=zmax-(zmax-zmin)*.085
    for v in o.data.vertices:
        if v.co.z>limit:v.co.z=limit+(v.co.z-limit)*.18
    o.data.update()
# Rebuild 16 treads over a 4.8m run; worn stone supports the full imported route.
top=Vector((-63.3,8.8,6.22*.62));bottom=Vector((-62.5,4.0,.15));axis=bottom-top;axis.z=0;length=axis.length;axis.normalize();side=Vector((-axis.y,axis.x,0));steps=16;width=2.25
stair=Mesh('Strict_Stair_16');support=Mesh('Strict_Stair_Solid_16')
for i in range(steps):
    z=top.z-(top.z-bottom.z)*i/steps;c=top+axis*(length*i/steps);depth=length/steps+.025
    cuts=[-.5,-.15,.23,.5] if i%2==0 else [-.5,.04,.5]
    for a,b in zip(cuts,cuts[1:]):
        poly=[c+side*(a*width+.006)-axis*.02,c+side*(b*width-.006)-axis*.02,c+side*(b*width-.018)+axis*depth,c+side*(a*width+.017)+axis*(depth+.007)]
        for p in poly:p.z=z
        low=[p-Vector((0,0,.24)) for p in poly];stair.part(poly,[(0,1,2,3)],'strict_cap')
        for j in range(4):n=(j+1)%4;stair.part([low[j],low[n],poly[n],poly[j]],[(0,1,2,3)],'strict_face')
    poly=[c+side*(-width/2)-axis*.025,c+side*(width/2)-axis*.025,c+side*(width/2)+axis*(depth+.025),c+side*(-width/2)+axis*(depth+.025)]
    for p in poly:p.z=z-.035
    low=[Vector((p.x,p.y,-.55)) for p in poly];support.part(poly,[(0,1,2,3)],'strict_face')
    for j in range(4):n=(j+1)%4;support.part([low[j],low[n],poly[n],poly[j]],[(0,1,2,3)],'strict_face')
replace('WALK_Cape_Stairs',stair.build());replace('Cape_Stair_Support',support.build())
LAYOUT['anchors']['cape_stair_bottom']=[bottom.x,bottom.z,-bottom.y];rc['stairs'].update(top=[top.x,top.z,-top.y],bottom=LAYOUT['anchors']['cape_stair_bottom'],steps=steps,width=width)
# Lower the submerged margin decisively; fill no visible vertical platter edge.
for name in ['WALK_Cape_Sand','Cape_Swash_Film']:
    o=SCENE.objects[name]
    for v in o.data.vertices:
        p=v.co;idx=max(0,min(31,round((p.x+68.5)/14*31)));sy=-rc['shoreline'][idx][1]
        if p.y<sy-.15:p.z=-.2-1.35*sm(sy-.15,sy-3,p.y)
        if p.x<-67.7 or p.x>-55.2:p.z-=.25
    o.data.update()
# Independently authored uneven low island ridges and narrow sea stacks.
for o in list(SCENE.objects):
    if live(o) and o.name.startswith('Cape_Distant_Islet_'):retire(o)
def ridge(name,cx,cy,width,depth,heights,turn):
    b=Mesh(name);cs=math.cos(turn);sn=math.sin(turn);n=len(heights);vs=[]
    for sideidx,y in enumerate([-depth/2,0,depth/2]):
        for j,h in enumerate(heights):
            x=-width/2+width*j/(n-1);z=h*(.33 if sideidx in [0,2] else 1);yy=y+(j%3-.8)*depth*.06
            vs.append((cx+x*cs-yy*sn,cy+x*sn+yy*cs,z-.3))
    fs=[]
    for i in range(2):
        for j in range(n-1):a=i*n+j;fs.extend([(a,a+1,a+n+1),(a,a+n+1,a+n)])
    for i in range(n-1):fs.append((i,i+1,2*n+i+1,2*n+i))
    fs.extend([(0,n,2*n),(n-1,3*n-1,2*n-1)]);b.part(vs,fs,'strict_face');o=b.build();state.setdefault('distant_reefs',[]).append(o.name)
ridge('Cape_Distant_Islet_Strict_0',-120,103,31,10,[.4,2,4.3,3.8,7.7,8.4,6.2,6.8,3.0,.7],.12)
ridge('Cape_Distant_Islet_Strict_1',-93,144,8,5,[.1,2.9,8.9,3.2,6.2,.3],-.13)
ridge('Cape_Distant_Islet_Strict_2',-77,112,5.0,4,[.1,4.8,9.4,8.1,.2],.1)
ridge('Cape_Distant_Islet_Strict_3',-60,180,31,8,[.2,2.0,4.6,3.2,5.4,4.0,2.4,.3],-.14)
rc['distant_islets']=state['distant_reefs'];state['proportion_polish']={'cliff_scale':.62,'tree_height_preserved':True,'steps':steps,'stair_run':length,'leaf_length_scale':1.42,'leaf_width_extra_scale':1.60,'reefs':'hand composed ridge height profiles, not block masses'}
state['stairs'].update(steps=steps,run=length,width=width)
save('proportion-reefs')
