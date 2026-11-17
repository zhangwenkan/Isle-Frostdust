"""Close the deep forest and near-bank composition using actual Blender assets."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
import ast,random
REVIEW=ROOT/'artifacts/bamboo-west-extension-review';COL=bpy.data.collections['43_West_Forest']
assert not SCENE.objects.get('Forest_Back_Ground')
# A falling forest floor beyond the previous visible edge. It remains behind
# the existing woodland, with its dark trunks screening the pale coastal sky.
vs=[];fs=[]
for i in range(43):
    x=-57+i*1.35
    for j in range(17):
        y=29+j*1.65;z=1.32-.28*(y-30)+.12*math.sin(x*.18+y*.31)
        vs.append((x,y,z))
for i in range(42):
    for j in range(16):
        a=i*17+j;fs.extend([(a,a+17,a+18),(a,a+18,a+1)])
b=Mesh('Forest_Back_Ground');b.part(vs,fs,bpy.data.materials['Forest_Floor'],[((p[0]+50)/54,(p[1]+4)/40) for p in vs]);b.build(smooth=True)
for row,dy in enumerate([10.5,19.0]):
    for j,index in enumerate([33,34,35,36,37]):
        for canopy in [False,True]:
            source=SCENE.objects[('Forest_Bamboo_Canopy_' if canopy else 'Forest_Bamboo_')+'%02d'%index]
            ob=source.copy();ob.data=source.data.copy();ob.name='Forest_Bamboo_DeepRow_%d_%d_%d'%(row,j,int(canopy));COL.objects.link(ob)
            dx=(-1.8 if row==0 else 1.1)
            for v in ob.data.vertices:
                v.co.x+=dx;v.co.y+=dy;v.co.z-=dy*.28
            ob.data.update();ob.hide_set(False);ob.hide_render=False
            LAYOUT['forest_extension']['groves'].append({'name':ob.name,'band':'backdrop'})
# Terminal grove beyond the playable endpoint: the path resolves into trees,
# while the player has a clear standing area before it.
for canopy in [False,True]:
    source=SCENE.objects['Forest_Bamboo_Canopy_26' if canopy else 'Forest_Bamboo_26']
    ob=source.copy();ob.data=source.data.copy();ob.name='Forest_Bamboo_Terminal_'+str(int(canopy));COL.objects.link(ob)
    for v in ob.data.vertices:v.co.x-=.8;v.co.y-=2.0;v.co.z+=.1
    ob.data.update();LAYOUT['forest_extension']['groves'].append({'name':ob.name,'band':'rear'})

# Broken grass patches tie the foreground into one bank. Their sizes and
# density taper across each patch rather than forming identical potted clumps.
tree=ast.parse((ROOT/'tools/blender/build_left_vegetation.py').read_text(encoding='utf-8'))
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name=='leaf':exec(compile(ast.Module(body=[node],type_ignores=[]),'leaf','exec'))
ob=SCENE.objects['WALK_Forest_NearSlope'];bvh=BVHTree.FromPolygons([v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons]);rng=random.Random(208)
grass=Mesh('Forest_Grass_NearPatches')
for ci,(cx,cy,sx,sy) in enumerate([(-21,6.8,2.1,1),(-26.4,6,3.0,1.4),(-32,5.5,2.8,1.5),(-37.5,6.3,2.6,1.2),(-43.2,6,3.1,1.3),(-46.8,8.8,1.2,1.7)]):
    for j in range(105):
        a=rng.random()*math.tau;r=math.sqrt(rng.random());x=cx+math.cos(a)*r*sx;y=cy+math.sin(a)*r*sy
        if r>.8 and j%3:continue
        hit=bvh.ray_cast(Vector((x,y,25)),Vector((0,0,-1)))[0]
        if hit is None:continue
        for k in range(5):
            ph=k*2.4+j*.73;h=[.24,.33,.42,.29,.37][(j+k)%5]*(1-.2*r)
            leaf(grass,Vector((x,y,hit.z-.015)),Vector((math.cos(ph)*.2,math.sin(ph)*.2,1)),h,.048,ph*.1,.8,[.91,1.06,.98][k%3],'grass_blade')
ob=grass.build()
for li in range(len(ob.data.loops)):ob.data.uv_layers[1].data[li].uv=(ob.data.uv_layers[0].data[li].uv.y,0)
export('west-forest-backdrop')
