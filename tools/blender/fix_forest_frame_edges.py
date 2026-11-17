"""Keep all open construction edges outside the playable cameras in Blender."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
REVIEW=ROOT/'artifacts/bamboo-west-extension-review';COL=bpy.data.collections['43_West_Forest']
assert not LAYOUT['forest_extension'].get('frame_edges_closed')
# Extend the land past the last camera; do not stretch the path or character.
for name in ['WALK_Forest_Ground','WALK_Forest_NearSlope','Forest_Back_Ground']:
    ob=SCENE.objects[name]
    for v in ob.data.vertices:
        if v.co.x<-43.6:v.co.x=-43.6+(v.co.x+43.6)*3.6
    ob.data.update()
# Taper the new near slope into the original upper terrace, rather than letting
# a high green sheet project over the old beach in the wide coastal camera.
ob=SCENE.objects['WALK_Forest_NearSlope']
front=json.loads((REVIEW/'forest-layout.json').read_text())['outline'][:6]
for v in ob.data.vertices:
    x=v.co.x
    if x<=-27:continue
    k=min(len(front)-2,max(0,next((j for j in range(len(front)-1) if front[j+1][0]>=x),len(front)-2)))
    a,b=front[k:k+2];t=max(0,min(1,(x-a[0])/(b[0]-a[0])));edge=a[1]+(b[1]-a[1])*t+.08
    v.co.y=edge+(v.co.y-edge)*sm(-18.2,-27,x)
ob.data.update()
# Close the exposed outer skirt down to the submerged rock base. Boundary
# edges shared with the upper floor have a small overlap, never a raised lip.
mesh=ob.data;bm=bmesh.new();bm.from_mesh(mesh);border=[(e.verts[0].co.copy(),e.verts[1].co.copy()) for e in bm.edges if e.is_boundary];bm.free()
b=Mesh('Forest_Near_Closed_Skirt')
for p,q in border:
    if p.y>6 and q.y>6:continue
    vs=[p,q,Vector((q.x+.07,q.y+.05,-.65)),Vector((p.x+.07,p.y+.05,-.65))]
    b.part(vs,[(0,1,2,3)],'rock_b',[(p.x*.25,p.z*.3),(q.x*.25,q.z*.3),(q.x*.25,-.2),(p.x*.25,-.2)])
b.build()
# A few intact groves occupy the newly off-camera banks and screen the endpoint.
floor_mesh=SCENE.objects['WALK_Forest_Ground'].data;bvh=BVHTree.FromPolygons([v.co for v in floor_mesh.vertices],[list(p.vertices) for p in floor_mesh.polygons])
for index,dx,dy in [(26,-5.,0.),(32,-6.,-1.),(37,-11.,0.)]:
    source=SCENE.objects['Forest_Bamboo_%02d'%index]
    center=sum((Vector(v) for v in source.bound_box),Vector())/8
    root=min(v.co.z for v in source.data.vertices)
    hit=bvh.ray_cast(Vector((center.x+dx,center.y+dy,30)),Vector((0,0,-1)))[0]
    dz=hit.z-root-.025 if hit else 0
    for canopy in [False,True]:
        source=SCENE.objects[('Forest_Bamboo_Canopy_' if canopy else 'Forest_Bamboo_')+'%02d'%index]
        ob=source.copy();ob.data=source.data.copy();ob.name='Forest_Bamboo_EndBank_%d_%d'%(index,int(canopy));COL.objects.link(ob)
        for v in ob.data.vertices:v.co+=Vector((dx,dy,dz))
        ob.data.update();LAYOUT['forest_extension']['groves'].append({'name':ob.name,'band':'deep' if index>26 else 'rear'})
LAYOUT['forest_extension']['frame_edges_closed']=True
export('west-forest-frame-edges')
