"""Extend the upper bamboo path WEST; executed only through Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
REVIEW=ROOT/'artifacts/bamboo-west-extension-review'
assert not bpy.data.collections.get('43_West_Forest'),'Extension already authored; refine rather than rebuild.'
COL=bpy.data.collections.new('43_West_Forest');SCENE.collection.children.link(COL)
old_edges=list(LAYOUT['edges']);old_anchors=dict(LAYOUT['anchors'])
ground=SCENE.objects['WALK_Left_Ground']
oldtree=BVHTree.FromPolygons([v.co for v in ground.data.vertices],[list(p.vertices) for p in ground.data.polygons])
# The path exits the existing top stair and turns left. It stays predominantly
# horizontal for ~30 m; depth changes are reserved for banks and the rear grove.
route=[('forest_west_entry',[-17.0,5.96,-12.35]),('forest_west_gate',[-21.4,6.08,-12.7]),('forest_west_light',[-27.0,6.18,-12.95]),('forest_west_mid',[-32.5,6.17,-12.8]),('forest_west_shade',[-37.8,6.32,-13.1]),('forest_west_end',[-43.4,6.40,-13.7])]
prev='forest_end'
for key,point in route:
    LAYOUT['anchors'][key]=point;A[key]=Vector((point[0],-point[2],point[1]));LAYOUT['edges'].append([prev,key]);prev=key
new_edges=LAYOUT['edges'][len(old_edges):]
boundary=[(-48.5,8.0),(-41.0,7.7),(-34,8.2),(-28,7.5),(-22,7.1),(-18.36,7.65),(-18.6,9.9),(-18,13.2),(-15.6,15.1),(-12.4,14.3),(-10,12.4),(-9.6,10.1),(-7.9,9.4),(-6.3,7.4),(-4.5,5.8),(-3.1,4.18),(-1.25,3.26),(1.2,7.5),(.5,15),(-4,24),(-12,31),(-28,34),(-43,32),(-48.5,27)]
join=boundary[5:17]
def closest_segment(x,y,p,q):
    v=Vector(q)-Vector(p);t=max(0,min(1,(Vector((x,y))-Vector(p)).dot(v)/v.length_squared));c=Vector(p)+v*t
    return (Vector((x,y))-c).length,c
def path_sample(x,y):
    best=(1e6,6.0)
    for ka,kb in new_edges:
        a=A[ka];b=A[kb];d,c=closest_segment(x,y,a.xy,b.xy)
        if d<best[0]:
            t=(c-a.xy).length/(b.xy-a.xy).length;best=(d,a.z+(b.z-a.z)*t)
    return best
def forest_height(x,y):
    # Quiet uneven banks, a shallow depression behind the light clearing, then
    # rising rear woodland. None of this deforms the ocean or original beach.
    h=6.18+.018*(y-13)+.19*math.sin(x*.19+y*.22)+.12*math.sin(y*.50-x*.13)
    h+=.80*sm(17,29,y)-.48*math.exp(-((x+28)/5)**2-((y-20)/3.5)**2)
    h-=.45*(1-sm(8,11,y))
    dist,rh=path_sample(x,y);h=h*sm(1.02,2.6,dist)+rh*(1-sm(1.02,2.6,dist))
    best=min((closest_segment(x,y,p,q) for p,q in zip(join,join[1:])),key=lambda t:t[0])
    d,c=best
    if d<3.3:
        # At the seam use the existing terrain's evaluated height, preserving
        # the upper stair. The small inward overlap closes raster hairlines.
        sample=c+Vector((.008,-.008));hit=oldtree.ray_cast(Vector((sample.x,sample.y,25)),Vector((0,0,-1)))[0]
        z=hit.z if hit else height(c.x,c.y)
        h=z*(1-sm(0,3.3,d))+h*sm(0,3.3,d)
    return h
# Save the evaluated layout and outline for the raster authoring step.
(REVIEW/'forest-layout.json').write_text(json.dumps({'route':route,'outline':boundary,'new_edges':new_edges},indent=2),encoding='utf-8')
points=[(x,y,forest_height(x,y)) for x,y in boundary]
mesh=bpy.data.meshes.new('WALK_Forest_Ground');mesh.from_pydata(points,[],tri(points));mesh.update()
bm=bmesh.new();bm.from_mesh(mesh)
bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=27,use_grid_fill=True)
for v in bm.verts:v.co.z=forest_height(v.co.x,v.co.y)
bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
ob=bpy.data.objects.new('WALK_Forest_Ground',mesh);COL.objects.link(ob);mesh.materials.append(MATS['grass'])
uv=mesh.uv_layers.new(name='UVMap');mesh.uv_layers.new(name='Wind')
for p in mesh.polygons:
    p.use_smooth=True
    for li in p.loop_indices:
        co=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=((co.x+50)/54,(co.y+4)/40)
# The continuous near bank is part of the land, not isolated foreground pillars.
wall=Mesh('Forest_Continuous_Bank')
front=boundary[:6]
for i,(p,q) in enumerate(zip(front,front[1:])):
    count=max(2,int((Vector(q)-Vector(p)).length/.8))
    for j in range(count):
        a=Vector(p).lerp(Vector(q),j/count);b=Vector(p).lerp(Vector(q),(j+1)/count)
        za=forest_height(*a);zb=forest_height(*b)
        wall.part([(a.x,a.y,za),(b.x,b.y,zb),(b.x+.15,b.y+.15,zb-1.7),(a.x+.15,a.y+.15,za-1.7)],[(0,1,2,3)],'rock_b')
wall.build()
LAYOUT['forest_extension']={'collection':COL.name,'direction':'west from forest_end','new_edges':new_edges,'bounds':[-48.5,1.2,3.26,34],'scope':'continuous westward path, near bank, activity band and deep forest'}
LAYOUT['camera']['physical_offset']=[0,10.28,31.65]
LAYOUT['camera']['physical_fov']=22.5
export('west-forest-terrain')
