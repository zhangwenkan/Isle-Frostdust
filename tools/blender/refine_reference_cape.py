"""Targeted cape refinement after actual game view; run only via Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
import ast
from mathutils.bvhtree import BVHTree
REVIEW=ROOT/'artifacts/reference-cape-review';TEX=OUT/'reference_cape'
assert LAYOUT.get('reference_cape') and not LAYOUT['reference_cape'].get('first_refine')
COL=bpy.data.collections['49_Reference_Cape']
for key in ['cape_side','cape_top','cape_platform','cape_tread','cape_sand','cape_wood','cape_char','cape_log_end','cape_ring','cape_leaf','cape_water','cape_fire','cape_smoke']:
    candidates=[m for m in bpy.data.materials if m.name.startswith('RC_'+key)];MATS[key]=candidates[-1]
for image in bpy.data.images:
    if 'reference_cape' in bpy.path.abspath(image.filepath):image.reload();image.pack()
source=ast.parse((ROOT/'tools/blender/build_reference_cape.py').read_text(encoding='utf-8'))
for node in source.body:
    if isinstance(node,ast.FunctionDef) and node.name in ['cut_rock','curve']:
        exec(compile(ast.Module(body=[node],type_ignores=[]),'cape_factories','exec'))
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['shape','specs'] for t in node.targets):
        exec(compile(ast.Module(body=[node],type_ignores=[]),'cape_parameters','exec'))
for i,s in enumerate(specs):
    old=SCENE.objects['Cape_Cliff_Mass_%02d'%i];replacement=cut_rock(old.name+'_Refined',*s)
    old.data=replacement.data;bpy.data.objects.remove(replacement,do_unlink=True)
oldtree=BVHTree.FromPolygons([v.co for v in SCENE.objects['WALK_Forest_Ground'].data.vertices],[list(p.vertices) for p in SCENE.objects['WALK_Forest_Ground'].data.polygons])
def old_height(x,y):
    hit=oldtree.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0]
    if hit is None:hit=oldtree.find_nearest(Vector((x,y,6.28)))[0]
    return hit.z
vs=[];uv=[];fs=[];NX=48;NY=12
for j in range(NY+1):
    s=(j/NY-.5)*2
    for i in range(NX+1):
        t=i/NX;x=-60.90-8.45*t;c=13.7-1.5*t;width=5.5-2.3*sm(0,.65,t)+.65*sm(.65,1,t);y=c+s*width
        h=6.28*(1-sm(.04,1,t))+4.55*sm(.04,1,t)+.10*s*s*(1-t)
        if t<.06:h=old_height(x,y)*(1-sm(0,.06,t))+h*sm(0,.06,t)
        vs.append(Vector((x,y,h)));uv.append((t,(s+1)*.5))
for j in range(NY):
    for i in range(NX):
        k=j*(NX+1)+i;fs.extend([(k,k+1,k+NX+2),(k,k+NX+2,k+NX+1)])
def replace(name,builder,smooth=False):
    old=SCENE.objects[name];new=builder.build(smooth=smooth);old.data=new.data;bpy.data.objects.remove(new,do_unlink=True)
b=Mesh('Refined_Neck');b.part(vs,fs,'cape_top',uv);replace('WALK_Cape_Neck',b,True)
b=Mesh('Refined_Neck_Side')
for row in [0,NY]:
    for i in range(NX):
        p=vs[row*(NX+1)+i];q=vs[row*(NX+1)+i+1]
        b.part([p,q,(q.x,q.y+.05,-.45),(p.x,p.y+.05,-.45)],[(0,1,2,3)],'cape_side')
replace('Cape_Neck_Rockside',b)
BACK=[(-84,9.5),(-81,5.3),(-77,3.5),(-73,1.8),(-69,5.0),(-66,9.8)]
FRONT=[(-84,-3.0),(-81,-5.5),(-77,-7.65),(-73,-8.0),(-68.8,-5.8),(-65,-1.8)]
NX=80;NY=36;maxv=1.35;vs=[];uv=[];coord=[];fs=[];arc=[0.]
for i in range(1,NX+1):arc.append(arc[-1]+(curve(FRONT,i/NX)-curve(FRONT,(i-1)/NX)).length)
for j in range(NY+1):
    v=j/NY*maxv
    for i in range(NX+1):
        u=i/NX;a=curve(BACK,u);f=curve(FRONT,u);p=a+(f-a)*v
        z=.145-.032*sm(.2,.8,v)-.30*sm(.74,1.03,v)-.46*sm(1.03,1.35,v)
        ends=sm(0,.075,u)*(1-sm(.925,1,u));z=z*ends-.65*(1-ends)
        vs.append(Vector((p.x,p.y,z)));uv.append((u,1-v/maxv));coord.append((arc[i],1.-(v-1)*(f-a).length))
for j in range(NY):
    for i in range(NX):
        k=j*(NX+1)+i;fs.extend([(k,k+1,k+NX+2),(k,k+NX+2,k+NX+1)])
for name,points,matkey in [('WALK_Cape_Sand',vs,'cape_sand'),('Cape_Swash_Film',[Vector((p.x,p.y,max(p.z,-.18)+.010)) for p in vs],'cape_water')]:
    b=Mesh('Refined_'+name);b.part(points,fs,matkey,uv);replace(name,b,True)
    ob=SCENE.objects[name]
    for p in ob.data.polygons:
        for li in p.loop_indices:ob.data.uv_layers[1].data[li].uv=coord[ob.data.loops[li].vertex_index]
terrain=[o for o in COL.objects if o.type=='MESH' and (o.name.startswith('WALK_') or o.name.startswith('Cape_Cliff_'))]
trees=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]) for o in terrain]
plant=SCENE.objects['Cape_Shore_Grass'];me=plant.data
for polygon in me.polygons:
    ids=list(polygon.vertices);center=sum((me.vertices[i].co for i in ids[:2]),Vector())/2
    hits=[t.ray_cast(Vector((center.x,center.y,35)),Vector((0,0,-1)))[0] for t in trees];hits=[h for h in hits if h is not None]
    if hits:
        dz=max(h.z for h in hits)+.014-center.z
        for i in ids:me.vertices[i].co.z+=dz
me.update()
LAYOUT['reference_cape']['first_refine']={'broader_attached_neck':True,'sand_reaches_cliff_feet':True,'sand_ends_under_water':True,'large_unequal_top_planes':True,'plants_snapped_to_actual_surfaces':True,'texture_baked_step_stripes_removed':True}
export('reference-cape-refine')
