"""Refresh editable painted sources and audit the Blender-authored role division."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
REVIEW=ROOT/'artifacts/forest-layer-role-review'
refreshed=[]
for im in bpy.data.images:
    if '/forest_layers/' in bpy.path.abspath(im.filepath).replace('\\','/'):
        im.reload();im.pack();refreshed.append(im.name)
rows=[]
for ob in bpy.data.collections['45_Forest_Layer_Roles'].objects:
    if ob.type!='MESH':continue
    wind=ob.data.uv_layers.get('Wind')
    min_z=min(v.co.z for v in ob.data.vertices)
    root_loops=[loop.index for loop in ob.data.loops if ob.data.vertices[loop.vertex_index].co.z<min_z+.04]
    rows.append({'name':ob.name,'triangles':sum(len(p.vertices)-2 for p in ob.data.polygons),
                 'uv0':ob.data.uv_layers.get('UVMap') is not None,'uv2':wind is not None,
                 'root_wind_max':max([wind.data[i].uv.x for i in root_loops],default=0) if 'Role_Main' in ob.name or 'Role_Front_' in ob.name else None,
                 'materials':[m.name for m in ob.data.materials]})
assert all(r['uv0'] and r['uv2'] for r in rows)
assert all(r['root_wind_max'] is None or r['root_wind_max']==0 for r in rows)
(REVIEW/'blender-audit.json').write_text(json.dumps({'scene':SCENE.name,'refreshed_textures':refreshed,'objects':rows},indent=2),encoding='utf-8')
export('forest-layer-roles-reviewed')
