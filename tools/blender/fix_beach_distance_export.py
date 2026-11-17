"""Compensate glTF's V-axis convention for numeric signed distance in UV2.y."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
for name in ['WALK_Left_Beach','Beach_Swash_Film']:
    ob=SCENE.objects[name]
    if not ob.get('shore_v_compensated'):
        for data in ob.data.uv_layers[1].data:data.uv.y=1.-data.uv.y
        ob['shore_v_compensated']=True
LAYOUT['beach_swatch']['uv2_export_y_compensated']=True
export('beach-distance-corrected')
