"""Correct sheet normals and reload the cleaned beach albedo via Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
for name in ['WALK_Left_Beach','Beach_Swash_Film']:
    ob=SCENE.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);bm.normal_update()
    negative=[f for f in bm.faces if f.normal.z<0.]
    bmesh.ops.reverse_faces(bm,faces=negative);bm.to_mesh(ob.data);bm.free();ob.data.update()
    print(name,'flipped',len(negative))
for im in bpy.data.images:
    if '/beach_swatch/' in bpy.path.abspath(im.filepath).replace('\\','/'):
        if im.packed_file:im.unpack(method='REMOVE')
        im.reload();im.pack()
export('beach-swash-refined')
