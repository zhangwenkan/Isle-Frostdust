"""Reconnect our existing rock relief into a continuous bedrock shell via Blender MCP.
Keep the actual ground top, reshape only the coast's outer skin and turf junction.
"""
import bpy,bmesh,math,bisect,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/coast-integration-review';A=R/'assets/original_coastal_rock'
s=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=s
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
def signature(o):
    h=hashlib.sha256()
    for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
    for f in o.data.polygons:h.update(str(tuple(f.vertices)).encode())
    for l in o.data.uv_layers:
        for d in l.data:h.update(str(tuple(d.uv)).encode())
    h.update(str(o.matrix_world).encode());return h.hexdigest()
def active(o):return o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)
other={o.name:signature(o) for o in s.objects if active(o) and not o.name.startswith(('Original_Coast_','Integrated_Coast_')) and o.name!='Fish_West_Continuous_Land'}
arc=bpy.data.collections.get('90_Before_Coast_Integration') or bpy.data.collections.new('90_Before_Coast_Integration')
if arc.name not in s.collection.children:s.collection.children.link(arc)
arc.hide_render=True
land=s.objects['Fish_West_Continuous_Land'];base=bpy.data.objects.get('IntegrationBaseline_Land')
if base is None:
    base=land.copy();base.data=land.data.copy();base.name='IntegrationBaseline_Land';arc.objects.link(base);base.hide_render=True;base.hide_set(True)
land.data=base.data.copy()
rocks=[o for o in s.objects if o.name.startswith('Original_Coast_Rock_')]
assert len(rocks)==18
sv=[];sf=[]
for ob in rocks:
    off=len(sv);sv.extend([ob.matrix_world@v.co for v in ob.data.vertices]);sf.extend([tuple(i+off for i in p.vertices) for p in ob.data.polygons])
tree=BVHTree.FromPolygons(sv,sf)
for ob in rocks:
    for c in list(ob.users_collection):c.objects.unlink(ob)
    arc.objects.link(ob);ob.hide_render=True;ob.hide_set(True)
col=bpy.data.collections.get('37_Integrated_Coastal_Mass') or bpy.data.collections.new('37_Integrated_Coastal_Mass')
if col.name not in s.collection.children:s.collection.children.link(col)
for ob in list(col.objects):bpy.data.objects.remove(ob,do_unlink=True)
top=[base.matrix_world@v.co for v in list(base.data.vertices)[:2626]]
boundary=[i*26 for i in range(101)]+[2600+j for j in range(1,26)]+[i*26+25 for i in range(99,-1,-1)]+list(range(24,0,-1))
perimeter=[top[i] for i in boundary];lengths=[0.]
for j in range(250):lengths.append(lengths[-1]+(perimeter[(j+1)%250]-perimeter[j]).length)
total=lengths[-1]
def frame(u):
    u=u%total;j=min(249,bisect.bisect_right(lengths,u)-1);t=(u-lengths[j])/(lengths[j+1]-lengths[j])
    p=perimeter[j].lerp(perimeter[(j+1)%250],t)
    tangent=perimeter[(j+1)%250]-perimeter[j]
    return p,Vector((-tangent.y,tangent.x,0)).normalized()
def smooth(a,b,x):
    t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def periodic_dist(a,b):return min(abs(a-b),total-abs(a-b))
# The previous planar boundary made every material blend read as a ribbon.
# Reshape only the outer 0.7 m of turf; retain the walking corridor and fire support.
ground_changes=[];protected=[]
for index in range(2626):
    v=land.data.vertices[index];q=land.matrix_world@v.co;best=(1e9,0.)
    for j,p in enumerate(perimeter):
        b=perimeter[(j+1)%250];a=Vector((p.x,p.y));ab=Vector((b.x-p.x,b.y-p.y));point=Vector((q.x,q.y))
        t=max(0,min(1,(point-a).dot(ab)/max(ab.length_squared,1e-8)));dist=(point-a-ab*t).length
        if dist<best[0]:best=(dist,lengths[j]+t*(lengths[j+1]-lengths[j]))
    dist,u=best
    safe=smooth(1.05,1.55,abs(q.y+.25))
    safe*=smooth(1.35,1.8,math.hypot(q.x+27.35,q.y-2.15))
    weight=(1-smooth(.0,.70,dist))*safe
    if weight<=1e-7:protected.append(index);continue
    p,n=frame(u);origin=p+n*1.6;origin.z=p.z-.65
    hit=tree.ray_cast(origin,-n,3.0)[0]
    shoulder=max(0,min(.55,(hit-p).dot(n))) if hit is not None else 0.
    outward=(.055+.58*shoulder+.055*math.sin(u*1.63)+.035*math.sin(u*3.1+.6))*weight
    drop=(.025+.075*(.5+.5*math.sin(u*1.47+.5)))*weight
    v.co+=land.matrix_world.inverted().to_3x3()@(n*outward+Vector((0,0,-drop)))
    ground_changes.append((index,outward,drop))
