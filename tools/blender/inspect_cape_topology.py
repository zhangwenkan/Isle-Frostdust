import bpy,json
s=bpy.data.scenes['Island_Refined'];o=s.objects['Fish_West_Continuous_Land'];me=o.data;me.calc_loop_triangles()
bad=[t for t in me.loop_triangles if all(i<2626 for i in t.vertices) and t.normal.z<=0 and max(me.vertices[i].co.x for i in t.vertices)<-19.2]
print('BAD_TOP',len(bad),json.dumps([{'p':t.polygon_index,'ids':list(t.vertices),'xyz':[list(me.vertices[i].co) for i in t.vertices]} for t in bad[:14]]))
print('ROWS',json.dumps([[round(me.vertices[r*26+j].co.y,4) for j in range(26)] for r in range(4)]))
