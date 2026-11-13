from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');AUDIT_OUTPUT=R/'artifacts/coast-unification-review';AUDIT_PHASE='candidate'
exec(compile((R/'tools/blender/audit_forest_rock_roots.py').read_text(encoding='utf8'),'audit_forest_rock_roots.py','exec'))
ob=scene.objects['InkSample_Rock_04'];pts=[ob.matrix_world@v.co for v in ob.data.vertices];center=sum(pts,Vector())/len(pts)
origin_ground=ground(center.x,center.y);candidates=[]
for dx in [-1.4,-1.0,-.6,-.3,0,.3,.6,1.0]:
 for dy in [-1.0,-.6,-.3,0,.3,.6,1.0,1.4]:
  h=ground(center.x+dx,center.y+dy)
  if h is None:continue
  delta=Vector((dx,dy,h-origin_ground));q=[p+delta for p in pts]
  rt=BVHTree.FromPolygons(q,[tuple(p.vertices) for p in ob.data.polygons])
  low=Vector([min(p[i] for p in q) for i in range(3)]);high=Vector([max(p[i] for p in q) for i in range(3)])
  collisions=0
  for stem,p,z in samples:
   if not(low.x<=p.x<=high.x and low.y<=p.y<=high.y and low.z<=p.z<=high.z):continue
   top=rt.ray_cast(Vector((p.x,p.y,high.z+1)),Vector((0,0,-1)))[0]
   bot=rt.ray_cast(Vector((p.x,p.y,low.z-1)),Vector((0,0,1)))[0]
   if top and bot and bot.z+.008<p.z<top.z-.008:collisions+=1
  candidates.append({'dx':dx,'dy':dy,'height':h,'collisions':collisions,'distance':math.hypot(dx,dy)})
candidates.sort(key=lambda c:(c['collisions'],c['distance']))
(AUDIT_OUTPUT/'rock-seat-candidates.json').write_text(json.dumps(candidates[:15],indent=2),encoding='utf8')
print('BEST_SEATS',json.dumps(candidates[:6]))
