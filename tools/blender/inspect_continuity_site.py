"""Read saved UV registration and attached wind roots through Blender MCP."""
import bpy,json,numpy as np
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/cape-forest-continuity-review'
L=json.loads((R/'assets/layered_island/layout.json').read_text(encoding='utf-8'))
report={'uv':{},'roots':{},'objects':[]}
for name in ['WALK_Forest_Ground','WALK_Forest_NearSlope','WALK_Cape_Neck']:
    me=bpy.data.objects[name].data;pts=[];values=[]
    for p in me.polygons:
        if p.material_index!=0:continue
        for li in p.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co
            pts.append([co.x,co.y,1]);values.append(list(me.uv_layers[0].data[li].uv))
    a=np.asarray(pts);b=np.asarray(values);fit=np.linalg.lstsq(a,b,rcond=None)[0]
    report['uv'][name]={'affine':fit.tolist(),'max_error':float(np.abs(a@fit-b).max()),'samples':[{'p':pts[i],'uv':values[i]} for i in range(0,len(pts),max(1,len(pts)//8))][:8]}
for k,v in L['forest_extension']['layer_roles']['wind_bindings'].items():
    if v['root'][0]<-52:report['roots'][k]=v
for ob in bpy.context.scene.objects:
    if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
    x=min((ob.matrix_world@v.co).x for v in ob.data.vertices);xx=max((ob.matrix_world@v.co).x for v in ob.data.vertices)
    if x<-52 and xx>-70.5:report['objects'].append({'name':ob.name,'xmin':x,'xmax':xx,'matrix':list(map(list,ob.matrix_world))})
(O/'site.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'uv':{k:{'affine':v['affine'],'max_error':v['max_error']} for k,v in report['uv'].items()},'roots':report['roots'],'object_names':[v['name'] for v in report['objects']]}))
