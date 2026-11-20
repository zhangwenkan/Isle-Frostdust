"""Read modelling-method evidence; mutate diagnostic exposure only, via MCP."""
import bpy, bmesh, json, math
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/tripo-rock-stair-analysis'
original=bpy.context.window.scene;main=bpy.data.scenes['Layered_Island_20261116']
rows=[]
for name in ['Cape_Strict_Rock_Sea_West','Cape_Strict_Rock_Sea_Front','Cape_Strict_Rock_Stair_Left','Cape_Strict_Rock_Stair_Right','Cape_Strict_Rock_Toe_West']:
    o=main.objects[name];bm=bmesh.new();bm.from_mesh(o.data)
    def counts():
        return {'vertices':len(bm.verts),'faces':len(bm.faces),'edges':len(bm.edges),
                'boundary_edges':sum(e.is_boundary for e in bm.edges),
                'manifold_edges':sum(e.is_manifold for e in bm.edges),
                'eligible_for_soften_rule':sum(e.is_manifold and e.calc_face_angle()>.35 for e in bm.edges)}
    before=counts();bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);after=counts();bm.free()
    rows.append({'object':name,'original_mesh':before,'welded_analysis_copy':after})
ref=bpy.data.scenes['Tripo_Rock_Stair_Diagnostic_20261119']
for o in ref.objects:
    if o.type!='MESH' or o.name=='DiagnosticFloor':continue
    bm=bmesh.new();bm.from_mesh(o.data)
    tripo={'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges)};bm.free()
layout=json.loads((ROOT/'assets/layered_island/layout.json').read_text(encoding='utf8'))
stairs=layout['reference_cape']['stairs'];top=Vector(stairs['top']);bottom=Vector(stairs['bottom'])
delta=top-bottom;rise=abs(delta.y);run=math.hypot(delta.x,delta.z)
report={'scope':'Analysis only. Weld is in an uncommitted bmesh copy; no model modified.',
        'soften_rule':'e.is_manifold and e.calc_face_angle() > 0.35 radians',
        'current_rocks':rows,'tripo_mesh':tripo,
        'current_stairs':{'steps':stairs['steps'],'width':stairs['width'],'rise':rise,'run':run,'average_riser':rise/stairs['steps'],'average_tread_run':run/stairs['steps'],'slope_degrees':math.degrees(math.atan2(rise,run))},
        'interpretation_limit':'Final eligible counts alone cannot reconstruct every past bevel operation. Boundary seams and their change after welding demonstrate the structural disconnect in the selected meshes. Raw glTF import boundary counts can include UV/normal vertex splits and must not be equated with a count of real holes. Tripo topology is not a quality target.'}
(OUT/'method-inspection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
s=bpy.data.scenes['Rock_Stair_Comparative_Diagnostic_20261119'];bpy.context.window.scene=s
try:
    s.view_settings.exposure=1.3;cam=s.camera;prefix=s.name+'_'
    for angle in [0,35]:
        a=math.radians(angle);target=Vector((0,0,.23));cam.location=target+Vector((math.sin(a)*2.4,-math.cos(a)*2.4,1.05));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        for key in ['tripo','current']:
            for o in s.objects:
                if o.type=='MESH' and o.name.startswith(prefix+'current_'):o.hide_render=key!='current'
                elif o.type=='MESH' and o.name.startswith(prefix+'tripo_'):o.hide_render=key!='tripo'
            s.render.filepath=str(OUT/(key+'-matched-clay-'+str(angle)+'.png'));bpy.ops.render.render(write_still=True)
    bpy.data.libraries.write(str(OUT/'matched-diagnostic.blend'),{s},fake_user=True,compress=True)
    print(json.dumps({'method_inspection':rows,'outputs':4,'diagnostic_exposure':1.3}))
finally:bpy.context.window.scene=original
