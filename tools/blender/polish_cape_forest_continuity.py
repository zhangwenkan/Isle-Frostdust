"""Round the original back edge and remove buried wall seams through Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
record=LAYOUT['reference_cape']['forest_continuity'];assert not record.get('back_edge_polish')
COL=bpy.data.collections['50_Cape_Forest_Continuity'];archive=bpy.data.collections['90_Before_Cape_Forest_Continuity']
originals={n:SCENE.objects['Continuity_Before_'+n] for n in ['WALK_Forest_Ground','WALK_Forest_NearSlope']}
trees=[BVHTree.FromPolygons([v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons]) for ob in originals.values()]
def original_height(x,y):
    xx=max(-62.98,x);hits=[t.ray_cast(Vector((xx,y,40)),Vector((0,0,-1)))[0] for t in trees];hits=[h.z for h in hits if h is not None]
    return max(hits) if hits else 6.28
def h(x,y):
    road=4.55+1.73*sm(-70,-53.5,x);center=13.7-1.5*sm(-61,-69,x)
    desired=road+.02*(y-center)-.14*(1-sm(8,11.5,y))-.63*(1-sm(-3,8,y))
    old=original_height(x,y);return old+(desired-old)*(1-sm(-57,-53.5,x))
def n(x,y):
    e=.035;return Vector((-(h(x+e,y)-h(x-e,y))/(2*e),-(h(x,y+e)-h(x,y-e))/(2*e),1)).normalized()
for name,old in originals.items():
    ob=SCENE.objects[name];before=ob.copy();before.data=ob.data.copy();before.name=name+'_Continuity_Pass1';archive.objects.link(before);before.hide_set(True);before.hide_render=True
    for v,source in zip(ob.data.vertices,old.data.vertices):
        p=source.co.copy()
        if p.x>=-53.5:continue
        if name=='WALK_Forest_Ground':
            factor=(1-sm(-61.24,-53.5,p.x))*sm(11,17,p.y)*(1-sm(20,34,p.y))
            p.x-=6.0*factor
            # The old low sheet used to sit under the near bank. Lift it to
            # within 2 cm of the shared top so it cannot expose internal walls.
            p.z=h(p.x,p.y)-.020
        else:p.z=h(p.x,p.y)
        v.co=p
    ob.data.update();norm=[]
    for p in ob.data.polygons:
        for li in p.loop_indices:
            co=ob.data.vertices[ob.data.loops[li].vertex_index].co
            norm.append(tuple(n(co.x,co.y)) if co.x<-53.5 else tuple(ob.data.corner_normals[li].vector))
    ob.data.normals_split_custom_set(norm)
# Keep the terrain's eastern connection smooth, including rear parts that had
# retained the first pass's abrupt height recovery.
ob=SCENE.objects['WALK_Cape_Neck']
for v in ob.data.vertices:v.co.z=h(v.co.x,v.co.y)
ob.data.update();norm=[]
for p in ob.data.polygons:
    for li in p.loop_indices:
        co=ob.data.vertices[ob.data.loops[li].vertex_index].co;norm.append(tuple(n(co.x,co.y)))
ob.data.normals_split_custom_set(norm)
# Internal neck walls are obsolete where land now covers both sides. Retain
# the outer far section and archive the pre-polish mesh for recovery.
ob=SCENE.objects['Cape_Neck_Rockside'];saved=ob.copy();saved.data=ob.data.copy();saved.name='Cape_Neck_Rockside_Continuity_Pass1';archive.objects.link(saved);saved.hide_set(True);saved.hide_render=True
bm=bmesh.new();bm.from_mesh(ob.data)
remove=[f for f in bm.faces if f.calc_center_median().x>-67.0]
bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(ob.data);bm.free();ob.data.update()
ground=SCENE.objects['WALK_Forest_Ground'].data;counts={}
for p in ground.polygons:
    for a,b in zip(p.vertices,list(p.vertices)[1:]+list(p.vertices)[:1]):
        key=tuple(sorted((a,b)));counts[key]=counts.get(key,0)+1
MATS['cape_side']=[m for m in bpy.data.materials if m.name.startswith('RC_cape_side')][-1]
wall=Mesh('Cape_Forest_Backbank')
for (a,b),count in counts.items():
    if count!=1:continue
    p=ground.vertices[a].co;q=ground.vertices[b].co
    if max(p.x,q.x)>-53.6:continue
    wall.part([p,q,(q.x,q.y,-1.4),(p.x,p.y,-1.4)],[(0,1,2,3)],'cape_side')
wall.build()
record['back_edge_polish']={'western_edge_curved_into_mouth_m':6.0,'internal_walls_removed_east_of':-67.0,'new_back_edge_closed':True,'new_object':'Cape_Forest_Backbank','hidden_ground_separation_m':.020}
export('cape-forest-continuity-back-edge')