top=[land.matrix_world@v.co for v in list(land.data.vertices)[:2626]]
perimeter=[top[i] for i in boundary];lengths=[0.]
for j in range(250):lengths.append(lengths[-1]+(perimeter[(j+1)%250]-perimeter[j]).length)
total=lengths[-1]
# Preserve the exact terrain boundary vertices, and insert enough points for the
# original large facets and shallow joins to survive silhouette reconstruction.
stations=[]
for j in range(250):
    count=max(1,math.ceil((lengths[j+1]-lengths[j])/.23))
    stations.extend(lengths[j]+(lengths[j+1]-lengths[j])*k/count for k in range(count))
N=len(stations)
depths=[0,.13,.34,.66,1.05,1.48,1.92,2.40,2.95,3.60,4.35,5.60]
# Stronger geological joints are deliberately fewer than the original module seams.
targets=[(-26.1,-2.4),(-18.4,-3.0),(-10.8,-4.1),(-3.0,-3.7),(3.6,-1.5),(-8,5.9),(-23,3.2)]
joints=[]
for x,y in targets:
    idx=min(range(N),key=lambda k:(frame(stations[k])[0].x-x)**2+(frame(stations[k])[0].y-y)**2)
    joints.append(stations[idx])
raw=[];zs=[];misses=0
for k,u in enumerate(stations):
    p,n=frame(u);rr=[];zz=[]
    for h in depths:
        depth=h+(.08*math.sin(u*.73)+.055*math.sin(u*1.7+1.1))*math.sin(math.pi*min(h/5.6,1))
        z=p.z-depth;origin=p+n*1.65;origin.z=z
        hit,normal,face,distance=tree.ray_cast(origin,-n,3.0)
        radius=(hit-p).dot(n) if hit is not None else -.25
        if hit is None:misses+=1
        rr.append(max(-.48,min(1.15,radius)));zz.append(z)
    raw.append(rr);zs.append(zz)
def neighbors(k,radius):
    return [j for j in range(N) if periodic_dist(stations[k],stations[j])<=radius]
near=[neighbors(k,.46) for k in range(N)];wide=[neighbors(k,.78) for k in range(N)]
verts=[];uv_coords=[];radii=[]
for k,u in enumerate(stations):
    p,n=frame(u);row=[]
    # Turf thickness belongs to the ground, with occasional rock reaching the edge.
    grass_depth=.10+.18*(.5+.5*math.sin(u*.83+.8))*(.5+.5*math.sin(u*.31+1.1))
    for hidx,h in enumerate(depths):
        if hidx==0:r=0.;z=p.z
        else:
            local=sum(raw[j][hidx] for j in near[k])/len(near[k])
            shoulder=max(raw[j][hidx] for j in wide[k])
            # Close secondary deep slits while keeping the existing broad rock relief.
            r=.46*raw[k][hidx]+.32*local+.22*shoulder-.065
            joint=max(math.exp(-(periodic_dist(u,(q+.18*math.sin(h*1.1+i))%total)/(.22+.04*(i%3)))**2)*( .12+.06*(i%3)) for i,q in enumerate(joints))
            r-=joint*smooth(.30,1.0,h)*(1-.45*smooth(3.0,5.6,h))
            # The upper rock slopes directly into the turf. No separate flat bright cap.
            w=smooth(.02,.38,h)
            r=r*w+.015*(1-w);z=zs[k][hidx]
        verts.append(tuple(p+n*r+Vector((0,0,z-p.z))))
        uv_coords.append((u/total,1-h/5.6));row.append(r)
    radii.append(row)
faces=[];uvs=[]
H=len(depths)
for k in range(N):
    kk=(k+1)%N
    for j in range(H-1):
        ids=(k*H+j,kk*H+j,kk*H+j+1,k*H+j+1);faces.append(ids)
        for index in ids:
            u,v=uv_coords[index]
            if k==N-1 and index//H==0:u=1.0
            uvs.append((u,v))
faces.append(tuple(k*H+H-1 for k in reversed(range(N))))
uvs.extend([(stations[k]/total,0.) for k in reversed(range(N))])
me=bpy.data.meshes.new('Continuous_Authored_Bedrock');me.from_pydata(verts,[],faces);me.update()
uv=me.uv_layers.new(name='ContinuousShoreUV');uv.data.foreach_set('uv',[v for pair in uvs for v in pair])
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4]);bm.to_mesh(me);bm.free()
mat=bpy.data.materials.get('Integrated_Coast_Painted') or bpy.data.materials.new('Integrated_Coast_Painted');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=1
tx=mat.node_tree.nodes.get('IntegratedPaint') or mat.node_tree.nodes.new('ShaderNodeTexImage');tx.name='IntegratedPaint'
paint=A/'integrated_coast_paint.png'
if paint.exists():tx.image=bpy.data.images.load(str(paint),check_existing=True);tx.image.reload();mat.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
else:bs.inputs['Base Color'].default_value=(.38,.25,.17,1)
me.materials.append(mat)
ob=bpy.data.objects.new('Integrated_Coast_Surface',me);col.objects.link(ob)
# Keep broad facets crisp while smoothing small sampling steps within a face.
for poly in me.polygons:poly.use_smooth=False
bm=bmesh.new();bm.from_mesh(me)
for edge in bm.edges:
    if edge.is_manifold:edge.smooth=edge.calc_face_angle()<math.radians(28)
