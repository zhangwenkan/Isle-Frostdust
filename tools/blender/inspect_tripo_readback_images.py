"""Inspect embedded images after a readback assertion, via MCP."""
import bpy,json
s=bpy.data.scenes['Tripo_Textured_GLB_Readback_20261119']
images=set(n.image for o in s.objects if o.type=='MESH' for m in o.data.materials for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image)
rows=[]
for im in images:
    row={'name':im.name,'before_has_data':im.has_data,'size':list(im.size),'packed':bool(im.packed_file),'path':im.filepath,'pixel0':list(im.pixels[:4])}
    row['after_has_data']=im.has_data;rows.append(row)
print(json.dumps(rows))
