"""Inspect the actual authored scene and fix only inverted open ground faces."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
import math
REVIEW=ROOT/'artifacts/bamboo-west-extension-review'
COL=bpy.data.collections['43_West_Forest']
report={'scene':SCENE.name,'meshes':[],'reversed_ground_faces':0,'degenerate_faces':0}
for ob in COL.objects:
    if ob.type!='MESH':continue
    me=ob.data
    if ob.name in ['WALK_Forest_Ground','WALK_Forest_NearSlope']:
        bad=[p.index for p in me.polygons if p.normal.z<0]
        if bad:
            bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table()
            bmesh.ops.reverse_faces(bm,faces=[bm.faces[i] for i in bad]);bm.to_mesh(me);bm.free();me.update()
            report['reversed_ground_faces']+=len(bad)
    zero=sum(p.area<1e-10 for p in me.polygons);report['degenerate_faces']+=zero
    report['meshes'].append({'name':ob.name,'vertices':len(me.vertices),'faces':len(me.polygons),'uv_layers':len(me.uv_layers),'zero_area':zero,'materials':[m.name for m in me.materials]})
report['collection']=COL.name;report['camera']=LAYOUT['camera'];report['new_edges']=LAYOUT['forest_extension']['new_edges']
(REVIEW/'blender-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
if report['reversed_ground_faces']:export('west-forest-normal-correction')
print(json.dumps({'scene':report['scene'],'meshes':len(report['meshes']),'reversed_ground_faces':report['reversed_ground_faces'],'degenerate_faces':report['degenerate_faces']}))
