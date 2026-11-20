"""Rebuild individually bounded Tripo rock profiles inside Blender through MCP.

New radial control surfaces and height patches are created from measured
surface intersections, not copied face/UV data. This is a reference-dependent
replication experiment. It is not yet an approved reusable modelling skill.
"""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/tripo-replica-review';ASSET=ROOT/'assets/layered_island/tripo_replica'
NAME='Tripo_Measured_Profile_Rebuild_20261119';assert not bpy.data.scenes.get(NAME),'Inspect completed profile rebuild.'
old=bpy.context.window.scene;source=bpy.data.scenes['Tripo_Coast_Processing_20261119'].objects['Tripo_Coast_Original_Surface']
bm=bmesh.new();bm.from_mesh(source.data);tree=BVHTree.FromBMesh(bm);bm.free()
s=bpy.data.scenes.new(NAME);bpy.context.window.scene=s
col=bpy.data.collections.new('Tripo_Profile_Replica_Authored');s.collection.children.link(col)
review=bpy.data.collections.new('Tripo_Profile_Replica_Review');s.collection.children.link(review)
clay=bpy.data.materials['Replica_Neutral_Clay'];profiles=[]

def mesh(name,v,f):
    me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(clay)
    for p in me.polygons:p.use_smooth=True
    o['construction']='New measured-profile surface. No original face or UV transfer, no bevel.'
    return o

def outer_surface(center,direction,limit):
    """Trace through thin double shells to the outermost measured surface."""
    start=center.copy();travel=0;found=None
    for _ in range(32):
        hit,n,index,d=tree.ray_cast(start,direction,max(0,limit-travel))
        if hit is None:break
        travel=(hit-center).dot(direction)
        if 0<=travel<=limit:found=hit.copy()
        else:break
        start=hit+direction*.000025;travel+=.000025
        if travel>=limit:break
    return found

def rock(label,low,high,center):
    lo=Vector(low);hi=Vector(high);c=Vector(center);radius=(hi-lo)*.5
    nt=96;np=48;v=[];observed=[];hit_count=0
    # The control scaffold is separate for each measured rock. Sampling the
    # actual surface creates unequal corners/facets rather than bevel rings.
    for j in range(np+1):
        phi=math.pi*j/np
        count=1 if j in (0,np) else nt
        for i in range(count):
            a=2*math.pi*i/nt
            delta=Vector((radius.x*math.sin(phi)*math.cos(a),radius.y*math.sin(phi)*math.sin(a),radius.z*math.cos(phi)))
            direction=delta.normalized()
            limits=[((hi[k] if direction[k]>0 else lo[k])-c[k])/direction[k] for k in range(3) if abs(direction[k])>1e-8]
            limit=min(x for x in limits if x>0)*.9998
            hit=outer_surface(c,direction,limit)
            # Only occluded internal faces use the bounded support scaffold.
            # No guessed external fractures or noise displacement is added.
            if hit is None:p=c+direction*min(delta.length,limit);observed.append(False)
            else:p=hit;observed.append(True);hit_count+=1
            v.append(tuple(p))
    f=[];top=0;bottom=len(v)-1
    for i in range(nt):f.append((top,1+i,1+(i+1)%nt))
    for j in range(np-2):
        a=1+j*nt;b=a+nt
        for i in range(nt):f.append((a+i,b+i,b+(i+1)%nt,a+(i+1)%nt))
    last=1+(np-2)*nt
    for i in range(nt):f.append((last+i,bottom,last+(i+1)%nt))
    o=mesh('Replica_Profile_'+label,v,f)
    # Keep profile source data separately for continued editing, without a
    # run-time reference to the downloaded Tripo asset.
    o['profile_theta_samples']=nt;o['profile_polar_samples']=np
    profiles.append({'name':o.name,'bounds':[low,high],'center':center,'theta':nt,'polar':np,
     'measured_vertices':hit_count,'support_vertices':len(v)-hit_count,'vertices':v,'observed':observed})
    return o

