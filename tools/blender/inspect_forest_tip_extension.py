"""Read the saved terrain, material and contact state through Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
O=ROOT/'artifacts/forest-tip-extension-review'
report={'source':bpy.data.filepath,'revision':LAYOUT['revision'],'objects':[]}
for ob in SCENE.objects:
    if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
    if not (ob.name.startswith('Cape_') or ob.name in ['WALK_Forest_Ground','WALK_Cape_Stairs']):continue
    me=ob.data;me.calc_loop_triangles()
    colors=me.color_attributes.active_color
    data={'name':ob.name,'matrix':[list(r) for r in ob.matrix_world],'bounds':[[min(v.co[k] for v in me.vertices),max(v.co[k] for v in me.vertices)] for k in range(3)],'materials':[m.name for m in me.materials],'uv_layers':[u.name for u in me.uv_layers],'faces':len(me.polygons),'negative_up_faces':sum(p.normal.z<-.1 for p in me.polygons),'color_bounds':[[min(d.color[k] for d in colors.data),max(d.color[k] for d in colors.data)] for k in range(3)] if colors else None}
    if ob.name=='WALK_Forest_Ground':
        tree=BVHTree.FromPolygons([v.co for v in me.vertices],[list(p.vertices) for p in me.polygons])
        data['samples']=[]
        for x in [-63,-61.5,-61.25,-61.1,-60.9,-60.5,-59.5,-55]:
            h,n,i,d=tree.ray_cast(Vector((x,13.0,40)),Vector((0,0,-1)))
            if h is None:continue
            p=me.polygons[i]
            data['samples'].append({'x':x,'hit':list(h),'normal':list(n),'vertex_normals':[list(me.vertices[vi].normal) for vi in p.vertices],'material':me.materials[p.material_index].name,'color':[list(colors.data[li].color) for li in p.loop_indices] if colors else None,'uv':[list(me.uv_layers[0].data[li].uv) for li in p.loop_indices]})
    report['objects'].append(data)
(O/'inspect-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'revision':report['revision'],'terrain':[r for r in report['objects'] if r['name']=='WALK_Forest_Ground']},ensure_ascii=False))
