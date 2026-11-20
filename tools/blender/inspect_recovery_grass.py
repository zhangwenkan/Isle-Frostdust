import bpy,json
s=bpy.data.scenes['Coast_Recovery_Original_Readonly_20261120']
print([(o.name,len(o.data.vertices),list(o.dimensions)) for o in s.objects if o.type=='MESH' and o.name.startswith('Left_Grass')][:20])
