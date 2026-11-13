import bpy,json
s=bpy.data.scenes['Island_Refined']
for o in s.objects:
 if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection) and ('Fern' in o.name or any(c.name=='25_Cliff_Ledge_Plants' for c in o.users_collection)):print(o.name,[c.name for c in o.users_collection])
