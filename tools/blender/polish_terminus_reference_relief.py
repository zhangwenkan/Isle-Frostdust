"""Correct discs, striped cliff relief and regular paving through Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
import ast
rc=LAYOUT['reference_cape'];data=rc['rocky_terminus'];rw=data['reference_rework'];assert not rw.get('polish')
COL=bpy.data.collections[rw['collection']]
MATS['relief_top']=bpy.data.materials['ForestCoast_relief_top'];MATS['relief_side']=bpy.data.materials['ForestCoast_relief_side']
ground=SCENE.objects['WALK_Forest_Ground']
def tree(o):return BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
ft=tree(ground)
def fh(x,y):
    p=ft.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0]
    return p.z if p else ft.find_nearest(Vector((x,y,6)))[0].z
def replace(o,new):o.data=new.data;bpy.data.objects.remove(new,do_unlink=True)
# Shapes are asymmetric block footprints, with long faces and clipped corners.
shapes=[ [(-1,-.78),(-.57,-1),(.86,-.82),(1,.55),(.48,.95),(-.87,.86)],
         [(-.90,-1),(.58,-.9),(1,-.45),(.72,.97),(-.54,.84),(-1,.18)],
         [(-1,-.66),(.24,-1),(.97,-.57),(.86,.72),(-.50,1),(-1,.31)] ]
def angular(name,x,y,w,d,base,h,angle,lean,tilt,variant=0):
    b=Mesh(name);cs=math.cos(angle);sn=math.sin(angle);rings=[];shape=shapes[variant%3];N=len(shape)
    for j,(f,z) in enumerate([(1.01,base),(.98,base+h-.13),(.925,base+h)]):
        row=[]
        for px,py in shape:
            dx=px*w*.5*f+lean[0]*j*.5;dy=py*d*.5*f+lean[1]*j*.5
            row.append(Vector((x+dx*cs-dy*sn,y+dx*sn+dy*cs,z+(tilt[0]*px+tilt[1]*py if j else 0))))
        rings.append(row)
    tile=variant%4;u=tile%2*.5;v=tile//2*.5
    for j in range(2):
        for i in range(N):
            q=(i+1)%N
            b.part([rings[j][i],rings[j][q],rings[j+1][q],rings[j+1][i]],[(0,1,2,3)],'relief_side' if j==0 else 'relief_top',[(u+.03,v+.04),(u+.47,v+.04),(u+.47,v+.47),(u+.03,v+.47)])
    # Two broad inclined roof planes, no cone or central ring.
    left=(rings[2][0]+rings[2][5])*.5+Vector((w*.29,d*.015,.055))
    right=(rings[2][2]+rings[2][3])*.5+Vector((-w*.30,-d*.025,.015))
    top=rings[2]+[left,right]
    uv=[(u+.08+(p.x-x+w*.5)/w*.32,v+.08+(p.y-y+d*.5)/d*.32) for p in top]
    b.part(top,[(0,1,2,7,6),(2,3,4,7),(4,5,0,6,7)],'relief_top',uv)
    b.part(rings[0],[tuple(reversed(t)) for t in tri(rings[0])],'relief_side');return b.build()
for i,row in enumerate(rw['rocks']):
    name=row['name'];ob=SCENE.objects[name];x=row['x'];y=row['y'];w=row['w'];d=row['d'];base=row['base'];h=row['height']
    if name.endswith('Root_West'):h+=.65;w*=.93
    elif name.endswith('Root_Middle'):h+=.42
    elif name.endswith('Root_East'):h+=.30
    elif name.endswith('Stair_West'):x-=.4;h+=.3;w*=.90
    elif name.endswith('Stair_East'):x+=.48;h+=.27;w*=.91
    elif name.endswith('Coast_West'):x+=.10;h+=.42
    elif name.endswith('Near_Shoulder'):h+=.35
    row.update(x=x,y=y,w=w,d=d,height=h)
    replace(ob,angular(name+'_Angular',x,y,w,d,base,h,[.12,-.22,.30][i%3],(.07*(-1)**i,.10),(.18*(-1)**i,-.18 if i<3 else .14),i))

# Continuously connected facades, with variable fracture levels. Brush UV is
# continuous along the cliff and never reset for each horizontal strip.
border=[Vector(p) for p in data['outline']];stations=[];skip=[];along=0
for seg,(p,q) in enumerate(zip(border,border[1:])):
    if p.y>8.7 and q.y>8.7 and p.x<-64 and q.x>-63:skip.append(seg)
    n=Vector((q.y-p.y,p.x-q.x,0)).normalized()
    for t in [0,.31,.74]:
        v=p.lerp(q,t);v.z=fh(v.x,v.y);stations.append((v,n,seg,along+(q-p).length*t))
    along+=(q-p).length
stations.append((Vector((border[-1].x,border[-1].y,fh(border[-1].x,border[-1].y))),stations[-1][1],len(border)-2,along))
rings=[[],[],[],[]]
for i,(p,n,seg,s) in enumerate(stations):
    rings[0].append(p)
    rings[1].append(p+n*.16-Vector((0,0,.22+.035*math.sin(i))))
    rings[2].append(Vector((p.x+n.x*(.24+.27*math.sin(i*1.1)),p.y+n.y*(.24+.27*math.sin(i*1.1)),2.7+.51*math.sin(i*.78))))
    rings[3].append(Vector((p.x+n.x*.27,p.y+n.y*.27,-.65)))
b=Mesh('Cape_Terminus_Continuous_Fractures')
for j in range(3):
    for i in range(len(stations)-1):
        if stations[i][2] in skip:continue
        vs=[rings[j][i],rings[j][i+1],rings[j+1][i+1],rings[j+1][i]]
        s0=stations[i][3];s1=stations[i+1][3]
        b.part(vs,[(0,1,2,3)],'relief_top' if j==0 else 'relief_side',[(s0/8,vs[0].z/7),(s1/8,vs[1].z/7),(s1/8,vs[2].z/7),(s0/8,vs[3].z/7)])
replace(SCENE.objects['Cape_Terminus_Bedrock'],b.build())
# Two attached basal wedges give the upper cliff a physical foot, keeping stairs open.
for i,(name,x,y,w,d,h,angle) in enumerate([('Cape_Terminus_Toe_West',-66.4,8.1,2.6,2.3,2.55,.35),('Cape_Terminus_Toe_East',-60.0,4.35,3.0,2.3,2.15,-.30)]):
    angular(name,x,y,w,d,-.45,h,angle,(.15,.10),(.15,-.17),i+1);rc['cliff_masses'].append(name)

# Replace the neat rows with unequal small groups and soil intervals.
paving=Mesh('Cape_Terminus_Path_Irregular')
path=[(-60.5,13.4,.7,.52),(-59.9,13.85,.55,.51),(-59.4,13.3,.72,.44),(-58.95,14.05,.61,.60),(-58.5,13.58,.62,.49),(-57.95,13.2,.74,.46),(-57.6,14.05,.60,.54),(-57.1,13.54,.77,.56),(-56.75,14.0,.53,.4),(-56.15,13.38,.75,.58),(-55.55,13.9,.65,.51),(-54.9,13.4,.81,.62)]
for i,(x,y,w,d) in enumerate(path):
    shape=shapes[i%3];pts=[(x+px*w*.5,y+py*d*.5) for px,py in shape];z=fh(x,y)+.018
    paving.part([(a,bb,z) for a,bb in pts],tri([Vector((a,bb,z)) for a,bb in pts]),'relief_top',[(.5+(a-x)/w*.34,.5+(bb-y)/d*.34) for a,bb in pts])
replace(SCENE.objects['Cape_Terminus_Path_Pieces'],paving.build())

# Refit plant roots without changing original UV2 weights or gust seeds.
rt=[tree(SCENE.objects[n]) for n in rc['cliff_masses']]
def support(x,y):
    ps=[t.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0] for t in [ft]+rt]
    return max([p.z for p in ps if p],default=fh(x,y))
roles=LAYOUT['forest_extension']['layer_roles'];bindings=roles['wind_bindings']
for name in rw['root_bamboo']:
    bind=bindings[name];dz=support(bind['root'][0],-bind['root'][2])+.012-bind['root'][1]
    for v in SCENE.objects[name].data.vertices:v.co.z+=dz
    SCENE.objects[name].data.update();bind['root'][1]+=dz
grass=SCENE.objects['Forest_Grass_Terminus'];N=5
for start in range(0,len(grass.data.vertices),N):
    root=(grass.data.vertices[start].co+grass.data.vertices[start+1].co)*.5
    dz=support(root.x,root.y)+.012-root.z
    for k in range(N):grass.data.vertices[start+k].co.z+=dz
grass.data.update()
# Ferns retain their frond proportions as one rooted group, never per-vertex terrain snapping.
ferns=SCENE.objects['Forest_Grass_Terminus_Ferns'];group=5*4*2*4
for start in range(0,len(ferns.data.vertices),group):
    verts=list(ferns.data.vertices)[start:start+group];x=sum(v.co.x for v in verts)/len(verts);y=sum(v.co.y for v in verts)/len(verts)
    base=min(v.co.z for v in verts)-.10;dz=support(x,y)+.015-base
    # Previous root is recovered from its known group center; shift relative support only.
    oldh=ft.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0]
    if oldh and dz<1.5:
        for v in verts:v.co.z+=max(-.35,min(.7,dz))
ferns.data.update()
for m in MATS.values():
    if m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type=='TEX_IMAGE' and n.image:n.image.reload();n.image.pack()
rw['polish']={'angular_footprints':True,'continuous_brush_uv':True,'irregular_path_pieces':len(path),'attached_toes':2,'art_status':'inspect required'}
export('reference-forest-coast-relief-pass2')
