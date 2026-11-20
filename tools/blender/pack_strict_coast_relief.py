"""Pack selected geological relief and connect the small lower foreground twigs."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/strict_coast_common.py',encoding='utf8').read(),'strict_coast_common.py','exec'))
assert not state.get('surface_relief_done')
m=MATS['strict_face'];im=bpy.data.images.load(str(T/'rock_normal.png'),check_existing=True);im.colorspace_settings.name='Non-Color';im.pack()
tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;n=m.node_tree.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.28;m.node_tree.links.new(tex.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs['Normal'],m.node_tree.nodes.get('Principled BSDF').inputs['Normal'])
for num in [70,71]:
    name='Forest_Strict_Low_Spray_%02d'%num;o=SCENE.objects.get(name)
    if not o:continue
    bind=LAYOUT['forest_extension']['layer_roles']['wind_bindings'][name];root=Vector((bind['root'][0],-bind['root'][2],bind['root'][1]));b=Mesh('Forest_Strict_Low_Branches_%02d'%num)
    for j in range(3):
        direction=Vector(((-1)**j*.75,.24*(-1)**num,0));start=root+Vector((0,0,bind['height']*(.29+j*.032)-1.17));end=start+direction
        tube(b,[start,start.lerp(end,.55)+Vector((0,0,.12)),end],[.017,.009,.003],'strict_branch',6)
    ob=b.build(True);LAYOUT['forest_extension']['layer_roles']['wind_bindings'][ob.name]=dict(bind)
    for li,l in enumerate(ob.data.loops):p=ob.data.vertices[l.vertex_index].co;ob.data.uv_layers[1].data[li].uv=(0,1-max(0,min(1,(p.z-root.z)/bind['height']))**1.8)
state['surface_relief_done']=True
save('surface-relief-review')