# Bounds/centres are measured from the three orthographic reference views.
# They define the original placements, never a new random composition.
specs=[
 ('Front_Left_Main',(-.315,-.315,.12),(-.075,-.105,.355),(-.205,-.22,.235)),
 ('Front_Right_Main',(.035,-.295,.115),(.305,-.095,.35),(.17,-.205,.23)),
 ('Left_Sea_Shoulder',(-.405,-.215,.075),(-.235,.09,.365),(-.32,-.045,.225)),
 ('Left_Back_Shoulder',(-.415,.075,.07),(-.215,.295,.385),(-.32,.175,.235)),
 ('Back_Left_Block',(-.24,.27,.055),(.055,.46,.39),(-.115,.355,.245)),
 ('Back_Right_Block',(.035,.255,.065),(.285,.46,.395),(.155,.355,.245)),
 ('Right_Tall_Block',(.205,.045,.055),(.495,.315,.49),(.355,.17,.29)),
 ('Right_Middle_Shoulder',(.255,-.13,.065),(.445,.09,.365),(.35,-.025,.225)),
 ('Left_Foot',(-.425,-.365,.01),(-.23,-.185,.205),(-.33,-.285,.11)),
 ('Left_Inset_Foot',(-.275,-.435,.015),(-.085,-.255,.195),(-.175,-.345,.10)),
 ('Right_Foot',(.025,-.395,.005),(.235,-.205,.205),(.135,-.30,.105)),
 ('Right_Outer_Foot',(.17,-.36,.005),(.39,-.14,.23),(.275,-.255,.12)),
 ('Left_Sea_Toe',(-.505,-.20,.001),(-.34,.145,.185),(-.425,-.065,.09)),
 ('Left_Back_Toe',(-.475,.15,.005),(-.28,.395,.235),(-.375,.275,.13)),
 ('Right_Return',(.26,-.225,.005),(.485,.10,.275),(.375,-.065,.15)),
]
rocks=[rock(*sp) for sp in specs]

def top_height(x,y,fallback):
    hit,n,index,d=tree.ray_cast(Vector((x,y,.37)),Vector((0,0,-1)),.38)
    return hit.z if hit is not None else fallback

def height_patch(name,x0,x1,y0,y1,nx,ny,ellipse=False):
    v=[];f=[];ids={}
    for j in range(ny+1):
        y=y0+(y1-y0)*j/ny
        for i in range(nx+1):
            x=x0+(x1-x0)*i/nx
            if ellipse and ((x+.012)/.236)**2+((y-.034)/.267)**2>1:continue
            fallback=.315 if ellipse else .06+.24*(y-y0)/(y1-y0)
            z=top_height(x,y,fallback)
            # The static flame is outside this rock-only reconstruction.
            if ellipse and x*x+(y-.01)**2<.055**2:z=.315
            ids[(i,j)]=len(v);v.append((x,y,z))
    for j in range(ny):
        for i in range(nx):
            keys=[(i,j),(i+1,j),(i+1,j+1),(i,j+1)]
            if all(k in ids for k in keys):f.append(tuple(ids[k] for k in keys))
    o=mesh(name,v,f)
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    sol=o.modifiers.new('Support behind measured surface','SOLIDIFY');sol.thickness=.035;sol.offset=-1;sol.use_even_offset=False
    bpy.ops.object.modifier_apply(modifier=sol.name);o.select_set(False)
    return o

platform=height_patch('Replica_Measured_Camp_Rock',-.245,.23,-.24,.30,96,112,True)
stairs=height_patch('Replica_Measured_Front_Stairs',-.105,.092,-.43,-.155,64,128)
backstairs=height_patch('Replica_Measured_Back_Stairs',-.072,.125,.235,.405,48,64)
# Match the reference neutral camera/light setup exactly.
base=bpy.data.scenes['Tripo_Reference_Reconstruction_20261119']
for o in base.objects:
    if o.type in {'CAMERA','LIGHT'} or (o.type=='MESH' and o.name.startswith('DiagnosticFloor')):
        cp=o.copy();cp.data=o.data.copy();review.objects.link(cp)
        if cp.type=='CAMERA':s.camera=cp
s.world=base.world.copy();s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=960;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
cam=s.camera;cam.data.ortho_scale=1.43;target=Vector((0,0,.21))
for angle in [0,35]:
    a=math.radians(angle);cam.location=target+Vector((math.sin(a)*2.4,-math.cos(a)*2.4,1.05));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.filepath=str(OUT/('profile-replica-gray-'+str(angle)+'.png'));bpy.ops.render.render(write_still=True)
s['revision']='measured-profile-replica-1'
bpy.data.libraries.write(str(ASSET/'tripo_measured_profile_replica.blend'),{s},fake_user=True,compress=True)
(ASSET/'measured-rock-profiles.json').write_text(json.dumps(profiles,separators=(',',':')),encoding='utf8')
report={'scene':s.name,'revision':s['revision'],'method':'New per-rock control surfaces traced to measured Tripo outer intersections, plus new height patches.',
 'original_face_or_uv_data_copied':False,'original_texture_copied':False,'rocks':len(rocks),'objects':len(col.objects),
 'reference_dependence':'This replica measures the supplied Tripo surfaces. Future independent modelling workflow remains unproven and will be developed only after user acceptance.',
 'source':'tools/blender/rebuild_tripo_measured_profiles.py','status':'Actual reconstruction experiment, pending visual comparison; not user acceptance or a final workflow.'}
(OUT/'profile-reconstruction-state.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
bpy.context.window.scene=old;print(json.dumps(report,ensure_ascii=False))
