import bpy
for n in ['Fish_Seabed','Mist_Peak_Near_01','Mist_Peak_Near_02','Mist_Peak_Near_03','Mist_Peak_Far_01','Mist_Peak_Far_02','Mist_Peak_Far_03','Mist_Peak_Far_04','Mist_Peak_Far_05']:
 o=bpy.data.objects.get(n)
 if o:
  b=o.bound_box; ws=[o.matrix_world@__import__('mathutils').Vector(c) for c in b]
  print(n, 'bounds', [[round(min(p[i] for p in ws),2),round(max(p[i] for p in ws),2)] for i in range(3)], 'verts',len(o.data.vertices))
