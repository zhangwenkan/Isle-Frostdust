"""Read current saved sample and source material; executed through Blender MCP."""
import bpy,json
sn='Tripo_Surface_Measurement_Rebuild_20261119'
s=bpy.data.scenes.get(sn);ref=bpy.data.scenes.get('Tripo_Coast_Processing_20261119')
report={'file':bpy.data.filepath,'active_scene':bpy.context.scene.name,'sample_scene':sn if s else None,'reference_scene':ref.name if ref else None}
if s:report['sample_meshes']=[{'name':o.name,'faces':len(o.data.polygons),'uvs':[uv.name for uv in o.data.uv_layers]} for o in s.objects if o.type=='MESH']
if ref:
    o=ref.objects['Tripo_Coast_Original_Surface']
    report['reference']={'name':o.name,'uvs':[u.name for u in o.data.uv_layers],'materials':[{'name':m.name,'nodes':[{'name':n.name,'type':n.type,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None,'size':list(n.image.size) if n.type=='TEX_IMAGE' and n.image else None} for n in m.node_tree.nodes]} for m in o.data.materials]}
print(json.dumps(report,ensure_ascii=False))
