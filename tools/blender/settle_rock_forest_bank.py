"""MCP: conform the continuous bank to retained terrain and retire torn lower faces."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/rock-forest-style-review';s=bpy.data.scenes['Tripo_Game_Assembly_20261119'];bpy.context.window.scene=s
assert s.get('bank_settled') is None
ground=s.objects['GameJoin_WALK_Forest_Ground'];tree=BVHTree.FromPolygons([v.co for v in ground.data.vertices],[list(p.vertices) for p in ground.data.polygons])
stations=json.loads((O/'bank-refined.json').read_text())['stations'];old=s.objects['Forest_Bank_Continuous_Core'];old.name='Rejected_Bank_Low_Apron';s.collection.objects.unlink(old)
def section(x):
    for a,b in zip(stations,stations[1:]):
        if a[0]-.0001<=x<=b[0]+.0001:
            f=(x-a[0])/(b[0]-a[0]);return [a[i]*(1-f)+b[i]*f for i in range(1,4)]
    return None
verts=[];faces=[];uvs=[];nx=49;ny=37
for ci in range(nx):
    x=stations[0][0]+(stations[-1][0]-stations[0][0])*ci/(nx-1);rear,front,z=section(x)
    for ri in range(ny):
        t=ri/(ny-1);y=rear*(1-t)+front*t
        h=z*(1-t**1.25)-.13*t**1.25+math.sin(t*math.pi)*(.10*math.sin(x*1.6)+.04*math.cos(y*2.1))
        hit=tree.ray_cast(Vector((x,y,12)),Vector((0,0,-1)),20)
        if hit[0] and hit[1].z>.3:h=max(h,hit[0].z)
        verts.append((x,y,h-.012));uvs.append((ci/(nx-1),t))
for c in range(nx-1):
    for r in range(ny-1):
        a=c*ny+r;b=a+ny;faces.extend([(a,b,b+1),(a,b+1,a+1)])
me=bpy.data.meshes.new('Settled_Continuous_Forest_Bank');me.from_pydata(verts,[],faces);me.update();uv=me.uv_layers.new(name='BankPaint')
for p in me.polygons:
    p.use_smooth=True
    for li in p.loop_indices:uv.data[li].uv=uvs[me.loops[li].vertex_index]
ob=bpy.data.objects.new('Forest_Bank_Continuous_Core',me);s.collection.objects.link(ob);me.materials.append(old.data.materials[0])
# Remove only lower torn ground inside this reconstructed region. Keep the route
# and lip as the original mesh; a 12 cm overlap conceals the trimmed boundary.
bm=bmesh.new();bm.from_mesh(ground.data);remove=[]
for f in bm.faces:
    p=f.calc_center_median();sec=section(p.x)
    if sec is None:continue
    rear,front,z=sec;t=(rear-p.y)/(rear-front)
    if .07<t<.98 and all(section(v.co.x) is not None for v in f.verts):remove.append(f)
bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(ground.data);bm.free();ground.data.update()
s['bank_settled']=True
(O/'bank-settled.json').write_text(json.dumps({'removed_old_lower_faces':len(remove),'new_vertices':len(me.vertices),'new_faces':len(me.polygons),'terrain_height_sampling':'Retained top terrain sampled before local replacement; path lip retained.'},indent=2),encoding='utf8')
print('Continuous bank settled; retired lower torn ground faces:',len(remove))
