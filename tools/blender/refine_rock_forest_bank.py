"""Replace failed boundary curtains with one sloping continuous terrain apron."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/rock-forest-style-review'
s=bpy.data.scenes['Tripo_Game_Assembly_20261119'];bpy.context.window.scene=s
old=s.objects['Forest_Bank_Continuous_Core'];old.name='Rejected_Bank_Boundary_Curtains';s.collection.objects.unlink(old)
ground=s.objects['GameJoin_WALK_Forest_Ground'];tree=BVHTree.FromPolygons([ground.matrix_world@v.co for v in ground.data.vertices],[list(p.vertices) for p in ground.data.polygons])
# Longitudinal, uneven contour follows the actual near slope and beach boundary.
controls=[(-60.7,14.6,7.35,4.0),(-59.9,13.15,6.90,4.0),(-59.1,11.7,6.35,4.0),(-58.25,10.6,5.55,4.0),(-57.35,9.7,4.5,4.0),(-56.35,9.1,3.35,4.0),(-55.2,8.7,2.15,4.0),(-54.0,8.3,.9,4.0),(-53.45,8.2,.45,4.0)]
stations=[]
for x,y,foot,z in controls:
    hit=tree.ray_cast(Vector((x,y,12)),Vector((0,0,-1)),20)
    if hit[0]:z=hit[0].z
    stations.append((x,y,foot,z))
verts=[];faces=[];uvs=[];rows=[0,.18,.44,.69,.88,1]
for ci,(x,y,foot,z) in enumerate(stations):
    for ri,t in enumerate(rows):
        yp=y*(1-t)+foot*t
        # Gentle turf lip, broader exposed soil slope, toe embedded in the sand.
        h=z*(1-t**1.25)+(-.12)*t**1.25
        h+=math.sin(t*math.pi)*(.13*math.sin(ci*1.42)+.065*math.cos(ci*2.5+t*6))
        verts.append((x,yp,h-.018));uvs.append(((x+60.7)/7.25,t))
for c in range(len(stations)-1):
    for r in range(len(rows)-1):
        a=c*len(rows)+r;b=a+len(rows)
        faces.extend([(a,b,b+1),(a,b+1,a+1)] if (c+r)%2 else [(a,b,a+1),(b,b+1,a+1)])
# Foot and end closures sink below the waterline, outside the view of the surface.
for c in range(len(stations)-1):
    a=c*len(rows)+len(rows)-1;b=a+len(rows);ia=len(verts);verts.extend([(verts[a][0],verts[a][1],-.85),(verts[b][0],verts[b][1],-.85)]);uvs.extend([uvs[a],uvs[b]]);faces.append((b,a,ia,ia+1))
for c in [0,len(stations)-1]:
    for r in range(len(rows)-1):
        a=c*len(rows)+r;b=a+1;ia=len(verts);verts.extend([(verts[a][0],verts[a][1],-.85),(verts[b][0],verts[b][1],-.85)]);uvs.extend([uvs[a],uvs[b]]);faces.append((a,b,ia+1,ia))
me=bpy.data.meshes.new('Continuous_Sloping_Forest_Bank');me.from_pydata(verts,[],faces);me.update()
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
uv=me.uv_layers.new(name='BankPaint')
for p in me.polygons:
    p.use_smooth=True
    for li in p.loop_indices:uv.data[li].uv=uvs[me.loops[li].vertex_index]
ob=bpy.data.objects.new('Forest_Bank_Continuous_Core',me);s.collection.objects.link(ob);me.materials.append(old.data.materials[0]);ob['description']='One sloping forest bank with an irregular turf lip and buried beach toe.'
report={'stations':stations,'vertices':len(me.vertices),'faces':len(me.polygons),'replaced':'Failed boundary-curtain support, retained outside export scene','existing_ground_and_rocks':'unchanged'}
(O/'bank-refined.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
