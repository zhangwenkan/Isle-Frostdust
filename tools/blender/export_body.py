# A Blender-authored contact disk is moved with the sprite in Godot.
if not bpy.data.objects.get('ContactShadow'):
    vs=[(math.cos(j*math.tau/32)*.33,0,math.sin(j*math.tau/32)*.19) for j in range(32)]
    mesh('ContactShadow',vs,[tuple(range(32))],['wet_rock'],'12_Birds')

# Validate every asset and use coherent outward normals before interchange.
stats={};total_triangles=0
for c in COL.values():
    if c.name.startswith('90_'):continue
    count=tri=0
    for ob in c.objects:
        if ob.type!='MESH':continue
        ob.data.validate(verbose=False)
        bm=bmesh.new();bm.from_mesh(ob.data)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(ob.data);bm.free()
        ob.data.calc_loop_triangles();tri+=len(ob.data.loop_triangles);count+=1
    stats[c.name]={'objects':count,'triangles':tri};total_triangles+=tri

save()
bpy.ops.object.select_all(action='DESELECT')
for c in COL.values():
    if c.name.startswith('90_'):continue
    for ob in c.objects:
        if ob.type=='MESH':ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'nameless_island.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=True)
report={'authoring':'Blender 5.1 via blender-mcp execute_blender_code','collections':stats,'triangles':total_triangles,'blend_file':str(OUT/'nameless_island.blend'),'glb_file':str(OUT/'nameless_island.glb')}
(OUT/'asset_manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
