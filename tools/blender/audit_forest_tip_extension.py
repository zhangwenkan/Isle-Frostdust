"""Read Blender route support, joined edges, original UVs and plant contact."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
O=ROOT/'artifacts/forest-tip-extension-review'
def tree(ob):return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons])
live=[o for o in SCENE.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
floors=[(o.name,tree(o)) for o in live if o.name.startswith('WALK_')]
solid=[(o.name,tree(o)) for o in live if o.name.startswith(('Cape_Cliff_','Cape_Tip_','Cape_Fire_Ring_','Cape_Fire_Log_','Cape_Timber'))]
ground=SCENE.objects['WALK_Forest_Ground'];terrain=tree(ground)
failures=[];samples=0;steps=[];clearance=[]
routes=[e for e in LAYOUT['edges'] if any(k.startswith(('cape_','forest_cape_')) for k in e)]
for a,b in routes:
    pa=Vector(LAYOUT['anchors'][a]);pa=Vector((pa.x,-pa.z,pa.y));pb=Vector(LAYOUT['anchors'][b]);pb=Vector((pb.x,-pb.z,pb.y));previous=None
    for i in range(121):
        center=pa.lerp(pb,i/120)
        for side in [-.22,0,.22]:
            p=center+Vector((0,side,0));hits=[(n,t.ray_cast(Vector((p.x,p.y,40)),Vector((0,0,-1)))[0]) for n,t in floors];hits=[(n,h) for n,h in hits if h is not None]
            if not hits:failures.append({'edge':[a,b],'t':i/120,'side':side,'error':'no floor'});continue
            n,h=max(hits,key=lambda r:r[1].z);samples+=1
            if side==0:
                if previous is not None:steps.append(abs(h.z-previous))
                previous=h.z
                for name,t in solid:
                    q=t.ray_cast(Vector((p.x,p.y,40)),Vector((0,0,-1)))[0]
                    if q is not None and q.z>h.z+.32:clearance.append({'edge':[a,b],'t':i/120,'obstacle':name,'height_above_floor':q.z-h.z})
if clearance:failures.append({'blocked_route':clearance})
# The terrain is one mesh, with no boundary edges along either former seam.
bm=bmesh.new();bm.from_mesh(ground.data)
seam_edges=[list(e.verts[0].co)+list(e.verts[1].co) for e in bm.edges if len(e.link_faces)==1 and ((abs(e.verts[0].co.x+61.24)<.005 and abs(e.verts[1].co.x+61.24)<.005) or (abs(e.verts[0].co.x+63.04)<.005 and abs(e.verts[1].co.x+63.04)<.005))]
bm.free()
if seam_edges:failures.append({'unwelded_seam_edges':seam_edges})
def payload(me):
    me.calc_loop_triangles()
    return {tuple(sorted(tuple(round(c,6) for c in (*me.vertices[vi].co,*me.uv_layers[0].data[li].uv)) for vi,li in zip(t.vertices,t.loops))) for t in me.loop_triangles}
current=payload(ground.data);original={}
for name in ['WALK_Forest_Ground','WALK_Forest_NearSlope']:
    old=payload(SCENE.objects['Tip_Before_'+name].data);missing=old-current;original[name]={'triangles':len(old),'original_position_uv_triangles_missing':len(missing)}
    if missing:failures.append({'old_geometry_or_uv_changed':name,'missing_triangles':len(missing)})
contacts=[];root_trees=[t for n,t in floors]+[t for n,t in solid if n.startswith(('Cape_Cliff_','Cape_Tip_'))]
me=SCENE.objects['Cape_Shore_Grass'].data
for p in me.polygons:
    ids=[me.loops[li].vertex_index for li in p.loop_indices if me.uv_layers[1].data[li].uv.x<.01]
    if len(ids)!=2:failures.append({'grass_face':p.index,'root_vertices':len(ids)});continue
    root=(me.vertices[ids[0]].co+me.vertices[ids[1]].co)/2
    near=[t.find_nearest(root)[0] for t in root_trees];near=[h for h in near if h is not None]
    error=min((h-root).length for h in near) if near else None
    contacts.append(error)
    if error is None or error>.07:failures.append({'grass_face':p.index,'contact_error':error,'root':list(root)})
meshes=[]
for ob in live:
    if not (ob.name.startswith(('Cape_','WALK_Cape_')) or ob==ground):continue
    bad=[p.index for p in ob.data.polygons if p.area<1e-10 or not all(math.isfinite(c) for c in p.normal)]
    if bad:failures.append({'mesh':ob.name,'bad_faces':bad})
    meshes.append({'name':ob.name,'faces':len(ob.data.polygons),'uv_layers':len(ob.data.uv_layers),'bad_faces':len(bad)})
record={'source':bpy.data.filepath,'revision':LAYOUT['revision'],'route_samples':samples,'routes':routes,'maximum_sampled_step_m':max(steps),'route_obstacles':clearance,'unwelded_seam_edges':seam_edges,'original_position_uv':original,'grass_contact_errors':contacts,'meshes':meshes,'failures':failures}
(O/'blender-audit.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k not in ['routes','meshes','grass_contact_errors']},ensure_ascii=False))
assert not failures
