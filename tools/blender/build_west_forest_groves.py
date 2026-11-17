"""Structured culms and canopy, joined forest path details. Blender MCP only."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
import ast,random
from mathutils.bvhtree import BVHTree
REVIEW=ROOT/'artifacts/bamboo-west-extension-review';COL=bpy.data.collections['43_West_Forest']
assert not SCENE.objects.get('Forest_Bamboo_00')
for source,names in [('build_left_vegetation.py',['leaf']),('build_left_stonework.py',['slab'])]:
    tree=ast.parse((ROOT/'tools/blender'/source).read_text(encoding='utf-8'))
    for node in tree.body:
        if isinstance(node,ast.FunctionDef) and node.name in names:exec(compile(ast.Module(body=[node],type_ignores=[]),source,'exec'))
archive=bpy.data.collections.new('90_Before_Forest_Composition');SCENE.collection.children.link(archive)
retired=[]
for ob in list(SCENE.objects):
    if ob.name.startswith('Left_Bamboo') and not any(c.name.startswith('90_') for c in ob.users_collection):
        retired.append(ob.name)
        for c in list(ob.users_collection):c.objects.unlink(ob)
        archive.objects.link(ob);ob.hide_set(True);ob.hide_render=True
trees=[]
for name in ['WALK_Left_Ground','WALK_Forest_Ground']:
    ob=SCENE.objects[name];trees.append(BVHTree.FromPolygons([v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons]))
def floor(x,y):
    hits=[tree.ray_cast(Vector((x,y,35)),Vector((0,0,-1)))[0] for tree in trees]
    hits=[p.z for p in hits if p is not None]
    return max(hits) if hits else None
def road_distance(x,y):
    best=100.
    for ka,kb in LAYOUT['edges'][2:]:
        a=A[ka];b=A[kb];v=b.xy-a.xy;t=max(0,min(1,(Vector((x,y))-a.xy).dot(v)/v.length_squared))
        best=min(best,(Vector((x,y))-a.xy-v*t).length)
    return best
# Root groups are authored in depth bands with deliberate gaps across the light
# clearing. Low branches start above head height; readable culms remain below.
groves=[
(-15.5,.3,5,7.1,1.25,'old'),(-12.9,2.2,4,7.7,1.15,'old'),(-9.7,1.3,3,6.9,.85,'old'),
(-1.5,2.0,3,6.4,.65,'old'),(-12.6,5.3,4,7.9,1.15,'old'),(-5.0,5.5,3,6.8,.7,'old'),
(-15.7,8.7,4,7.8,1.3,'old'),(-8,9.0,3,7.1,.6,'old'),(-10.6,14.3,4,7.9,.9,'old'),
(-16.0,15.1,4,7.7,1.15,'old'),(-17.5,4.5,3,7.1,.75,'old'),(-10.5,5.3,3,7.5,.8,'old'),
(-3.1,7.6,3,7.4,.8,'rear'),(-5.6,11.8,4,8.1,1.1,'rear'),(-8,17.5,4,8.2,1.1,'rear'),
(-1.4,12.2,4,8.3,1.3,'deep'),(-5.2,19.8,5,8.3,1.3,'deep'),(-12.8,22.8,5,8.4,1.5,'deep'),
(-20.4,9.0,3,7.5,.7,'front'),(-32.0,9.4,2,7.9,.45,'front'),(-43.4,10.0,3,8.2,.65,'front'),
(-19.0,16.0,4,8.0,1.1,'rear'),(-23.4,16.8,4,8.4,1.3,'rear'),(-30.4,17.0,3,8.1,1.0,'rear'),
(-35.5,16.5,4,8.4,1.2,'rear'),(-40.2,17.8,4,8.3,1.3,'rear'),(-46.1,17,4,8.5,1.2,'rear'),
(-17.5,23,4,8.0,1.4,'deep'),(-22.6,24.5,5,8.6,1.5,'deep'),(-28.1,24,4,8.4,1.6,'deep'),
(-33.7,24.2,5,8.1,1.5,'deep'),(-39.0,25,4,8.5,1.4,'deep'),(-45,24,5,8.4,1.4,'deep'),
(-12,28.5,4,7.7,1.2,'far'),(-19,30,4,8.0,1.4,'far'),(-26,30.5,5,8.2,1.5,'far'),
(-33,30.5,4,8.0,1.5,'far'),(-41,30,4,8.1,1.5,'far')]
records=[];rng=random.Random(161126)
for gi,(cx,cy,count,H,radius,band) in enumerate(groves):
    b=Mesh('Forest_Bamboo_%02d'%gi)
    for si in range(count):
        phase=si*2.4+gi*.78;rad=radius*(.25+.73*(si+1)/count);x=cx+math.cos(phase)*rad;y=cy+math.sin(phase)*rad
        z=floor(x,y)
        if z is None or road_distance(x,y)<1.38:continue
        h=H*[.91,1.04,.95,1.0,.87][(si+gi)%5];R=[.092,.11,.08,.10,.086][(gi+si)%5]
        base=Vector((x,y,z-.025));bend=Vector((math.cos(phase+.5),math.sin(phase+.5),0))*(.22+.11*(si%3))
        def center(z):return base+Vector((0,0,z))+bend*(z/h)**1.8
        intervals=round(h/.64)
        zs=[j*h/intervals for j in range(intervals+1)];radii=[R*(1-.57*j/intervals) for j in range(intervals+1)]
        tube(b,[center(v) for v in zs],radii,'culm',9,[(v/h)**1.9 for v in zs])
        for j in range(1,intervals):
            v=j*h/intervals;rr=R*(1-.57*j/intervals)
            tube(b,[center(v-.028),center(v-.008),center(v+.025)],[rr*1.03,rr*1.14,rr*1.03],'node',9,[(v/h)**1.9]*3)
        # Three to four sprays per stem. The front row keeps its lower 4.5 m
        # open, so the canopy frames the scene without a wall at actor height.
        low=.64 if band=='front' else (.53 if band=='old' else .49)
        for k in range(4):
            q=low+(1-low)*k/4;v=h*q;ang=phase+k*2.24
            axis=Vector((math.cos(ang),math.sin(ang),.14));length=[1.45,1.7,1.4,1.22][k]
            start=center(v);elbow=start+axis*length*.52+Vector((0,0,.18));end=start+axis*length
            wt=q**1.9;tube(b,[start,elbow,end],[R*.31,R*.16,.008],'branch',5,[wt,wt,wt])
            for twig in [-1,0,1]:
                begin=elbow.lerp(end,.28 if twig else .70);a=ang+twig*.7;direction=Vector((math.cos(a),math.sin(a),-.18));tip=begin+direction*(.78 if twig else .97)
                tube(b,[begin,tip],[.009,.003],'branch',5,[wt,wt])
                for li in range(7):
                    t=.08+li*.135;side=1 if li%2 else -1;alpha=a+side*(.72+.06*(li%3))
                    direct=Vector((math.cos(alpha),math.sin(alpha),[-.33,-.12,.03,-.26][(li+k)%4]))
                    length=[.48,.59,.52,.63,.43][(si+li+k)%5]
                    leaf(b,begin.lerp(tip,t),direct,length,length*.205,(li%3-1)*.44,wt,[.93,1.05,.98,.88,1.02][(si+li)%5])
        for k in range(7):
            a=phase+k*math.tau/7;leaf(b,center(h-.20),Vector((math.cos(a),math.sin(a),.10-k*.04)),.52,.106,k*.19,1.0,.98)
        records.append({'object':b.name,'band':band,'root':[x,y,z],'height':h})
    ob=b.build()
    ob['depth_band']=band
    for p in ob.data.polygons:
        if ob.data.materials[p.material_index].name in ['LF_culm','LF_node','LF_branch']:p.use_smooth=True

# Surface map shared by old and new ground. This changes UV/material only on
# the original floor; all original stair/slab geometry remains editable.
m=bpy.data.materials.new('Forest_Floor');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.97
im=bpy.data.images.load(str(OUT/'forest_extension/forest_floor.png'),check_existing=True);im.reload();im.pack();node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;m.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
for name in ['WALK_Left_Ground','WALK_Forest_Ground']:
    ob=SCENE.objects[name];index=4 if name=='WALK_Left_Ground' else 0;ob.data.materials[index]=m
    for poly in ob.data.polygons:
        if poly.material_index!=index:continue
        for li in poly.loop_indices:
            co=ob.data.vertices[ob.data.loops[li].vertex_index].co;ob.data.uv_layers[0].data[li].uv=((co.x+50)/54,(co.y+4)/40)

# Occasional embedded stepping stones, worn soil is the main walking surface.
stones=Mesh('WALK_Forest_Paving');stone_records=[]
for i,(ka,kb) in enumerate(LAYOUT['forest_extension']['new_edges']):
    a=A[ka];b=A[kb];direction=(b-a).normalized();forward=Vector((direction.x,direction.y,0)).normalized();right=Vector((forward.y,-forward.x,0))
    for j,t in enumerate([.16,.43,.78]):
        c=a.lerp(b,t)+right*([-.42,.18,-.28][j]);z=floor(c.x,c.y)
        if z is None:continue
        c.z=z+.020
        slab(stones,c,right,forward,[.62,.90,.56][j],[.47,.58,.65][(j+i)%3],.075,'paving',i+j)
        stone_records.append(list(c))
stones.build()

# Low rock shoulders are embedded in the banks, outside the activity strip.
rock_specs=[(-19.4,15.2,1.4,.85,.65),(-24.3,17.8,1.85,1.05,.90),(-29.7,10.0,1.25,.72,.42),(-36.1,15.2,1.6,.95,.64),(-42.6,16.6,1.95,1.1,.85),(-7.2,13.8,1.45,1.05,.58)]
for ri,(cx,cy,sx,sy,h) in enumerate(rock_specs):
    z=floor(cx,cy)
    if z is None:continue
    b=Mesh('Forest_Rock_%02d'%ri);plan=[(-1,-.3),(-.6,-.82),(.45,-.7),(1,.08),(.60,.85),(-.64,.64)]
    rings=[]
    for k in range(3):
        rings.extend([(cx+x*sx*[.85,1,.77][k]+k*.08,cy+y*sy*[.86,1,.79][k],z+[-.28,h*.59,h][k]+(.11*x-.08*y if k==2 else 0)) for x,y in plan])
    for k in range(2):
        for j in range(6):
            ids=[k*6+j,k*6+(j+1)%6,(k+1)*6+(j+1)%6,(k+1)*6+j];b.part([rings[v] for v in ids],[(0,1,2,3)],['rock_a','rock_b','rock_c'][(j+ri)%3])
    b.part(rings[12:],tri(rings[12:]),'rock_top');b.part(rings[:6],[tuple(reversed(t)) for t in tri(rings[:6])],'rock_c');b.build()

# Grass is distributed in banks, interrupted at stones and root collars.
grass=Mesh('Forest_Grass_Banks');tufts=[]
for ka,kb in LAYOUT['forest_extension']['new_edges']:
    a=A[ka];b=A[kb];v=b-a;side=Vector((-v.y,v.x,0)).normalized()
    for j in range(max(2,int(v.length/.30))):
        for sign in [-1,1]:
            p=a.lerp(b,(j+.5)/max(2,int(v.length/.30)))+side*sign*(1.30+.15*math.sin(j*1.9))
            if j%5==0:continue
            tufts.append((p.x,p.y))
for ri,r in enumerate(records):
    x,y,z=r['root']
    if r['band'] in ['rear','front']:
        for j in range(3):tufts.append((x+math.cos(j*2.4)*.32,y+math.sin(j*2.4)*.32))
for i,(x,y) in enumerate(tufts):
    z=floor(x,y)
    if z is None:continue
    for k in range(7):
        a=k*2.4+i*.47;d=Vector((math.cos(a)*.28,math.sin(a)*.28,1));ln=[.25,.34,.27,.41,.29,.37,.22][(i+k)%7]
        leaf(grass,Vector((x,y,z-.016)),d,ln,.046,a*.13,.75,[.92,1.08,1.0,.86][(i+k)%4],'grass_blade')
ob=grass.build()
for li in range(len(ob.data.loops)):ob.data.uv_layers[1].data[li].uv=(ob.data.uv_layers[0].data[li].uv.y,0)
LAYOUT['forest_extension']['groves']=[{'name':'Forest_Bamboo_%02d'%i,'band':r[-1]} for i,r in enumerate(groves)]
(REVIEW/'forest-authoring.json').write_text(json.dumps({'roots':records,'embedded_stones':stone_records,'retired_groves':retired,'new_ground_vertices':len(SCENE.objects['WALK_Forest_Ground'].data.vertices)},indent=2),encoding='utf-8')
export('west-forest-groves')
