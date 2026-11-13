import bpy,json
s=next(s for s in bpy.data.scenes if s.library and s.name=='WS_Bamboo_Study')
print('REFCOUNT',len(s.objects))
for o in [o for o in s.objects if 'SM_XYNJiangnan017' in o.name][:6]:
 print(o.name,dict(o.items()),list(o.matrix_world.translation),list(o.bound_box))
