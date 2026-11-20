"""Fit the cape to the actual forest slope; author only through Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
import ast
from mathutils.bvhtree import BVHTree
COL=bpy.data.collections['49_Reference_Cape']
assert not LAYOUT['reference_cape'].get('continuous_cliff_join'),'Already completed: inspect current source before editing.'
for key in ['cape_side','cape_top','cape_platform','cape_tread']:
    MATS[key]=[m for m in bpy.data.materials if m.name.startswith('RC_'+key)][-1]
source=ast.parse((ROOT/'tools/blender/build_reference_cape.py').read_text(encoding='utf-8'))
for node in source.body:
    if isinstance(node,ast.FunctionDef) and node.name=='cut_rock':exec(compile(ast.Module(body=[node],type_ignores=[]),'cape_rock_factory','exec'))
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['shape','outline'] for t in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'cape_source_outline','exec'))
archive=bpy.data.collections.new('90_Reference_Cape_Column_Cliffs');SCENE.collection.children.link(archive)
def retain_old(ob):
    for c in list(ob.users_collection):c.objects.unlink(ob)
    archive.objects.link(ob);ob.hide_set(True);ob.hide_render=True
def replace_mesh(name,builder,smooth=False):
    old=SCENE.objects[name];new=builder.build(smooth)
    # Preserve a recoverable object and its original mesh, not just the .blend backup.
    saved=old.copy();saved.data=old.data.copy();saved.name=name+'_Before_Continuous';archive.objects.link(saved);saved.hide_set(True);saved.hide_render=True
    old.data=new.data;bpy.data.objects.remove(new,do_unlink=True)
    return old
def tree(ob):return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons])
near=SCENE.objects['WALK_Forest_NearSlope'];neck=tree(SCENE.objects['WALK_Cape_Neck'])
seam=sorted([v.co.copy() for v in near.data.vertices if abs(v.co.x+63.04)<.002],key=lambda p:p.y)
assert len(seam)==15,len(seam)
def interp(points,y):
    for a,b in zip(points,points[1:]):
        if a.y<=y<=b.y:return a.z+(b.z-a.z)*(y-a.y)/(b.y-a.y)
    return points[0].z if y<points[0].y else points[-1].z
neck_me=SCENE.objects['WALK_Cape_Neck'].data
counts={}
for p in neck_me.polygons:
    for a,b in zip(p.vertices,list(p.vertices)[1:]+list(p.vertices)[:1]):
        k=tuple(sorted((a,b)));counts[k]=counts.get(k,0)+1
front_ids={i for e,c in counts.items() if c==1 for i in e if neck_me.vertices[i].co.y<11}
neck_front=sorted([neck_me.vertices[i].co.copy() for i in front_ids],key=lambda p:p.x)
def neck_edge(x):
    for a,b in zip(neck_front,neck_front[1:]):
        if a.x<=x<=b.x:
            t=(x-a.x)/(b.x-a.x);return a.lerp(b,t)
    return neck_front[0] if x<neck_front[0].x else neck_front[-1]
# A fitted wedge continues all the way across the real western boundary of
# the old near slope. The back meets the neck; the near edge curls into the bay.
vs=[];uv=[];fs=[];NX=40;NY=56
for j in range(NY+1):
    s=j/NY
    for i in range(NX+1):
        t=i/NX;blend=sm(0,1,t)
        x=-63.04-6.45*t+.48*math.sin(math.pi*s)*math.sin(math.pi*t)
        back=neck_edge(x);front_y=-2.92+6.6*blend
        y=front_y+(back.y+.025-front_y)*s
        start_y=-2.92+(neck_edge(-63.04).y+.025+2.92)*s
        if start_y<=seam[-1].y:old_z=interp(seam,start_y)
        else:
            old_z=seam[-1].z+(neck_edge(-63.04).z-seam[-1].z)*sm(seam[-1].y,neck_edge(-63.04).y,start_y)
        end_z=1.10+(4.52-1.10)*sm(0,.93,s)
        z=old_z*(1-blend)+end_z*blend
        z+=(.09*math.sin(s*7.0+t*3.0))*math.sin(math.pi*t)*(1-s)
        # This upper edge is on the existing neck, with a very small overlap.
        upper=sm(.82,1,s)*sm(0,.12,t)
        z=z*(1-upper)+back.z*upper
        vs.append(Vector((x,y,z)));uv.append((x*.16,y*.16))
for j in range(NY):
    for i in range(NX):
        k=j*(NX+1)+i;fs.extend([(k,k+1,k+NX+2),(k,k+NX+2,k+NX+1)])
b=Mesh('Cape_Connection_Shoulder_Continuous');b.part(vs,fs,'cape_top',uv)
replace_mesh('Cape_Connection_Shoulder',b,True)
# Close the visible near edge and western flank to below sea level. The east
# edge touches the retained old skirt exactly; there is no hanging surface.
rim=[vs[i] for i in range(NX+1)]+[vs[j*(NX+1)+NX] for j in range(1,NY+1)]
wall=Mesh('Cape_Connection_Closed_Skirt')
for a,b in zip(rim,rim[1:]):
    d=(b-a);out=Vector((d.y,-d.x,0)).normalized()*.23
    ma=Vector((a.x,a.y,min(2.1,a.z*.45)))+out
    mb=Vector((b.x,b.y,min(2.1,b.z*.45)))+out
    wall.part([a,b,mb,ma],[(0,1,2,3)],'cape_side')
    wall.part([ma,mb,(mb.x,mb.y,-1.4),(ma.x,ma.y,-1.4)],[(0,1,2,3)],'cape_side')
wall.build()
# The shelf's continuous irregular core carries the main silhouette. The
# stair notch remains open, and the rock toe leans outward with unequal folds.
platform=tree(SCENE.objects['WALK_Cape_Platform']);center=Vector((-75.3,11.3,0));top=[];mid=[];bottom=[]
for i,(x,y) in enumerate(outline):
    hit=platform.ray_cast(Vector((x,y,20)),Vector((0,0,-1)))[0]
    if hit is None:hit=platform.find_nearest(Vector((x,y,4.55)))[0]
    p=Vector((x,y,hit.z-.027));direction=Vector((x-center.x,y-center.y,0)).normalized()
    # Keep both sides of the stair notch clear. Other folds spread to the toe.
    notch=i in [2,3,4,5]
    expand=0.0 if notch else [.32,.64,.24,.48,.34][i%5]
    top.append(p)
    mid.append(Vector((x,y,1.75+.28*math.sin(i*1.6)))+direction*expand)
    bottom.append(Vector((x,y,-.70))+direction*(expand+.10 if not notch else 0))
b=Mesh('Cape_Continuous_Cliff_Core')
for i in range(len(top)):
    k=(i+1)%len(top)
    b.part([top[i],top[k],mid[k],mid[i]],[(0,1,2,3)],'cape_side')
    b.part([mid[i],mid[k],bottom[k],bottom[i]],[(0,1,2,3)],'cape_side')
b.part(bottom,[tuple(reversed(t)) for t in tri(bottom)],'cape_side')
replace_mesh('Cape_Attached_Cliff_Core',b)
for name in LAYOUT['reference_cape']['cliff_masses']:retain_old(SCENE.objects[name])
major=[(-81.95,10.3,3.45,6.15,-.50,4.85,.15),(-78.7,6.55,5.50,3.3,-.50,4.63,-.16),(-70.55,7.05,4.15,4.5,-.45,4.70,.21),(-70.0,15.12,4.20,3.25,-.40,6.10,-.21)]
names=[]
for i,s in enumerate(major):
    ob=cut_rock('Cape_Cliff_Plane_%02d'%i,*s,lean=(.45,-.30),top_scale=.98);names.append(ob.name)
toe=[(-81.25,5.55,3.50,2.65,-.40,1.70,.18),(-78.9,4.6,3.30,2.55,-.40,2.15,-.24),(-70.3,3.75,3.05,3.15,-.40,1.90,.17),(-68.35,6.05,2.8,3.0,-.40,2.70,.22)]
for i,s in enumerate(toe):
    ob=SCENE.objects['Cape_Cliff_Toe_%02d'%i];new=cut_rock(ob.name+'_Joined',*s,lean=(.35,-.20),top_scale=.88)
    saved=ob.copy();saved.data=ob.data.copy();saved.name=ob.name+'_Before_Continuous';archive.objects.link(saved);saved.hide_set(True);saved.hide_render=True
    ob.data=new.data;bpy.data.objects.remove(new,do_unlink=True)
for im in bpy.data.images:
    if 'reference_cape' in bpy.path.abspath(im.filepath):im.reload();im.pack()
LAYOUT['reference_cape']['cliff_masses']=names
LAYOUT['reference_cape']['continuous_cliff_join']={'old_near_slope_seam_vertices':len(seam),'old_near_slope_unchanged':True,'new_shoulder_closed_to_sea':True,'continuous_shelf_core':True,'major_attached_rock_planes':4,'original_column_cliffs_archived':archive.name}
export('reference-cape-continuous-join')
