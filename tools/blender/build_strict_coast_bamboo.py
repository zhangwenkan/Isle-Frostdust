"""Jointed bamboo, spatially branched lanceolate leaves and rooted understory."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/strict_coast_common.py',encoding='utf8').read(),'strict_coast_common.py','exec'))
assert state.get('landforms_done') and not state.get('bamboo_done')
ft=ground_tree();rt=[tree(SCENE.objects[n]) for n in state['rocks']];roles=LAYOUT['forest_extension']['layer_roles'];bindings=roles['wind_bindings'];rng=random.Random(391)
def support(x,y):
    hs=[v for v in [sample(t,x,y) for t in [ft]+rt] if v is not None];return max(hs) if hs else None
ret=[]
for name,bind in list(bindings.items()):
    if bind['root'][0]>-49:continue
    o=SCENE.objects.get(name)
    if o and live(o):retire(o);ret.append(name)
    del bindings[name]
LAYOUT['forest_extension']['groves']=[g for g in LAYOUT['forest_extension']['groves'] if g['name'] not in ret]
for name in ['Forest_Grass_Terminus','Forest_Grass_Terminus_Ferns']:
    if SCENE.objects.get(name) and live(SCENE.objects[name]):retire(SCENE.objects[name])
def wind_uv(o,root,h):
    for li,l in enumerate(o.data.loops):
        p=o.data.vertices[l.vertex_index].co;w=max(0,min(1,(p.z-root.z)/h))**1.8
        o.data.uv_layers[1].data[li].uv=(0,1-w)
def blade(b,base,direction,length,width,material='strict_leaf',droop=.2,weight=0):
    direction=Vector(direction).normalized();side=direction.cross(Vector((0,-.52,.85))).normalized()
    if side.length<.1:side=Vector((1,0,0))
    vs=[];uv=[]
    for t,f in [(0,.10),(.29,.8),(.57,1),(.81,.60),(1,0)]:
        p=Vector(base)+direction*length*t+Vector((0,0,-droop*t*t))
        vs.extend([p-side*width*f,p+Vector((0,0,width*.17*f)),p+side*width*f]);uv.extend([(0,t),(.5,t),(1,t)])
    fs=[]
    for k in range(4):
        a=k*3;fs.extend([(a,a+3,a+4,a+1),(a+1,a+4,a+5,a+2)])
    # Collapse only the last two panels to a true pointed tip, no zero-area faces.
    fs=fs[:-2]+[(9,12,10),(10,12,11)]
    b.part(vs,fs,material,uv,[weight]*len(vs))
def bamboo(num,x,y,h,r,seed,front=False):
    z=support(x,y)
    if z is None:return
    root=Vector((x,y,z+.012));body=Mesh('Forest_Strict_Bamboo_%02d'%num);leaves=Mesh('Forest_Strict_Leaves_%02d'%num);rr=random.Random(seed);bend=Vector((rr.uniform(-.4,.4),rr.uniform(-.2,.2),0))
    def center(v):return root+Vector((0,0,v))+bend*(v/h)**1.9
    joints=round(h/.55)
    tube(body,[center(j*h/joints) for j in range(joints+1)],[r*(1-.62*j/joints) for j in range(joints+1)],'strict_culm',12)
    for j in range(1,joints):
        v=j*h/joints;rad=r*(1-.62*v/h)
        tube(body,[center(v-.026),center(v-.012),center(v+.022),center(v+.033)],[rad,rad*1.16,rad*1.11,rad],'strict_node',12)
    # Lower sparse twigs and larger upper sprays grow out of real nodes.
    for k,fraction in enumerate([.30,.43,.55,.67,.77,.87,.95]):
        v=round(h*fraction/.55)*.55;v=min(h-.25,v)
        for s in range(2 if k>1 else 1):
            a=seed*.13+k*2.41+s*math.pi;direction=Vector((math.cos(a),math.sin(a)*.75,.18));start=center(v)
            length=[.70,.88,1.20,1.36,1.25,1.08,.80][k]*rr.uniform(.84,1.18)
            end=start+direction*length+Vector((0,0,.12));middle=start.lerp(end,.46)+Vector((0,0,.09))
            tube(body,[start,middle,end],[.022 if k<4 else .017,.011,.0035],'strict_branch',6)
            # Six lateral leaf pairs per twig, curving through depth, no large cards.
            for j in range(2,8):
                t=j/8;anchor=start.lerp(end,t)+Vector((0,0,.12*math.sin(t*math.pi)))
                across=Vector((-direction.y,direction.x,.08)).normalized()
                for sign in [-1,1]:
                    dl=(direction*.3+across*sign+Vector((0,0,-.12-.35*t))).normalized()
                    leaflen=rr.uniform(.34,.57)*(1-.22*t);blade(leaves,anchor,dl,leaflen,rr.uniform(.027,.043),droop=.14)
            blade(leaves,end,direction+Vector((0,0,-.2)),.38,.033,droop=.13)
    for o in [body.build(True),leaves.build(True)]:
        wind_uv(o,root,h);bindings[o.name]={'root':[root.x,root.z,-root.y],'height':h,'seed':seed,'amplitude':.49 if front else .58}
        LAYOUT['forest_extension']['groves'].append({'name':o.name,'band':'role_front' if front else 'role_main'})
    state['plants'].append({'name':body.name,'root':list(root),'height':h,'front':front})
# Irregular small stands in four depth bands, with the route opening retained.
sites=[(-65.0,18.2),(-64.3,17.9),(-63.1,18.6),(-62.5,18),(-60.8,17.8),(-60.1,18.5),(-58.5,17.9),(-57.8,18.6),(-56.0,17.5),(-54.9,18),(-53.6,17.1),(-51.8,17.6),(-50.4,17.9),
       (-64.9,20.1),(-64.0,20.8),(-62.5,20.0),(-61.4,20.8),(-59.8,20),(-58.1,20.7),(-56.7,20.1),(-55.5,20.9),(-53.9,20.5),(-52.4,21),(-50.8,20),
       (-63.3,22.5),(-62.6,23),(-61.3,23.6),(-59.9,23.4),(-58.6,23),(-57,23.4),(-55.8,23),(-54.2,23.6),(-52.7,23.7),(-51,23.1),
       (-62.1,25),(-60.6,25.5),(-59.3,25),(-57.9,25.7),(-56.5,25),(-55,25.5),(-53.5,25.1),(-51.9,25.8)]
for i,(x,y) in enumerate(sites):bamboo(i,x,y,[10.8,11.6,10.1,12.0,9.7,11.2][i%6], [.115,.089,.133,.104][i%4],821+i*17)
# Near-side culms occur beside the path, not across the camp or stair opening.
for i,(x,y) in enumerate([(-58.2,9.3),(-56.3,9.7),(-52.0,10.0)]):bamboo(70+i,x,y,[10.2,11.3,10.5][i],[.145,.11,.13][i],2311+i*29,True)
# Moss caps use an irregular footprint on upper rock surfaces, inset from edges.
for j,name in enumerate(state['rocks']):
    if any(k in name for k in ['Sea_','Stair_','Toe_']):continue
    ob=SCENE.objects[name];bb=[Vector(v) for v in ob.bound_box];cx=sum(p.x for p in bb)/8;cy=sum(p.y for p in bb)/8;w=(max(p.x for p in bb)-min(p.x for p in bb))*.38;d=(max(p.y for p in bb)-min(p.y for p in bb))*.32;t=tree(ob);b=Mesh('Cape_Strict_Moss_'+str(j));pts=[]
    for k in range(14):
        a=k*math.tau/14;x=cx+math.cos(a)*w*(.83+.13*math.sin(k*2.3));y=cy+math.sin(a)*d;z=sample(t,x,y)
        if z is not None:pts.append(Vector((x,y,z+.007)))
    if len(pts)>4:b.part(pts,tri(pts),'strict_moss');b.build(True)
grass=Mesh('Forest_Strict_Grass');shrubs=Mesh('Forest_Strict_Understory');flowers=Mesh('Forest_Strict_Flowers');grass_roots=[]
# Rooted patches delineate the clearing, step shoulders and lower bank. Empty
# route space remains visible; coverage is organized in broad connected groups.
patches=[(-65.5,16.0,1,.5),(-62.0,15.2,1.1,.5),(-60.7,15.1,1.5,.6),(-58.7,15.2,1.5,.6),(-56.5,15.2,1.5,.6),(-54.2,15.3,1.4,.6),
         (-60.5,10.7,1.4,.7),(-58.5,10.3,1.7,.8),(-56.2,11,1.7,.7),(-54,11.3,1.5,.7),(-58.0,7.5,1.5,.65),(-55.5,6.5,1.5,.8),
         (-64.7,19.5,1.2,.8),(-61.8,19,1.4,.8),(-59,19.5,1.7,.8),(-56.5,19,1.5,.8),(-54,19.7,1.4,.8)]
for pi,(cx,cy,rx,ry) in enumerate(patches):
    for k in range(80):
        a=rng.uniform(0,math.tau);rad=math.sqrt(rng.random());x=cx+math.cos(a)*rx*rad;y=cy+math.sin(a)*ry*rad;z=support(x,y)
        if z is None:continue
        dist,rh,ei,t=route_at(x,y)
        if dist<.95:continue
        root=Vector((x,y,z+.008));grass_roots.append(list(root));h=rng.uniform(.12,.34)
        for sign in [-1,1]:
            dl=Vector((rng.uniform(-.5,.5),rng.uniform(-.4,.4),1));blade(grass,root,dl,h,.018,'strict_grass',droop=.03)
        if k%7==0:
            for j in range(6):
                aa=j*math.tau/6+pi;dl=Vector((math.cos(aa)*.8,math.sin(aa)*.8,.55))
                blade(shrubs,root+Vector((0,0,.09)),dl,.40+rng.random()*.23,.06,'strict_leaf',droop=.04)
        if k%11==0:
            for j in range(3):
                p=root+Vector((rng.uniform(-.04,.04),rng.uniform(-.04,.04),h+.05));tube(flowers,[root,p],[.007,.004],'strict_branch',4)
                for a in range(5):
                    aa=a*math.tau/5;c=p+Vector((math.cos(aa)*.018,math.sin(aa)*.018,.0));flowers.part([c+Vector((-.014,0,0)),c+Vector((0,.016,.01)),c+Vector((.014,0,0)),c+Vector((0,-.016,.01))],[(0,1,2,3)],'strict_flower')
for b in [grass,shrubs,flowers]:
    o=b.build(True)
    for li,l in enumerate(o.data.loops):
        p=o.data.vertices[l.vertex_index].co;h=support(p.x,p.y)
        o.data.uv_layers[1].data[li].uv=(max(0,min(1,(p.z-(h if h is not None else p.z))/.6)),0)
state['bamboo_done']=True;state['grass_roots']=grass_roots;state['bamboo_design']='Jointed tapered culms, seven branch heights, lateral paired narrow leaves with folded volume, four staggered depth bands';state['understory']='Rooted grass patches, broad leaf rosettes, restrained flowers and moss caps'
save('bamboo-understory')
