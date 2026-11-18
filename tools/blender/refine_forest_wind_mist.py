"""Bind existing bamboo, refine painted-layer projection, and author mist carriers via MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
REVIEW=ROOT/'artifacts/forest-wind-mist-review'
assert not bpy.data.collections.get('46_Forest_Layer_Mist'),'Inspect the existing refinement instead of repeating mutations.'
COL=bpy.data.collections.new('46_Forest_Layer_Mist');SCENE.collection.children.link(COL)
bindings={};changed=[]
roots=LAYOUT['forest_extension']['layer_roles']['roots']
for i,rec in enumerate(roots):
    root=Vector(rec['root']);h=rec['height'];bend=Vector(([-.25,.17,.32,-.12][i%4],.12,0))
    name='Forest_Bamboo_Role_Leaves_%02d'%i;ob=SCENE.objects[name]
    ends=[]
    for k in range(4):
        v=h*(.59+k*.105);d=-1 if (i+k)%2 else 1
        start=root+Vector((0,0,v))+bend*(v/h)**1.8
        ends.append(start+Vector((d*(1.15 if k<2 else .95),[-.14,.12,.04][(i+k)%3],.22)))
    wind=ob.data.uv_layers['Wind']
    for loop in ob.data.loops:
        p=ob.data.vertices[loop.vertex_index].co
        flex=min(1,min((p-end).length for end in ends)/1.8)
        # glTF flips UV V: encode 1-flex so Godot UV2.y contains flex.
        wind.data[loop.index].uv.y=1-flex
    binding={'root':[root.x,root.z,-root.y],'height':h,'seed':17.31+i*13.47,'amplitude':.82}
    bindings[rec['object']]=binding;bindings[name]=binding;changed.append(name)
for i in range(3):
    body=SCENE.objects['Forest_Bamboo_Role_Front_%02d'%i]
    z=min(v.co.z for v in body.data.vertices)
    low=[v.co for v in body.data.vertices if v.co.z<z+.03]
    root=sum(low,Vector())/len(low);h=[8.9,9.3,8.8][i]
    name='Forest_Bamboo_Role_FrontLeaf_%02d'%i;ob=SCENE.objects[name]
    ends=[root+Vector((-.1+(-1 if (i+k)%2 else 1)*1.2,0,h*(.76+k*.13)+.16)) for k in range(2)]
    wind=ob.data.uv_layers['Wind']
    for loop in ob.data.loops:
        p=ob.data.vertices[loop.vertex_index].co
        wind.data[loop.index].uv.y=1-min(1,min((p-end).length for end in ends)/2.0)
    binding={'root':[root.x,root.z,-root.y],'height':h,'seed':631.9+i*19.31,'amplitude':1.05}
    bindings[body.name]=binding;bindings[name]=binding;changed.append(name)
for key,new_z in [('Near',11.2),('Middle',7.0)]:
    ob=SCENE.objects['Forest_Paint_'+key]
    row=next(r for r in LAYOUT['forest_extension']['layer_roles']['painted_layers'] if r['name']==ob.name)
    delta=new_z-row['center'][2]
    for v in ob.data.vertices:v.co.z+=delta
    ob.data.update();row['center'][2]=new_z;changed.append(ob.name)
angle=math.radians(30.55);up=Vector((0,math.sin(angle),math.cos(angle)))
mist_mat=bpy.data.materials.new('ForestRole_Mist_Carrier');mist_mat.use_nodes=True
mist_mat.diffuse_color=(.45,.53,.40,.10)
principled=mist_mat.node_tree.nodes.get('Principled BSDF')
principled.inputs['Base Color'].default_value=(.45,.53,.40,1)
principled.inputs['Alpha'].default_value=.10;principled.inputs['Roughness'].default_value=1
mist_mat.surface_render_method='DITHERED';mist_mat.use_backface_culling=False
mist_rows=[]
for i,(name,center,width,height) in enumerate([('Front',(-32,24.0,10.0),112,6.0),('Middle',(-32,36.0,3.0),134,9.0),('Far',(-32,53.0,-6.3),164,13.0)]):
    b=Mesh('Forest_Mist_'+name);vs=[];uv=[];fs=[];nx=24;ny=6
    for j in range(ny+1):
        for k in range(nx+1):
            s=k/nx;t=j/ny;vs.append(Vector(center)+Vector(((s-.5)*width,0,0))+up*((t-.5)*height));uv.append((s,t))
    for j in range(ny):
        for k in range(nx):
            a=j*(nx+1)+k;fs.append((a,a+1,a+nx+2,a+nx+1))
    b.part(vs,fs,mist_mat,uv);ob=b.build();ob['role']='independent thin mist between painted forest layers'
    mist_rows.append({'name':ob.name,'layer':i,'center':center,'height':height,'width':width})
for im in bpy.data.images:
    if '/forest_layers/' in bpy.path.abspath(im.filepath).replace('\\','/'):im.reload();im.pack()
LAYOUT['forest_extension']['layer_roles']['wind_bindings']=bindings
LAYOUT['forest_extension']['layer_roles']['mist_layers']=mist_rows
(REVIEW/'blender-refine.json').write_text(json.dumps({'changed_existing':changed+['Forest_Paint_Depth'],'wind_bindings':bindings,'mist_layers':mist_rows,'body_geometry_unchanged':True,'uv2_v_encoding':'1-flex, glTF imported V is flex'},indent=2),encoding='utf-8')
export('irregular-wind-layered-mist')
