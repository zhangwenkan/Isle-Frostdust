"""Enclose the west path in a wooded valley. Execute only via Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
REVIEW=ROOT/'artifacts/forest-valley-enclosure-review'
assert not bpy.data.collections.get('44_Valley_Forest_Backdrop'), 'Inspect existing pass instead of rebuilding.'
COL=bpy.data.collections.new('44_Valley_Forest_Backdrop');SCENE.collection.children.link(COL)
ARCH=bpy.data.collections.new('90_Before_Valley_Forest_Backdrop');SCENE.collection.children.link(ARCH)
old_floor=SCENE.objects['Forest_Back_Ground']
source_trees={i:(SCENE.objects['Forest_Bamboo_%02d'%i],SCENE.objects['Forest_Bamboo_Canopy_%02d'%i]) for i in range(33,38)}
old_trees=[]
for ob in list(SCENE.objects):
    if ob.name=='Forest_Back_Ground' or ob.name.startswith('Forest_Bamboo_DeepRow_'):
        old_trees.append(ob)
        for collection in list(ob.users_collection):collection.objects.unlink(ob)
        ARCH.objects.link(ob);ob.hide_render=True;ob.hide_set(True)
LAYOUT['forest_extension']['groves']=[g for g in LAYOUT['forest_extension']['groves'] if not g['name'].startswith('Forest_Bamboo_DeepRow_')]

def sm2(a,b,v):
    t=max(0,min(1,(v-a)/(b-a)));return t*t*(3-2*t)
def valley_height(x,y):
    # Match the previous join at y=29; dip into the valley, then climb again.
    near=1.32-.28*(y-30)+.12*math.sin(x*.18+y*.31)
    basin=.55+.20*math.sin(x*.085)+.10*math.sin(x*.16+y*.19)
    h=near*(1-sm2(29,39,y))+basin*sm2(29,39,y)
    h+=7.4*sm2(44,72,y)+6.6*sm2(63,91,y)
    h+=1.35*sm2(42,78,y)*math.sin(x*.075+1.2)
    return h

vs=[];fs=[]
nx=69;ny=42
for ix in range(nx):
    x=-98+ix*1.6
    for iy in range(ny):
        y=29+iy*1.55;vs.append((x,y,valley_height(x,y)))
for ix in range(nx-1):
    for iy in range(ny-1):
        a=ix*ny+iy;fs.extend([(a,a+ny,a+ny+1),(a,a+ny+1,a+1)])
ground=Mesh('Forest_Valley_Ground')
ground.part(vs,fs,bpy.data.materials['Forest_Floor'],[((p[0]+50)/54,(min(p[1],38)+4)/40) for p in vs])
ground.build(smooth=True)

old_bvhs=[]
for name in ['WALK_Forest_Ground','Forest_Back_Ground']:
    ob=SCENE.objects[name]
    old_bvhs.append(BVHTree.FromPolygons([v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons]))
def old_height(x,y,fallback):
    hits=[b.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))[0] for b in old_bvhs]
    heights=[h.z for h in hits if h is not None]
    return max(heights) if heights else fallback

created=[]
rows=[(45.0,-90.0,11,8.7,1.18),(61.0,-93.0,13,8.0,1.35),(79.0,-95.0,14,7.6,1.48)]
for row,(cy,start,count,spacing,scale) in enumerate(rows):
    for j in range(count):
        cx=start+j*spacing
        cy2=cy+[1.6,-1.0,.6,-1.7,.3][(j+row)%5]
        index=33+(j+row*2)%5;body,canopy=source_trees[index]
        points=[Vector(p) for p in body.bound_box]
        sx=(min(p.x for p in points)+max(p.x for p in points))*.5
        sy=(min(p.y for p in points)+max(p.y for p in points))*.5
        base=min(p.z for p in points)
        angle=[-.18,.13,.28,-.09,.05][(j+row)%5]
        xy_scale=[1.16,1.32,1.24,1.38,1.20][(j+row)%5]
        tall=scale*[1.0,.91,1.07,.97,1.02][(j+row)%5]
        for part,src in enumerate([body,canopy]):
            ob=src.copy();ob.data=src.data.copy();ob.name='Forest_Bamboo_Valley_%d_%02d_%d'%(row,j,part);COL.objects.link(ob)
            for v in ob.data.vertices:
                p=v.co.copy();dx=(p.x-sx)*xy_scale;dy=(p.y-sy)*xy_scale
                x=cx+dx*math.cos(angle)-dy*math.sin(angle)
                y=cy2+dx*math.sin(angle)+dy*math.cos(angle)
                floor=old_height(p.x,p.y,base+.03)
                v.co=(x,y,valley_height(x,y)+(p.z-floor)*tall)
            ob.data.update();ob.hide_set(False);ob.hide_render=False
            LAYOUT['forest_extension']['groves'].append({'name':ob.name,'band':'valley_far' if row>0 else 'valley_middle'})
            created.append(ob.name)

LAYOUT['forest_extension']['valley_enclosed']={'collection':COL.name,'ground':'Forest_Valley_Ground','background':'misty woodland, no open sea or sky from west path','bounds':[-98,10.8,29,92.55]}
(REVIEW/'build-report.json').write_text(json.dumps({'new_objects':created,'archived':[o.name for o in old_trees],'ground_vertices':len(vs),'ground_faces':len(fs)},indent=2),encoding='utf-8')
export('valley-forest-backdrop')
