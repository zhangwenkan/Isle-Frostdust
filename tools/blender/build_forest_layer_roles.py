"""Author the narrow bamboo band and painted-depth carriers via Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
REVIEW=ROOT/'artifacts/forest-layer-role-review'
assert not bpy.data.collections.get('45_Forest_Layer_Roles'),'Inspect the current pass before repeating mutations.'
COL=bpy.data.collections.new('45_Forest_Layer_Roles');SCENE.collection.children.link(COL)
ARCH=bpy.data.collections.new('90_Rejected_Dense_Valley_Forest');SCENE.collection.children.link(ARCH)
archived=[]
for ob in list(SCENE.objects):
    if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
    remove=any(c.name=='44_Valley_Forest_Backdrop' for c in ob.users_collection)
    if ob.name.startswith('Forest_Bamboo_'):
        suffix=ob.name.removeprefix('Forest_Bamboo_').removeprefix('Canopy_')
        if suffix.isdigit():remove=remove or int(suffix) in [3,8,9,14,16,17] or int(suffix)>=18
        else:remove=remove or suffix.startswith(('Terminal_','EndBank_','DeepRow_'))
    if remove:
        for collection in list(ob.users_collection):collection.objects.unlink(ob)
        ARCH.objects.link(ob);ob.hide_render=True;ob.hide_set(True);archived.append(ob.name)
LAYOUT['forest_extension']['groves']=[g for g in LAYOUT['forest_extension']['groves'] if g['name'] not in archived]

floors=[SCENE.objects[n] for n in ['WALK_Forest_Ground','WALK_Forest_NearSlope','WALK_Left_Ground']]
bvhs=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]) for o in floors]
def ground(x,y):
    hits=[b.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0] for b in bvhs]
    hits=[h.z for h in hits if h is not None]
    assert hits,(x,y,'root outside authored ground')
    return max(hits)

def texture_mat(name,file,cutout=True):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.94
    im=bpy.data.images.load(str(OUT/'forest_layers'/file),check_existing=True);im.reload();im.pack()
    node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=im
    m.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
    if cutout:m.node_tree.links.new(node.outputs['Alpha'],p.inputs['Alpha']);m.surface_render_method='DITHERED'
    m.use_backface_culling=False
    return m
sprays=[texture_mat('ForestRole_Leaf_%d'%i,'leaf_spray_%d.png'%i) for i in range(3)]
paintings={name:texture_mat('ForestRole_'+name,file,name!='Depth') for name,file in [('Depth','forest_depth.png'),('Middle','forest_shapes_middle.png'),('Near','forest_shapes_near.png')]}
# Plane axes are calibrated to the established viewing angle in author space.
angle=math.radians(30.55);right=Vector((1,0,0));up=Vector((0,math.sin(angle),math.cos(angle)));normal=right.cross(up)
def card(builder,center,width,height,material,wind=.0,turn=.0,flip=False,bow=.0,nx=8,ny=3):
    r=right*math.cos(turn)+up*math.sin(turn);u=up*math.cos(turn)-right*math.sin(turn)
    vs=[];uv=[];weights=[];fs=[]
    for j in range(ny+1):
        for i in range(nx+1):
            s=i/nx;t=j/ny
            vs.append(Vector(center)+r*((s-.5)*width)+u*((t-.5)*height)+normal*(math.sin(s*math.pi)*math.sin(t*math.pi)*bow))
            uv.append((1-s if flip else s,t));weights.append(wind*(.35+.65*abs(s-.5)*2))
    for j in range(ny):
        for i in range(nx):
            a=j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
    builder.part(vs,fs,material,uv,weights)

# Individual culms, not entire duplicated groves. Gaps align with clearings.
xs=[-59.2,-57.9,-56.0,-53.7,-52.8,-49.8,-48.5,-46.8,-44.5,-43.7,-41.4,-39.8,
    -37.0,-35.8,-33.9,-32.7,-30.6,-28.7,-27.4,-25.1,-23.8,-22.2,-20.0,-18.8,-16.8,-14.7,-13.2,-10.5,-8.4,-6.3]
roots=[]
for i,x in enumerate(xs):
    y=16.45+[.0,.35,-.24,.42,-.18][i%5];z=ground(x,y)-.025
    h=[9.3,8.8,9.8,9.1,10.0,8.6][i%6];radius=[.097,.076,.092,.108,.084][i%5]
    base=Vector((x,y,z));bend=Vector(([-.25,.17,.32,-.12][i%4],.12,0))
    def center(v):return base+Vector((0,0,v))+bend*(v/h)**1.8
    body=Mesh('Forest_Bamboo_Role_Main_%02d'%i)
    intervals=round(h/.66);levels=[j*h/intervals for j in range(intervals+1)]
    tube(body,[center(v) for v in levels],[radius*(1-.57*v/h) for v in levels],'culm',8,[(v/h)**1.9 for v in levels])
    for v in levels[1:-1]:
        r=radius*(1-.57*v/h)
        tube(body,[center(v-.022),center(v+.022)],[r*1.11,r*1.11],'node',8,[(v/h)**1.9]*2)
    crown=Mesh('Forest_Bamboo_Role_Leaves_%02d'%i)
    for k in range(4):
        # Keep the lower four-plus metres open; small upper cards make a canopy.
        v=h*(.59+k*.105);direction=-1 if (i+k)%2 else 1
        start=center(v);end=start+Vector((direction*(1.15 if k<2 else .95),[-.14,.12,.04][(i+k)%3],.22))
        tube(body,[start,start.lerp(end,.52)+Vector((0,0,.11)),end],[.022,.013,.005],'branch',5,[(v/h)**1.9]*3)
        w=[2.85,3.25,2.65,2.45][k];height=w*[.77,.60,.53][(i+k)%3]
        c=end+right*(direction*w*.21)-up*(height*.12)
        card(crown,c,w,height,sprays[(i+k)%3],(v/h)**1.8,[-.13,.10,.03,-.07][(i+k)%4],direction<0,.12)
    ob=body.build();leaf_ob=crown.build()
    LAYOUT['forest_extension']['groves'].extend([{'name':ob.name,'band':'role_main'},{'name':leaf_ob.name,'band':'role_main'}])
    roots.append({'object':ob.name,'root':list(base),'height':h,'radius':radius,'lower_branch':h*.59})

# A few near silhouettes, with empty intervals and root-fixed wind.
for i,(x,y) in enumerate([(-50.3,8.1),(-35.1,8.3),(-20.2,8.4)]):
    z=ground(x,y)-.025;h=[8.9,9.3,8.8][i];base=Vector((x,y,z))
    body=Mesh('Forest_Bamboo_Role_Front_%02d'%i)
    tube(body,[base+Vector((-.15*(j/13)**2,0,j*h/13)) for j in range(14)],[.105*(1-.53*j/13) for j in range(14)],'culm',8,[(j/13)**2 for j in range(14)])
    for j in range(1,13):
        p=base+Vector((-.15*(j/13)**2,0,j*h/13));r=.105*(1-.53*j/13)*1.1
        tube(body,[p-Vector((0,0,.025)),p+Vector((0,0,.025))],[r,r],'node',8,[(j/13)**2]*2)
    crown=Mesh('Forest_Bamboo_Role_FrontLeaf_%02d'%i)
    for k in range(2):
        start=base+Vector((-.1,0,h*(.76+k*.13)));d=-1 if (i+k)%2 else 1;end=start+Vector((d*1.2,0,.16))
        tube(body,[start,end],[.022,.005],'branch',5,[.6,.8])
        card(crown,end+right*(d*.58),3.5,2.0,sprays[(i+k)%3],.85,.06*d,d<0,.13)
    for ob in [body.build(),crown.build()]:LAYOUT['forest_extension']['groves'].append({'name':ob.name,'band':'role_front'})

carriers=[]
for name,center,width,height in [('Near',(-32,29.0,9.1),112,20),('Middle',(-32,43,12.0),134,29),('Depth',(-32,64,18.0),164,48)]:
    b=Mesh('Forest_Paint_'+name);card(b,center,width,height,paintings[name],.0,.0,False,.0,32,8);ob=b.build()
    ob['role']='distant painted forest, no solid bamboo geometry';ob['source']='assets/layered_island/forest_layers/SOURCE.json'
    carriers.append({'name':ob.name,'center':center,'width':width,'height':height})
LAYOUT['forest_extension']['layer_roles']={'collection':COL.name,'main_culms':len(xs),'foreground_culms':3,'painted_layers':carriers,'roots':roots}
LAYOUT['forest_extension']['valley_enclosed']={'collection':COL.name,'background':'three independent forest paintings behind a narrow main bamboo band','no_sea_sky_in_forest':True}
(REVIEW/'build-report.json').write_text(json.dumps({'archived':archived,'main_roots':roots,'carriers':carriers,'source':'Blender MCP author scene'},indent=2),encoding='utf-8')
export('forest-layer-roles')
