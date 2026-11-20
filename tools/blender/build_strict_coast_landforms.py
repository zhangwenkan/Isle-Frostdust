"""Sculpt geological shapes, worn stone stairs and an integrated sand cove."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/strict_coast_common.py',encoding='utf8').read(),'strict_coast_common.py','exec'))
assert not state.get('landforms_done'),'Already authored; inspect rather than repeating.'
ft=ground_tree()
for o in list(SCENE.objects):
    if live(o) and o.name.startswith('Cape_Terminus_') and o.name!='Cape_Terminus_Bedrock':retire(o)
# The profiles are separately composed outlines, broad fracture directions and
# cap ridges for this reference's sea wall, stair shoulders and rooted bedding.
profiles=[ [(-1,-.4),(-.9,-.9),(-.3,-1),(.5,-.88),(.94,-.3),(.8,.55),(.32,.95),(-.6,.88)],
           [(-1,-.78),(-.35,-.94),(.66,-1),(1,-.32),(.83,.52),(.05,.96),(-.71,.77),(-.95,.1)],
           [(-.94,-.6),(-.57,-.96),(.12,-.86),(.86,-.72),(1,.08),(.48,.96),(-.15,.88),(-.91,.35)],
           [(-.8,-.95),(-.05,-1),(.82,-.65),(.91,.3),(.40,.89),(-.32,1),(-1,.4),(-.90,-.25)] ]
def rock(name,x,y,w,d,z,h,turn,style,lean=(0,0),tilt=(.1,-.1)):
    shape=profiles[style%4];b=Mesh(name);cs=math.cos(turn);sn=math.sin(turn);rings=[]
    # Broken ledges are unequal in height and width. There is no uniform cap bevel.
    factors=[.92,1.0,1.02,.91,.78];levels=[0,.22,.58,.87,1.0]
    for j,(f,v) in enumerate(zip(factors,levels)):
        row=[]
        for k,(px,py) in enumerate(shape):
            cut=[.0,.055,-.04,.015,-.065,.02,-.01,.04][(k+style)%8]*(1 if j in [1,2,3] else .2)
            dx=px*w*.5*(f+cut)+lean[0]*v;dy=py*d*.5*(f-cut*.6)+lean[1]*v
            zz=z+h*v+(tilt[0]*px+tilt[1]*py)*v
            if j in [1,2,3]:zz+=h*.045*math.sin(k*1.7+style*.8+j*.6)
            row.append(Vector((x+dx*cs-dy*sn,y+dx*sn+dy*cs,zz)))
        rings.append(row)
    for j in range(4):
        for k in range(8):
            n=(k+1)%8;a=rings[j][k];c=rings[j][n];e=rings[j+1][n];f=rings[j+1][k]
            # Break one broad face at a hand selected geological shoulder.
            if (k+style)%5==1 and j==2:
                mid=(a+c+e+f)*.25+Vector((.03*math.cos(turn),-.06,.045))
                b.part([a,c,e,f,mid],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],'strict_face')
            else:b.part([a,c,e,f],[(0,1,2,3)],'strict_face')
    ridge=(rings[-1][0]+rings[-1][4])*.5+Vector((-.15*w,.04*d,.13*h))
    b.part(rings[-1]+[ridge],[(k,(k+1)%8,8) for k in range(8)],'strict_cap')
    b.part(rings[0],[tuple(reversed(t)) for t in tri(rings[0])],'strict_face')
    o=b.build();soften(o,.028+min(w,d)*.006);state['rocks'].append(o.name);return o
specs=[('Sea_West',-67.0,12.0,2.9,3.25,-.35,6.5,.06,0,(.12,-.12),(.17,.12)),
       ('Sea_Front',-66.25,9.0,2.6,2.55,-.3,6.45,-.20,1,(.25,.1),(-.16,.15)),
       ('Stair_Left',-65.6,7.5,2.0,2.8,.3,5.95,-.14,2,(-.05,.1),(.08,.18)),
       ('Stair_Right',-60.85,8.1,2.6,2.75,.85,5.40,.25,3,(-.17,-.09),(-.13,.13)),
       ('Root_West',-64.4,16.6,3.25,2.7,5.70,2.35,-.14,1,(.18,.03),(.14,-.14)),
       ('Root_Mid',-61.7,17.1,2.45,2.0,5.75,1.75,.20,2,(-.16,-.05),(-.12,.10)),
       ('Root_East',-58.7,17.0,2.6,2.25,5.60,1.65,-.24,0,(.15,.0),(.15,-.09)),
       ('Root_Embedded',-60.0,15.6,1.8,1.3,6.0,.95,.3,3,(-.1,.08),(.04,.1)),
       ('Near_Upper',-58.5,8.0,3.35,2.55,3.65,2.42,-.24,2,(.12,.1),(-.09,.20)),
       ('Near_Lower',-56.0,4.5,3.3,2.5,1.55,2.8,.17,0,(-.13,.07),(.22,-.14)),
       ('Toe_West',-67.4,7.9,1.95,2.2,-.40,2.25,.14,3,(.04,.15),(.2,-.05)),
       ('Toe_West_Inset',-65.9,6.0,1.35,1.65,-.28,1.65,-.30,0,(.1,-.1),(.08,.15)),
       ('Toe_Right',-61.2,3.5,2.3,1.9,-.25,2.0,.40,1,(.12,.06),(.1,-.15)),
       ('Toe_Right_Low',-60.2,1.4,1.25,1.75,-.3,1.02,-.10,2,(-.1,.05),(-.15,.10)),
       ('Near_Seam',-54.3,4.0,2.2,2.4,1.2,2.4,.12,3,(.07,.07),(.14,-.05))]
for s in specs:rock('Cape_Strict_Rock_'+s[0],*s[1:])
rocktrees=[tree(SCENE.objects[n]) for n in state['rocks']]
# Preserve the connected solid base and its exact walking boundary. Its face
# is subdivided along geological fractures, no giant flat strip facade.
wall=SCENE.objects['Cape_Terminus_Bedrock'];keep(wall);bm=bmesh.new();bm.from_mesh(wall.data)
bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=2,use_grid_fill=True)
for v in bm.verts:
    p=v.co
    if p.z>5.9:continue
    p.x+=.045*math.sin(p.z*2.4+p.y*.7);p.y+=.075*math.sin(p.x*1.1+p.z*1.3)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(wall.data);bm.free();wall.data.materials.clear();wall.data.materials.append(MATS['strict_face']);wall.data.update()
for p in wall.data.polygons:
    p.material_index=0
    for li in p.loop_indices:
        co=wall.data.vertices[wall.data.loops[li].vertex_index].co
        wall.data.uv_layers[0].data[li].uv=(co.x*.28+co.y*.22,co.z*.23)
# Worn paving follows the actual route. Each stone has thickness and a varied
# perimeter; gaps expose the same registered soil surface.
rng=random.Random(204);paving=Mesh('Cape_Strict_Paving')
for i in range(19):
    x=-63.2+i*.51;y=13.35+.35*math.sin(i*.36)
    for j in [-1,0,1]:
        cx=x+rng.uniform(-.14,.14);cy=y+j*.51+rng.uniform(-.12,.12);z=height_at(ft,cx,cy)
        w=rng.uniform(.37,.63);d=rng.uniform(.32,.53);a=rng.uniform(-.35,.35);cs=math.cos(a);sn=math.sin(a);shape=profiles[(i+j)%4]
        tops=[Vector((cx+px*w*.5*cs-py*d*.5*sn,cy+px*w*.5*sn+py*d*.5*cs,z+.032+.008*px)) for px,py in shape]
        bottoms=[p-Vector((0,0,.055)) for p in tops]
        paving.part(tops,tri(tops),'strict_cap')
        for k in range(8):n=(k+1)%8;paving.part([bottoms[k],bottoms[n],tops[n],tops[k]],[(0,1,2,3)],'strict_face')
paving.build()
# One shorter stair in the same notch. Alternate real stone joints and slightly
# chipped nosings; an invisible imported solid provides complete support.
top=Vector((-63.3,8.8,6.22));bottom=Vector((-62.5,1.6,.15));axis=bottom-top;axis.z=0;length=axis.length;axis.normalize();side=Vector((-axis.y,axis.x,0));steps=22;width=2.38
stair=Mesh('Strict_Stair_Treads');support=Mesh('Strict_Stair_Solid')
for i in range(steps):
    z=top.z-(top.z-bottom.z)*i/steps;c=top+axis*(length*i/steps);depth=length/steps+.026
    joints=[-.5,-.17,.22,.5] if i%2==0 else [-.5,.04,.5]
    for k,(l,r) in enumerate(zip(joints,joints[1:])):
        l=l*width+.008;r=r*width-.008
        # A long broad top, recessed edge and broken end corners.
        poly=[c+side*l-axis*.03,c+side*r-axis*.02,c+side*(r-.025)+axis*(depth-.012),c+side*(l+.018)+axis*(depth+.003)]
        for p in poly:p.z=z
        lo=[p-Vector((0,0,.255)) for p in poly]
        stair.part(poly,[(0,1,2,3)],'strict_cap')
        for a in range(4):b=(a+1)%4;stair.part([lo[a],lo[b],poly[b],poly[a]],[(0,1,2,3)],'strict_face')
    # Support under full tread, including joints, down to seabed.
    poly=[c+side*(-width*.5)-axis*.045,c+side*(width*.5)-axis*.045,c+side*(width*.5)+axis*(depth+.02),c+side*(-width*.5)+axis*(depth+.02)]
    for p in poly:p.z=z-.045
    lo=[Vector((p.x,p.y,-.55)) for p in poly];support.part(poly,[(0,1,2,3)],'strict_face')
    for a in range(4):b=(a+1)%4;support.part([lo[a],lo[b],poly[b],poly[a]],[(0,1,2,3)],'strict_face')
o=replace('WALK_Cape_Stairs',stair.build());soften(o,.013)
replace('Cape_Stair_Support',support.build())
LAYOUT['anchors']['cape_stair_bottom']=[bottom.x,bottom.z,-bottom.y];rc['stairs'].update(bottom=LAYOUT['anchors']['cape_stair_bottom'],steps=steps,width=width)
# Rebuild the cove cross sections: a concave shoreline, a shallow submerged
# apron and dry sand continuing under the rock feet. UV2 stores swash distance.
shore=[]
for i in range(32):
    t=i/31;x=-68.5+14*t;y=-1.7-6.1*math.sin(math.pi*t)**.85+.40*math.sin(t*math.tau*2)
    shore.append([x,-y])
rc['shoreline']=shore
for name,film in [('WALK_Cape_Sand',False),('Cape_Swash_Film',True)]:
    b=Mesh(name+'_Cove');vs=[];uv=[];ws=[];fs=[];widthn=22
    for i,(x,gz) in enumerate(shore):
        sy=-gz;t=i/31;back=9.5-4*sm(.4,1,t)
        for j in range(widthn+1):
            v=j/widthn;y=sy-3.0+(back-sy+3)*v;dist=sy-y
            z=.13-.78*(1-sm(sy-3,sy-.2,y))
            if y>sy+.9:z+=.008*math.sin(x*1.7+y*.8)
            if film:z=max(-.17,z+.008)
            vs.append((x,y,z));uv.append((t,v));ws.append(0)
    for i in range(31):
        for j in range(widthn):a=i*(widthn+1)+j;fs.append((a,a+1,a+widthn+2,a+widthn+1))
    b.part(vs,fs,'strict_soil',uv,ws);o=replace(name,b.build(True))
    for li,l in enumerate(o.data.loops):
        p=o.data.vertices[l.vertex_index].co;idx=max(0,min(31,round((p.x+68.5)/14*31)));sy=-shore[idx][1]
        o.data.uv_layers[1].data[li].uv=(p.x,sy-p.y)
state['landforms_done']=True;state['stairs']={'steps':steps,'width':width,'run':length,'previous_steps':30,'previous_run':11.353};state['sand']='Curved cove with dry beach, submerged apron, signed swash UV2 and cliff foot overlap'
rc['cliff_masses']=state['rocks']
save('landforms')