bm.to_mesh(me);bm.free()
ob['source']='Outer relief of original authored coastal modules, reconnected into continuous bedrock through Blender MCP'
ob['primary_joint_count']=len(joints)
def closest_shore(q):
    best=(1e9,0.,0.)
    for j,p in enumerate(perimeter):
        b=perimeter[(j+1)%250];a=Vector((p.x,p.y));ab=Vector((b.x-p.x,b.y-p.y));point=Vector((q.x,q.y))
        t=max(0,min(1,(point-a).dot(ab)/max(ab.length_squared,1e-8)));dist=(point-a-ab*t).length
        if dist<best[0]:best=(dist,lengths[j]+t*(lengths[j+1]-lengths[j]),p.z*(1-t)+b.z*t)
    return best
# Retain the authored foreground facets and low shoulders. The new mass fills
# their minor clefts and connects their upper roots to the actual turf edge.
for original in rocks:
    child=original.copy();child.data=original.data.copy();child.name=original.name.replace('Original_','Integrated_',1)
    col.objects.link(child);child.hide_render=False;child.hide_set(False)
    while len(child.data.uv_layers)>1:child.data.uv_layers.remove(child.data.uv_layers[-1])
    child.data.materials.clear();child.data.materials.append(mat)
    for face in child.data.polygons:face.material_index=0
    vertex_uv=[]
    for v in child.data.vertices:
        q=child.matrix_world@v.co;dist,u,height=closest_shore(q)
        vertex_uv.append((u/total,1-max(0,min(1,(height-q.z)/5.6))))
    uv=child.data.uv_layers[0]
    for face in child.data.polygons:
        coordinates=[vertex_uv[child.data.loops[i].vertex_index] for i in face.loop_indices]
        wraps=max(p[0] for p in coordinates)-min(p[0] for p in coordinates)>.5
        for index,pair in zip(face.loop_indices,coordinates):
            u,v=pair
            if wraps and u<.5:u+=1.
            uv.data[index].uv=(u,v)
    child.data.uv_layers.active_index=0;child.data.uv_layers[0].active_render=True
# Existing grass top is untouched geometrically; remove only the exposed old cap
# by retracting its side rings behind the new skin. Inner core stays closed.
for i in range(2626,len(land.data.vertices)):
    v=land.data.vertices[i];q=base.data.vertices[i].co
    nearest=min(range(250),key=lambda k:(perimeter[k].x-q.x)**2+(perimeter[k].y-q.y)**2)
    p,n=frame(lengths[nearest]);h=max(0,p.z-q.z)
    if h<.65:v.co.x-=n.x*.24;v.co.y-=n.y*.24
# A dedicated land UV channel encodes edge mix and the shared coastal paint position.
edge_uv=land.data.uv_layers.get('CoastEdgeBlend') or land.data.uv_layers.new(name='CoastEdgeBlend')
edge_data=[]
for vertex in land.data.vertices:
    q=land.matrix_world@vertex.co;best=(1e9,0.)
    for j,p in enumerate(perimeter):
        b=perimeter[(j+1)%250];a=Vector((p.x,p.y));ab=Vector((b.x-p.x,b.y-p.y));point=Vector((q.x,q.y))
        t=max(0,min(1,(point-a).dot(ab)/max(ab.length_squared,1e-8)));dist=(point-a-ab*t).length
        if dist<best[0]:best=(dist,lengths[j]+t*(lengths[j+1]-lengths[j]))
    dist,u=best;extent=.20+.28*(.5+.5*math.sin(u*.81+.8))*(.5+.5*math.sin(u*.32))
    # Sparse bare rock patches reach into the grass edge; retain long quiet turf runs.
    patch=.22+.64*(.5+.5*math.sin(u*.63+1.7))**3
    weight=(1-smooth(.0,extent,dist))*patch
    edge_data.append((weight,u/total))
for loop in land.data.loops:edge_uv.data[loop.index].uv=edge_data[loop.vertex_index]
land.data.uv_layers.active_index=0;land.data.uv_layers[0].active_render=True
assert all((land.data.vertices[i].co-base.data.vertices[i].co).length==0 for i in protected)
assert all(signature(s.objects[name])==sig for name,sig in other.items())
info={'perimeter_m':total,'stations':N,'depths':depths,'joints':joints,'preserved_other_blender_meshes':len(other),'protected_ground_vertices_unchanged':len(protected),'edge_ground_vertices_changed':len(ground_changes),'max_edge_outward_m':max(v[1] for v in ground_changes),'max_edge_drop_m':max(v[2] for v in ground_changes),'archived_modules':18,'source_ray_misses':misses,'vertices':len(me.vertices),'faces':len(me.polygons),'stations_data':[{'u':u/total,'s':u,'point':list(frame(u)[0]),'radii':radii[k]} for k,u in enumerate(stations)]}
(O/'integration-authoring.json').write_text(json.dumps(info,indent=2),encoding='utf8')
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
print('COAST_INTEGRATED',N,'stations; preserved',len(other),'meshes')
