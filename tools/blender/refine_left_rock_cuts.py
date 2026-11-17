"""Cut individual diagonal shoulders; retain broad face hierarchy and foot scale."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
for image in bpy.data.images:
    if 'left_finish_textures' in bpy.path.abspath(image.filepath):
        if image.packed_file:image.unpack(method='REMOVE')
        image.reload();image.pack()
records=[]
for idx,ob in enumerate([o for o in COL.objects if o.name.startswith('Left_Rock_') and 'ShoreChip' not in o.name]):
    if ob.get('cut_shoulders'):continue
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
    xs=[v.co.x for v in bm.verts];ys=[v.co.y for v in bm.verts];zs=[v.co.z for v in bm.verts]
    cx=(min(xs)+max(xs))*.5;cy=(min(ys)+max(ys))*.5;dx=max(xs)-min(xs);dy=max(ys)-min(ys);h=max(zs);bottom=min(zs)
    skew=[-.10,.14,-.09,.11,-.13,.13,-.09,.11,-.1][idx%9]
    for v in bm.verts:
        t=(v.co.z-bottom)/(h-bottom);v.co.x+=skew*t*(v.co.y-cy);v.co.y+=.08*t*(v.co.x-cx)
    cuts=[(Vector((cx,min(ys)+dy*.14,h*.74)),Vector((.12 if idx%2 else -.14,-.77,.62))),
          (Vector((cx+dx*.39,cy,h*.51)),Vector((.91,-.22,.35)))]
    for co,no in cuts:
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=co,plane_no=no,clear_outer=True)
        border=[e for e in bm.edges if e.is_boundary]
        if border:
            filled=bmesh.ops.holes_fill(bm,edges=border,sides=0)
            for f in filled.get('faces',[]):f.material_index=min(1,len(ob.data.materials)-1)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
    for p in ob.data.polygons:
        p.use_smooth=False
        # Existing face-coordinate UVs are retained; new cut surfaces get their
        # own aligned projection. UV interpolation from a collapsed edge is not used.
        for li in p.loop_indices:
            co=ob.data.vertices[ob.data.loops[li].vertex_index].co
            if abs(p.normal.z)>.6:uv=((co.x-cx)/dx+.5,(co.y-cy)/dy+.5)
            elif abs(p.normal.x)>.7:uv=((co.y-cy)/dy+.5,(co.z-bottom)/(h-bottom))
            else:uv=((co.x-cx)/dx+.5,(co.z-bottom)/(h-bottom))
            ob.data.uv_layers[0].data[li].uv=uv
    ob['cut_shoulders']=True;records.append(ob.name)
(REVIEW/'rock-cuts.json').write_text(json.dumps(records,indent=2))
export('rock-cuts')
