"""Read-only asset audit of live Blender scene and explicitly protected geometry."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
REVIEW=ROOT/'artifacts/beach-swash-review';COL=bpy.data.collections['42_Beach_Swash']
protected=json.loads((REVIEW/'protected-geometry.json').read_text());changed=[]
for name,expected in protected.items():
    ob=SCENE.objects.get(name)
    if not ob:changed.append(name+': missing');continue
    blob=repr(([(tuple(v.co)) for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons],[[tuple(d.uv) for d in uv.data] for uv in ob.data.uv_layers],list(map(tuple,ob.matrix_world)))).encode()
    if hashlib.sha256(blob).hexdigest()!=expected:changed.append(name)
live=[o for o in SCENE.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
records=[]
for ob in COL.objects:
    row={'name':ob.name,'vertices':len(ob.data.vertices),'faces':len(ob.data.polygons),'uv_layers':[u.name for u in ob.data.uv_layers],'materials':[m.name for m in ob.data.materials]}
    if ob.name.startswith(('Left_Beach_Pebble',)):
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
        row['boundary_edges']=sum(e.is_boundary for e in bm.edges);bm.free()
    if ob.name.startswith(('Left_Bamboo','Left_Grass')):
        w=[d.uv.x for d in ob.data.uv_layers[1].data]
        row['wind_range']=[min(w),max(w)];row['root_weights_zero']=sum(abs(v)<1e-5 for v in w)
    records.append(row)
result={'protected_geometry_count':len(protected),'protected_changed':changed,'live_meshes':len(live),'left_meshes':len(records),'beach_objects':records,'live_legacy_bamboo':[o.name for o in live if o.name.startswith(('Bamboo_','Space_Bamboo'))], 'file_sizes':{p.name:p.stat().st_size for p in [OUT/'layered_island.blend',OUT/'layered_island.glb']}}
(REVIEW/'blender-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='beach_objects'}))
