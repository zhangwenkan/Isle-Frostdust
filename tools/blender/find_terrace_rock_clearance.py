from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');AUDIT_OUTPUT=R/'artifacts/forest-backwall-review';AUDIT_PHASE='search'
exec(compile((R/'tools/blender/audit_forest_rock_roots.py').read_text(encoding='utf8'),'audit_forest_rock_roots.py','exec'))
ob=scene.objects['InkSample_Rock_04'];rt=tree(ob);pts=[ob.matrix_world@v.co for v in ob.data.vertices];center=sum(pts,Vector())/len(pts)
lo=Vector(tuple(min(p[i] for p in pts) for i in range(3)));hi=Vector(tuple(max(p[i] for p in pts) for i in range(3)))
near=[p for n,p,h in samples if lo.x-1.1<p.x<hi.x+1.1 and lo.y-.7<p.y<hi.y+.7]
oldground=ground(center.x,center.y);candidates=[]
for dx in [-.8,-.6,-.4,-.2,0,.2,.4,.6,.8]:
 for dy in [-.5,-.35,-.2,0,.2,.35,.5]:
  h=ground(center.x+dx,center.y+dy)
  if h is None:continue
  delta=Vector((dx,dy,h-oldground));count=0
  for p in near:
   q=p-delta
   if not(lo.x<q.x<hi.x and lo.y<q.y<hi.y and lo.z<q.z<hi.z):continue
   top=rt.ray_cast(Vector((q.x,q.y,hi.z+1)),Vector((0,0,-1)))[0]
   bottom=rt.ray_cast(Vector((q.x,q.y,lo.z-1)),Vector((0,0,1)))[0] if top else None
   if top and bottom and bottom.z+.008<q.z<top.z-.008:count+=1
  candidates.append({'delta':list(delta),'count':count,'distance2':dx*dx+dy*dy})
candidates.sort(key=lambda a:(a['count'],a['distance2']))
(AUDIT_OUTPUT/'rock-clearance-candidates.json').write_text(json.dumps(candidates,indent=2),encoding='utf8')
print('ROCK_CLEARANCE_CANDIDATES',json.dumps(candidates[:8]))
