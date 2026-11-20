"""Close the sand/cliff footprint gap and settle attached grass via Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
import ast
from mathutils.bvhtree import BVHTree
COL=bpy.data.collections['49_Reference_Cape']
assert not LAYOUT['reference_cape'].get('sand_foot_join')
for key in ['cape_sand','cape_water']:
    MATS[key]=[m for m in bpy.data.materials if m.name.startswith('RC_'+key)][-1]
source=ast.parse((ROOT/'tools/blender/build_reference_cape.py').read_text(encoding='utf-8'))
for node in source.body:
    if isinstance(node,ast.FunctionDef) and node.name=='curve':exec(compile(ast.Module(body=[node],type_ignores=[]),'cape_shore_curve','exec'))
BACK=[(-84,10.0),(-81,8.0),(-77,7.0),(-73,6.5),(-69,9.0),(-66,10.5)]
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
archive=bpy.data.collections.new('90_Reference_Cape_Before_Sand_Foot');SCENE.collection.children.link(archive)
for name,points,key in [('WALK_Cape_Sand',vs,'cape_sand'),('Cape_Swash_Film',[Vector((p.x,p.y,max(p.z,-.18)+.010)) for p in vs],'cape_water')]:
    old=SCENE.objects[name];saved=old.copy();saved.data=old.data.copy();saved.name=name+'_Before_Foot_Join';archive.objects.link(saved);saved.hide_set(True);saved.hide_render=True
    b=Mesh(name+'_Foot_Fit');b.part(points,fs,key,uv);new=b.build(True);old.data=new.data;bpy.data.objects.remove(new,do_unlink=True)
    for p in old.data.polygons:
        for li in p.loop_indices:old.data.uv_layers[1].data[li].uv=coord[old.data.loops[li].vertex_index]
floors=[o for o in COL.objects if o.type=='MESH' and (o.name.startswith(('WALK_','Cape_Cliff_')) or o.name in ['Cape_Attached_Cliff_Core','Cape_Connection_Shoulder'])]
trees=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]) for o in floors]
me=SCENE.objects['Cape_Shore_Grass'].data;snapped=0;unmatched=[]
for p in me.polygons:
    ids=list(p.vertices);root=(me.vertices[ids[0]].co+me.vertices[ids[1]].co)/2
    hits=[t.ray_cast(Vector((root.x,root.y,30)),Vector((0,0,-1)))[0] for t in trees];hits=[h for h in hits if h is not None]
    if hits:delta=Vector((0,0,max(h.z for h in hits)+.014-root.z))
    else:
        near=[t.find_nearest(root)[0] for t in trees];near=[h for h in near if h is not None and (h.xy-root.xy).length<.70]
        if not near:unmatched.append(p.index);continue
        h=min(near,key=lambda h:(h-root).length);delta=h-root+Vector((0,0,.014))
    for i in ids:me.vertices[i].co+=delta
    snapped+=1
me.update();assert not unmatched,unmatched
LAYOUT['reference_cape']['sand_foot_join']={'sand_back_extends_under_actual_cliff':True,'shoreline_unchanged':True,'grass_blades_resnapped':snapped,'unmatched':unmatched}
export('reference-cape-sand-foot-fit')
