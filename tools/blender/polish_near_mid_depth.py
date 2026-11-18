"""Blender MCP: cohesive exposed soil and restrained foreground leaf scale."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
REVIEW=ROOT/'artifacts/near-mid-depth-review'
data=LAYOUT['forest_extension']['near_mid_depth'];assert not data.get('edge_polish'),'Inspect saved polish rather than repeat it.'
COL=bpy.data.collections['48_Near_Middle_Depth']
ob=SCENE.objects['WALK_Forest_Ground'];me=ob.data
# Restore the continuous ground painting. Per-triangle color changes were
# making a torn outline; exposed earth is instead a few fitted bank surfaces.
for p in me.polygons:
    p.material_index=0
    for li in p.loop_indices:
        co=me.vertices[me.loops[li].vertex_index].co;me.uv_layers[0].data[li].uv=((co.x+50)/54,(co.y+4)/40)
while len(me.materials)>1:me.materials.pop(index=len(me.materials)-1)
me.update()
tree=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons])
def ground(x,y):
    hit=tree.ray_cast(Vector((x,y,35)),Vector((0,0,-1)))[0];assert hit,(x,y)
    return hit.z
route=[A[k] for k in ['forest_west_entry','forest_west_gate','forest_west_light','forest_west_mid','forest_west_shade','forest_west_end']]
def center_y(x):
    for a,b in zip(route,route[1:]):
        if min(a.x,b.x)<=x<=max(a.x,b.x):return a.y+(b.y-a.y)*(x-a.x)/(b.x-a.x)
    return route[-1].y if x<route[-1].x else route[0].y
def rim(x):return 1.10+.15*math.sin((x+37)*.34)+.07*math.sin((x+21)*.67)
patches=[]
for index,(left,right) in enumerate([(-43.0,-39.8),(-36.7,-31.6),(-28.9,-24.1),(-22.0,-19.5)]):
    builder=Mesh('Forest_Eroded_Bank_%02d'%index)
    segments=math.ceil((right-left)/.28)
    for j in range(segments):
        xs=[left+(right-left)*j/segments,left+(right-left)*(j+1)/segments]
        quad=[]
        for x in xs:
            fade=sm(left,left+.55,x)*(1-sm(right-.55,right,x))
            y=center_y(x)-rim(x)+.005
            top=ground(x,y)+.012
            front=y-.16*fade
            bottom=ground(x,front)+.012
            # Fitted slope surface slightly above the underlying earth;
            # ends narrow into the same bank without detached blocks.
            quad.extend([(x,y-.005,top),(x,front-.005,bottom)])
        builder.part(quad,[(0,2,3,1)],'soil',[(p[0]*.30,p[2]*.55) for p in quad])
    built=builder.build();built['role']='small exposed surface following the actual earthen bank'
    patches.append(built.name)

def groups(me):
    adjacency=[[] for _ in me.vertices]
    for e in me.edges:
        a,b=e.vertices;adjacency[a].append(b);adjacency[b].append(a)
    seen=set()
    for start in range(len(me.vertices)):
        if start in seen:continue
        ids=[];todo=[start];seen.add(start)
        while todo:
            i=todo.pop();ids.append(i)
            for k in adjacency[i]:
                if k not in seen:seen.add(k);todo.append(k)
        yield ids
leaf_changes=[]
for index in range(3):
    leaf=SCENE.objects['Forest_Bamboo_Role_FrontLeaf_%02d'%index]
    for ids in groups(leaf.data):
        c=sum((leaf.data.vertices[i].co for i in ids),Vector())/len(ids)
        for i in ids:
            v=leaf.data.vertices[i];v.co=c+(v.co-c)*.64+Vector((0,0,1.05))
    leaf.data.update()
    body=SCENE.objects['Forest_Bamboo_Role_Front_%02d'%index]
    branch=set()
    for p in body.data.polygons:
        if body.data.materials[p.material_index].name=='LF_branch':branch.update(p.vertices)
    for i in branch:body.data.vertices[i].co.z+=1.05
    body.data.update()
    leaf_changes.append({'leaf':leaf.name,'scale_about_each_card':.64,'lift':1.05,'attached_branches_lifted':True})
data['edge_polish']={'fitted_earth_patches':patches,'foreground_leaf_changes':leaf_changes,'reason':'cohesive real earth edges and smaller attached leaves above the actor band'}
(REVIEW/'author-polish.json').write_text(json.dumps(data['edge_polish'],indent=2),encoding='utf-8')
export('near-middle-depth-polish')
