"""Read the imported-author cape geometry, route clearance and mesh validity."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/reference-cape-review'
scene=bpy.data.scenes['Layered_Island_20261116'];layout=json.loads((ROOT/'assets/layered_island/layout.json').read_text(encoding='utf-8'))
def tree(ob):return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons])
floors=[(o.name,tree(o)) for o in scene.objects if o.type=='MESH' and o.name.startswith('WALK_') and not any(c.name.startswith('90_') for c in o.users_collection)]
obstacles=[(o.name,tree(o)) for o in bpy.data.collections['49_Reference_Cape'].objects if o.type=='MESH' and o.name.startswith(('Cape_Cliff_','Cape_Timber','Cape_Fire_Ring_','Cape_Fire_Log_'))]
routes=[e for e in layout['edges'] if any(k.startswith(('cape_','forest_cape_')) for k in e)]
failures=[];clearance=[];count=0;previous=None;maxstep=0.;meshes=[]
for a,b in routes:
    pa=Vector(layout['anchors'][a]);pa=Vector((pa.x,-pa.z,pa.y));pb=Vector(layout['anchors'][b]);pb=Vector((pb.x,-pb.z,pb.y));previous=None
    for i in range(121):
        p=pa.lerp(pb,i/120)
        hits=[(name,t.ray_cast(Vector((p.x,p.y,40)),Vector((0,0,-1)))[0]) for name,t in floors];hits=[(n,h) for n,h in hits if h is not None]
        if not hits:failures.append({'edge':[a,b],'t':i/120,'error':'no floor'});continue
        name,h=max(hits,key=lambda r:r[1].z);count+=1
        if previous is not None:maxstep=max(maxstep,abs(h.z-previous))
        previous=h.z
        for obstacle,t in obstacles:
            q=t.ray_cast(Vector((p.x,p.y,40)),Vector((0,0,-1)))[0]
            if q is not None and q.z>h.z+.32:clearance.append({'edge':[a,b],'t':i/120,'obstacle':obstacle,'obstacle_top':q.z,'floor':h.z})
for ob in bpy.data.collections['49_Reference_Cape'].objects:
    if ob.type!='MESH':continue
    bad=[p.index for p in ob.data.polygons if p.area<1e-10 or not all(math.isfinite(c) for c in p.normal)]
    if bad:failures.append({'mesh':ob.name,'bad_faces':bad})
    meshes.append({'name':ob.name,'faces':len(ob.data.polygons),'uv_layers':len(ob.data.uv_layers),'bad_faces':len(bad)})
if clearance:failures.append({'route_obstacle_intersections':clearance})
old=scene.objects['WALK_Forest_NearSlope'];shoulder=tree(scene.objects['Cape_Connection_Shoulder'])
seam_samples=[]
for v in old.data.vertices:
    if abs(v.co.x+63.04)<.002:
        hit=shoulder.ray_cast(Vector((v.co.x-.0001,v.co.y,40)),Vector((0,0,-1)))[0]
        # Boundary rays can fall a fraction outside the tessellated footprint.
        near=shoulder.find_nearest(v.co)[0]
        error=(near-v.co).length if near is not None else None
        seam_samples.append({'point':list(v.co),'error':error})
        if error is None or error>.06:failures.append({'seam':list(v.co),'error':error})
plant_checks=[]
root_trees=[t for n,t in floors]+[tree(o) for o in bpy.data.collections['49_Reference_Cape'].objects if o.type=='MESH' and (o.name.startswith('Cape_Cliff_') or o.name in ['Cape_Attached_Cliff_Core','Cape_Connection_Shoulder'])]
for p in scene.objects['Cape_Shore_Grass'].data.polygons:
    verts=scene.objects['Cape_Shore_Grass'].data.vertices
    grass=scene.objects['Cape_Shore_Grass'].data
    roots=[grass.loops[li].vertex_index for li in p.loop_indices if grass.uv_layers[1].data[li].uv.x<.01]
    assert len(roots)==2
    root=(verts[roots[0]].co+verts[roots[1]].co)/2
    # Grass can attach to a lower ledge below an overhang. Measure actual
    # surface contact rather than assuming the highest downward hit is its root.
    near=[t.find_nearest(root)[0] for t in root_trees];near=[h for h in near if h is not None]
    error=min((h-root).length for h in near) if near else None
    plant_checks.append(error)
    if error is None or error>.07:failures.append({'grass_root':p.index,'error':error})
report={'source':bpy.data.filepath,'route_edges':routes,'route_samples':count,'max_sampled_height_step':maxstep,'obstacle_intersections':clearance,'seam_samples':seam_samples,'grass_root_errors':plant_checks,'meshes':meshes,'failures':failures}
(OUT/'blender-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','route_edges']}))
assert not failures
