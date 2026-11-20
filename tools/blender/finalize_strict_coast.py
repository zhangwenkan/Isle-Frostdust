"""Continuous near ledges, attached foreground foliage, root repair and final UV."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/strict_coast_common.py',encoding='utf8').read(),'strict_coast_common.py','exec'))
assert not state.get('near_ledge_done')
ft=ground_tree();rt=[tree(SCENE.objects[n]) for n in state['rocks']]
def support(x,y):return max([h for h in [sample(t,x,y) for t in [ft]+rt] if h is not None],default=None)
# Clear roof flattening/root discrepancy before recording final contact.
for row in state['plants']:
    old=Vector(row['root']);new=old.copy();new.z=support(old.x,old.y)+.012;delta=new-old;row['root']=list(new);num=row['name'].rsplit('_',1)[1]
    for kind in ['Bamboo','Leaves']:
        o=SCENE.objects['Forest_Strict_'+kind+'_'+num]
        for v in o.data.vertices:v.co+=delta
        o.data.update();LAYOUT['forest_extension']['layer_roles']['wind_bindings'][o.name]['root']=[new.x,new.z,-new.y]
# Repair each grass/rosette base on the actual revised substrate, not its grid.
for name in ['Forest_Strict_Grass','Forest_Strict_Understory']:
    o=SCENE.objects[name]
    for start in range(0,len(o.data.vertices),15):
        verts=[o.data.vertices[start+j] for j in range(15)];base=(verts[0].co+verts[2].co)*.5;h=support(base.x,base.y)
        if h is None:continue
        delta=h+.008-base.z
        for v in verts:v.co.z+=delta
    o.data.update()
# Two attached lower ledges follow the near-bank break. Staggered masonry is
# subordinate to the geological base, with continuous top soil and moss.
path=[(-61.0,6.8),(-59.7,6.3),(-58.2,5.3),(-56.8,3.9),(-55.1,2.4),(-54.0,.6)]
terrace=Mesh('Cape_Strict_Near_Ledges');moss=Mesh('Cape_Strict_Near_Ledge_Moss')
for i,((x,y),(xx,yy)) in enumerate(zip(path,path[1:])):
    a=Vector((x,y,height_at(ft,x,y)));b=Vector((xx,yy,height_at(ft,xx,yy)));direction=b-a;direction.z=0;n=Vector((direction.y,-direction.x,0)).normalized();segments=3
    for j in range(segments):
        p=a.lerp(b,j/segments);q=a.lerp(b,(j+1)/segments)
        for course in range(3):
            upper=[p+n*(.12+course*.075),q+n*(.12+course*.075)];lower=[v.copy() for v in upper]
            for v in upper:v.z-=course*.35
            for v in lower:v.z-=(course+1)*.35+.015
            terrace.part([upper[0],upper[1],lower[1],lower[0]],[(0,1,2,3)],'strict_face')
        # Moss grows over the top edge, leaving the path and bare camp clear.
        p.z+=.01;q.z+=.01;moss.part([p,q,q-n*.48,p-n*.42],[(0,1,2,3)],'strict_moss')
terrace.build();moss.build()
# Attached rocky shoulders interrupt the broad foreground slope. These are
# shallow exposures, not the previously rejected separate foreground pillars.
import ast
source=ast.parse((ROOT/'tools/blender/build_strict_coast_landforms.py').read_text(encoding='utf8'))
for node in source.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='profiles' for t in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'profiles','exec'))
    if isinstance(node,ast.FunctionDef) and node.name=='rock':exec(compile(ast.Module(body=[node],type_ignores=[]),'rock','exec'))
for i,(x,y,w,d,h) in enumerate([(-59.1,10.0,1.8,1.6,.56),(-56.7,8.2,2.0,1.8,.72),(-54.7,9.0,1.5,1.25,.50)]):
    z=height_at(ft,x,y);rock('Cape_Strict_Attached_Exposure_'+str(i),x,y,w,d,z-.50,h+.50,.2*(-1)**i,i,(.06,.03),(.06,-.08))
# A small foreground spray is linked to existing near culms. Its real depth
# supplies framing at the edge, with the established actor clearance logic.
for num in [70,71]:
    src=SCENE.objects['Forest_Strict_Leaves_%02d'%num];bind=LAYOUT['forest_extension']['layer_roles']['wind_bindings'][src.name];root=Vector((bind['root'][0],-bind['root'][2],bind['root'][1]));b=Mesh('Forest_Strict_Low_Spray_%02d'%num)
    me=src.data;selected=[p for p in me.polygons if all(me.vertices[v].co.z<root.z+bind['height']*.49 for v in p.vertices)]
    for p in selected:
        vs=[me.vertices[v].co.copy() for v in p.vertices];uv=[tuple(me.uv_layers[0].data[li].uv) for li in p.loop_indices]
        for v in vs:v.z-=1.20
        b.part(vs,[tuple(range(len(vs)))],'strict_leaf',uv)
    if b.v:
        o=b.build(True);LAYOUT['forest_extension']['layer_roles']['wind_bindings'][o.name]=dict(bind)
        for li,l in enumerate(o.data.loops):p=o.data.vertices[l.vertex_index].co;o.data.uv_layers[1].data[li].uv=(0,1-max(0,min(1,(p.z-root.z)/bind['height']))**1.8)
# Pack updated raster structure and retain correct UV density.
for m in [MATS['strict_face'],MATS['strict_cap']]:
    for n in m.node_tree.nodes:
        if n.type=='TEX_IMAGE' and n.image:n.image.reload();n.image.pack()
state['near_ledge_done']=True;state['art_status']='Reference-driven working revision; not a claim of full visual equivalence';rc['cliff_masses']=state['rocks']
save('near-ledge-contact-review')
