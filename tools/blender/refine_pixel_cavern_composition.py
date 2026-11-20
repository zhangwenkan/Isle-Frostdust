"""Refine new sample from its first actual render, through Blender MCP."""
import bpy
from pathlib import Path
exec((Path('D:/自己做着玩的/孤屿霜尘/tools/blender/pixel_cavern_lib.py')).read_text(encoding='utf-8'),globals())
scene=bpy.data.scenes[SCENE];bpy.context.window.scene=scene
assert scene['revision']=='pixel-cavern-complete-3'
P=palette();bamboo=collection('07_Bamboo');green=collection('08_Undergrowth');sea=collection('06_Shore');rockcol=collection('02_Cliffs')

for ob in scene.objects:
    if ob.type!='MESH':continue
    if ob.name.startswith('Mountain_'):
        for v in ob.data.vertices:v.co.z*=.72 if 'Far' in ob.name or 'Mid' in ob.name else .80
    if ob.name.startswith('Bamboo_Leaves'):
        # Broaden lance leaves at the projected pixel scale; keep existing stems.
        for p in ob.data.polygons:
            ids=list(p.vertices)
            if len(ids)!=4:continue
            root=ob.data.vertices[ids[0]].co.copy();tip=ob.data.vertices[ids[2]].co.copy();axis=(tip-root).normalized()
            for i in [1,3]:
                v=ob.data.vertices[ids[i]];along=root+axis*(v.co-root).dot(axis);perp=v.co-along
                v.co=along+perp*1.8
        normals=[]
        for l in ob.data.loops:normals.append((-.08,-.32,.94))
        ob.data.normals_split_custom_set(normals)

# Stronger middle sprays give the forest layered silhouette and cover branches.
for i,ob in enumerate([o for o in scene.objects if o.name.startswith('Bamboo_Stem')]):
    points=[v.co for v in ob.data.vertices];bottom=min(q.z for q in points);top=max(q.z for q in points)
    c=sum(points,Vector())/len(points)
    for j,t in enumerate([.40,.55,.70,.84]):
        q=Vector((c.x,c.y,bottom+(top-bottom)*t));a=-1.9+j*2.35+i*.78
        leaf_group('Bamboo_Spray_%02d_%d'%(i,j),q,a,2.45 if j<3 else 1.95,bamboo,[P['leaf'],P['leaf_lit']],i*19+j+6000,fullness=18)

# Move cave opening slightly toward its landing; all inside geometry follows.
for ob in list(scene.objects):
    if ob.type!='MESH':continue
    if ob.name.startswith(('Rock_Cave_','Root_Cavern_','Root_Ridge_','CaveInterior_','Step_Cave','Rock_Cave_Buried','Plant_Moss_Rock_Cave')):
        for v in ob.data.vertices:v.co.y-=.85
    if ob.name.startswith(('Root_Vine_','Plant_Vine_Leaves_')):
        ix=int(ob.name.rsplit('_',1)[1])
        if ix<10:
            for v in ob.data.vertices:v.co.y-=.85

# Sand coastline gets intermediate points and a gently submerged slope. The
# earlier broad submerged slab made the sea read as a visible rectangular tile.
old=scene.objects.get('Rock_Submerged_Shelf')
if old:
    archive=bpy.data.collections.new('PCC_Archive_Visible_Seabed')
    for c in list(old.users_collection):c.objects.unlink(old)
    archive.objects.link(old);old['pixel_cavern']=False
for name in ['Sand_Cove','Sand_Wet_Edge']:
    ob=scene.objects[name];bm=bmesh.new();bm.from_mesh(ob.data)
    # Subdivide boundary geometry and smooth horizontally without smoothing height.
    bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=2,use_grid_fill=True)
    original_z={v:v.co.z for v in bm.verts}
    for iteration in range(3):bmesh.ops.smooth_vert(bm,verts=list(bm.verts),factor=.45,use_axis_x=True,use_axis_y=True,use_axis_z=False)
    bm.to_mesh(ob.data);bm.free()

# Thin substrate extending down under water, with no exposed box edge.
shoreline=[(-18,-9),(-16,-12),(-11,-13.1),(-7,-12.1),(-4,-10.2),(-3.8,-7.8)]
vs=[]
for i,(x,y) in enumerate(shoreline):
    vs.extend([(x,y,.03),(x*1.08-1.0,y*1.08-.5,-.45),(x*1.17-1.2,y*1.17-1.3,-1.8)])
fs=[]
for i in range(len(shoreline)-1):
    for j in range(2):fs.append((i*3+j,(i+1)*3+j,(i+1)*3+j+1,i*3+j+1))
mesh('Sand_Submerged_Slope',vs,fs,sea,[P['sand_wet']])

# Quiet grounded rock flecks and a few structural lines at hero-scale, not
# a noise texture across every surface.
def cleft(ob,name,points,width=.024):
    vs=[]
    for x,z in points:
        for dz in [-width*.5,width*.5]:
            hit,q,n,k=ob.ray_cast(Vector((x,-25,z+dz)),Vector((0,1,0)))
            if not hit:return
            vs.append(tuple(q+n*.008))
    mesh(name,vs,[(i*2,i*2+2,i*2+3,i*2+1) for i in range(len(points)-1)],rockcol,[P['stone_shadow']])
for name,pts in [
 ('Rock_Cliff_LFront',[(-12,2.1),(-11.6,2.15),(-11.15,2.03)]),
 ('Rock_Cliff_LBridgeShoulder',[(-4.75,2.28),(-4.4,2.36),(-3.95,2.30)]),
 ('Rock_Cave_LeftJamb',[(7.95,7.1),(8.28,7.25),(8.63,7.20)]),
 ('Rock_Cave_RightJamb',[(13.45,6.5),(13.7,6.52),(14.05,6.45)])]:
    cleft(scene.objects[name],'Stone_Cleft_'+name,pts)

scene['revision']='pixel-cavern-composition-4';export_scene(scene['revision'])
