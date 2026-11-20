"""Inspect an export/readback mismatch without redoing modelling."""
import bpy,json
for sn in ['Tripo_Surface_Measurement_Rebuild_20261119','Tripo_Replica_GLB_Static_Readback_20261119']:
    s=bpy.data.scenes.get(sn)
    print(json.dumps({'scene':sn,'objects':[{'name':o.name,'type':o.type,'selected':o.select_get(),'hidden':o.hide_render,'faces':len(o.data.polygons) if o.type=='MESH' else None} for o in s.objects]},ensure_ascii=False))
