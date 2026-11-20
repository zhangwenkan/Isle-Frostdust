"""Finish a reviewable reference-dependent replica sample via Blender MCP.
The final staircase is newly authored from height/axis landmarks. Rock surfaces
retain the measured reconstruction; that dependence is explicitly recorded.
"""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/tripo-replica-review';A=R/'assets/layered_island/tripo_replica'
s=bpy.data.scenes['Tripo_Surface_Measurement_Rebuild_20261119'];old=bpy.context.window.scene;bpy.context.window.scene=s
assert s['revision']=='new-control-measured-detail-2','Inspect completed static sample before retrying.'
master=s.objects['Replica_Surface_Control'];dg=bpy.context.evaluated_depsgraph_get()
me=bpy.data.meshes.new_from_object(master.evaluated_get(dg),depsgraph=dg)
o=bpy.data.objects.new('Replica_Measured_Rock_Surfaces',me)
col=bpy.data.collections['Replica_New_Surface_Topology'];col.objects.link(o)
archive=bpy.data.collections.new('90_Measured_Multires_Control_Not_Exported');s.collection.children.link(archive)
for c in list(master.users_collection):c.objects.unlink(master)
archive.objects.link(master);master.hide_render=True;master.hide_set(True)
# Preserve the measured control/detail source, while reviewing a cleaned surface.
ys=[-.449,-.428,-.407,-.384,-.364,-.347,-.329,-.311,-.293,-.275,-.256,-.237,-.219,-.200,-.184]
zs=[.0806,.0978,.1124,.1352,.1475,.1635,.1828,.1989,.2225,.2487,.2765,.3042,.325,.343]
def xc(y):return -.070+(y+.449)*.287
def tread_height(y):
    i=next((k for k in range(len(zs)) if ys[k]<=y<ys[k+1]),len(zs)-1)
    return zs[max(0,i)]
bm=bmesh.new();bm.from_mesh(me)
remove=[]
for f in bm.faces:
    p=f.calc_center_median()
    # The stair axis is diagonal in plan; a world-X rectangular cut would
    # erase the flanking rocks, so use the actual widening stair corridor.
    width=.073+.010*max(0,min(1,(p.y+.449)/.265))
    if -.451<p.y<-.185 and abs(p.x-xc(p.y))<width and p.z<tread_height(p.y)+.013:
        remove.append(f)
bmesh.ops.delete(bm,geom=remove,context='FACES')
bmesh.ops.dissolve_degenerate(bm,dist=.0000005,edges=list(bm.edges));bm.to_mesh(me);bm.free();me.update()
vs=[];fs=[];ncols=12
# Continuous tread/riser surface with varying measured heights, not separated bars.
rows=[]
for j in range(len(zs)):
    z=zs[j]
    for y in [ys[j],ys[j+1]]:
        row=[];width=.073+.010*max(0,min(1,(y+.449)/.265))
        for i in range(ncols+1):
            u=-1+2*i/ncols;x=xc(y)+width*u
            # Cross slope follows the scanned noses; endpoint losses are
            # local corner chips and do not form a perimeter bevel band.
            yy=y-u*.0035
            zz=z+.0012*u+.001*(y-ys[j])/(ys[j+1]-ys[j])
            if i in (0,ncols) and j in (2,7,11):zz-=.0018
            row.append(len(vs));vs.append((x,yy,zz))
        rows.append(row)
for r in range(len(rows)-1):
    for i in range(ncols):fs.append((rows[r][i],rows[r][i+1],rows[r+1][i+1],rows[r+1][i]))
# Sloped side support and bottom are separate from the nose/riser geometry.
left=[];right=[]
for r,row in enumerate(rows):
    for ids,idx in [(left,row[0]),(right,row[-1])]:
        x,y,z=vs[idx];ids.append(len(vs));vs.append((x,y,.065))
for r in range(len(rows)-1):
    fs.append((rows[r][0],rows[r+1][0],left[r+1],left[r]))
    fs.append((rows[r][-1],right[r],right[r+1],rows[r+1][-1]))
fs.append(tuple(left+list(reversed(right))))
fs.append(tuple(rows[0]+[right[0],left[0]]));fs.append(tuple(list(reversed(rows[-1]))+[left[-1],right[-1]]))
stme=bpy.data.meshes.new('Authored_Staircase_Landmarks');stme.from_pydata(vs,[],fs);stme.update()
bm=bmesh.new();bm.from_mesh(stme);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(stme);bm.free()
st=bpy.data.objects.new('Replica_Authored_Diagonal_Staircase',stme);col.objects.link(st)
stme.materials.append(bpy.data.materials['Replica_Neutral_Clay'])
st['method']='New continuous step mesh from measured tread levels and diagonal plan axis. No reference topology/UV/texture.'
st['tread_heights']=zs
for p in stme.polygons:p.use_smooth=False
s['revision']='static-measured-replica-with-authored-stairs-3'
cam=s.camera;target=Vector((0,0,.21));s.cycles.samples=32
for angle in [0,35]:
    a=math.radians(angle);cam.location=target+Vector((math.sin(a)*2.4,-math.cos(a)*2.4,1.05));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.filepath=str(O/('review-replica-gray-%s.png'%angle));bpy.ops.render.render(write_still=True)
# Extra view checks the original back deficiency, without pretending to fix it.
a=math.radians(155);cam.location=target+Vector((math.sin(a)*2.4,-math.cos(a)*2.4,1.05));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(O/'review-replica-back-gray.png');bpy.ops.render.render(write_still=True)
cam.location=target+Vector((math.sin(math.radians(35))*2.4,-math.cos(math.radians(35))*2.4,1.05));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.data.libraries.write(str(A/'tripo_replica_review.blend'),{s},fake_user=True,compress=True)
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);st.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.gltf(filepath=str(A/'tripo_replica_review.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
report={'scene':s.name,'revision':s['revision'],'review_meshes':[o.name,st.name],'rock_vertices':len(me.vertices),'rock_faces':len(me.polygons),
 'stairs':len(zs),'removed_stair_faces':len(remove),'source_blend':'assets/layered_island/tripo_replica/tripo_replica_review.blend',
 'glb':'assets/layered_island/tripo_replica/tripo_replica_review.glb',
 'rock_method':'New surface topology reconstructed from supplied Tripo geometry, with reference-fitted multires detail. Reference dependent.',
 'stair_method':st['method'],'original_texture_uv_or_face_topology_exported':False,
 'limits':['Independent geological sculpting has not been demonstrated.','Reference static camp props and side/back deficiencies remain in the measured surface.','Neutral material only; Tripo texture appearance has not been replicated.','Not integrated into the game; no passage or motion tests; workflow awaits user acceptance.'],
 'status':'Static sample for evaluation; no user acceptance implied.'}
(O/'review-state.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
bpy.context.window.scene=old;print(json.dumps(report,ensure_ascii=False))
