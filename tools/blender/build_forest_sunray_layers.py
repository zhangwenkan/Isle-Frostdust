"""Six thin light carriers, authored inside Blender through the MCP connection."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
assert not bpy.data.collections.get('47_Forest_Sunray_Layers'),'Inspect existing carriers; do not repeat their construction.'
COL=bpy.data.collections.new('47_Forest_Sunray_Layers');SCENE.collection.children.link(COL)
m=bpy.data.materials.new('ForestRole_Sunray_Carrier');m.use_nodes=True
p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.8,.75,.57,1);p.inputs['Alpha'].default_value=.08;p.inputs['Roughness'].default_value=1
m.surface_render_method='DITHERED';m.use_backface_culling=False
up=Vector((0,math.sin(math.radians(30.55)),math.cos(math.radians(30.55))))
rows=[]
for layer,(name,y,z,xs,width,height,strength) in enumerate([
    ('Near',25,7.8,[-34,-50],8.0,10.0,.14),
    ('Middle',37,2.7,[-32,-47],10.0,13.0,.12),
    ('Depth',54,-6.2,[-27,-42],13.0,18.0,.10)]):
    for i,x in enumerate(xs):
        center=Vector((x,y,z));right=Vector((width*.5,0,0));vertical=up*height*.5
        b=Mesh('Forest_Sunray_%s_%d'%(name,i))
        b.part([center-right-vertical,center+right-vertical,center+right+vertical,center-right+vertical],[(0,1,2,3)],m,[(0,0),(1,0),(1,1),(0,1)])
        ob=b.build();ob['role']='solar scattering carrier interleaved with painted forest, not tree geometry'
        rows.append({'name':ob.name,'layer':layer,'center':list(center),'width':width,'height':height,'strength':strength})
LAYOUT['forest_extension']['layer_roles']['sunray_layers']=rows
(ROOT/'artifacts/forest-light-depth-review/blender-sunray.json').write_text(json.dumps({'source_study':'artifacts/bamboo-atmosphere-source-study/README.md','new_carriers':rows,'existing_geometry_or_uv_changed':False},indent=2),encoding='utf-8')
export('forest-shared-light-depth')
