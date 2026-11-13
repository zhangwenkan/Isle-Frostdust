# Second art pass after inspecting the Godot midshot.
for ob in list(COL['09_Distant_Isles'].objects):
    if 'Lichen' in ob.name:bpy.data.objects.remove(ob,do_unlink=True)
for col in ['02_Cliff_Strata','03_Weathered_Rocks','08_Sea_Reefs','10_Foreground']:
    for ob in list(COL[col].objects):
        if 'Lichen' in ob.name:
            base_name=ob.name.removesuffix('_Crown_Lichen')
            parent=bpy.data.objects.get(base_name)
            if parent:ob.location=parent.location.copy()

# Bring shallow earth lips back to a narrow strip, break broad cliff bands into facets.
for ob in COL['02_Cliff_Strata'].objects:
    if 'Stratified' not in ob.name:continue
    for p in ob.data.polygons:
        if p.material_index==3:p.material_index=0
    # Irregular vertical buttresses make the large silhouette visibly eroded.
for i in range(26):
    x=-17.9+i*.82;z=2.6+math.sin((x+13)*.17)*.7
    if not inside(x,z-.35,OUTLINE):continue
    top=height(x,z);h=(top-WATER)*.42
    sculpt_rock('Eroded_Vertical_Buttress_%02d'%i,(x,(top+WATER)*.5,z-.05),(.52,h,.44),'02_Cliff_Strata',seed=820+i)

# Densify crown volume with independent tufts around the branch tips.
for i,(x,z,h,lean) in enumerate([(-15.5,-2,4.9,-.75),(-10.5,-3.3,6,.65),(-7.4,-3.8,4,-.45),(-1.8,-1.9,4.8,.75),(18.5,-1.7,5.8,-.65),(22.3,-1,4.6,.6)]):
    rr=random.Random(721+i);base=Vector((x,height(x,z),z));b=Batch()
    for j in range(13):
        f=.43+j*.039;a=j*2.399+i*.4
        origin=base+Vector((lean*f*f+.17*math.sin(f*5),h*f,.13*math.sin(f*4)))
        length=(1-f)*h*.75+.28
        center=origin+Vector((math.cos(a)*length,.2,math.sin(a)*length*.70))
        for cluster in range(9):
            c=center+Vector((rr.uniform(-.48,.48),rr.uniform(-.16,.18),rr.uniform(-.36,.36)))
            radius=rr.uniform(.22,.36)
            # Layered lobes are tightly packed pointed needles, never billboard cards.
            vs=[]
            for level in [0,1,2]:
                for k in range(9):
                    ang=k*math.tau/9+.1*level;r=radius*[.5,1,.3][level]
                    vs.append(c+Vector((math.cos(ang)*r,[-.10,.01,.15][level],math.sin(ang)*r*.8)))
            fs=[]
            for level in range(2):
                for k in range(9):fs.append((level*9+k,level*9+(k+1)%9,(level+1)*9+(k+1)%9,(level+1)*9+k))
            fs.append(tuple(18+k for k in range(9)))
            b.add(vs,fs,rr.choices([0,1,2],[25,55,20])[0])
    b.finish(f'Pine_{i:02d}_Dense_Needle_Clusters',['pine','pine_light','pine_tip'],'04_Pine_Trees')

# Add cliff-top turf tufts and gravel that visually dissolve the trail edge.
tufts=Batch()
for j in range(380):
    x=R.uniform(-18.2,4.2);z=path_z(x)+(1 if j%2 else -1)*R.uniform(.58,.85)
    y=height(x,z)+.045
    for k in range(4):
        a=R.random()*math.tau;h=R.uniform(.07,.19)
        leaf(tufts,(x,y,z),(x+math.cos(a)*.08,y+h,z+math.sin(a)*.08),.015,.01,j%3)
tufts.finish('Trail_Edge_Grass_Transition',['grass_dark','grass_mid','grass_tip'],'06_Ferns_Grass')

# Keep the authoring file and interchange asset in sync.
save()
print('Second pass: compact needle crowns, irregular cliff buttresses, turf edges and corrected lichen placement.')
