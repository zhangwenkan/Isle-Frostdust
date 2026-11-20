"""Remove old platform intrusions and design broad rock-face breaks via MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
R=ROOT/'artifacts/rock-stair-composition-review'
LAYOUT=json.loads((R/'grey-layout.json').read_text(encoding='utf8'))
state=LAYOUT['reference_cape']['rock_stair_composition']
assert not state.get('enclosure_refined'), 'Already refined; inspect saved version.'
assert bpy.data.collections.get(state['collection'])
rocks=[SCENE.objects[n] for n in state['rocks']]

# Main faces get broad, individually located faults and shoulders. Bisecting
# shared topology produces real changes in planes, without repeated noise.
designs={
 'Sea_Front':[(2.50,.16,.18), (1.36,-.12,.11)],
 'Stair_Right':[(2.42,-.12,.18),(1.55,.18,-.09)],
 'Stair_Left':[(1.52,.14,.15)],
 'Near_Upper':[(1.83,-.17,.20)],
 'Near_Lower':[(1.30,.16,.12)],
 'Near_Seam':[(1.70,-.21,.16)],
 'Sea_West':[(2.10,.16,.14)]}
for suffix,lines in designs.items():
 o=SCENE.objects['Cape_Strict_Rock_'+suffix];me=o.data
 bm=bmesh.new();bm.from_mesh(me)
 lo=min(v.co.y for v in bm.verts);hi=max(v.co.y for v in bm.verts)
 for z,slope,reach in lines:
  center=sum((v.co.x for v in bm.verts))/len(bm.verts)
  n=Vector((slope,0,1));p=Vector((center,0,z))
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=p,plane_no=n,dist=.00001)
  for v in bm.verts:
   d=(v.co-p).dot(n)/n.length
   band=max(0,1-abs(d)/.70)
   front=1-sm(lo+.22,hi-.40,v.co.y)
   v.co.y-=reach*band*front
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()

trees=[BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]) for o in rocks]
def roof(x,y):
 hits=[]
 for t in trees:
  p,n,idx,dist=t.ray_cast(Vector((x,y,15)),Vector((0,0,-1)),20)
  if p is not None and n.z>.22:hits.append(p.z)
 return max(hits,default=None)

# Preserve interpolated original UV layers while giving the old large deck
# triangles enough vertices to follow the actual irregular exposed blocks.
ground=SCENE.objects['WALK_Forest_Ground'];bm=bmesh.new();bm.from_mesh(ground.data)
for iteration in range(3):
 edges=[e for e in bm.edges if e.calc_length()>.65 and all(v.co.x<-53.6 and v.co.y<19 for v in e.verts)]
 if not edges:break
 bmesh.ops.subdivide_edges(bm,edges=edges,cuts=1,use_grid_fill=True)
changed=0
for v in bm.verts:
 p=v.co
 if p.x>-53.6 or p.y>19:continue
 h=roof(p.x,p.y)
 if h is not None and p.z>h-.055 and p.z-h<1.45:
  p.z=h-.055;changed+=1
 # The exposed near edge steps down inside the designed rock shoulders.
 if -60.9<p.x<-54.0 and p.y<7.7:
  edge=1-sm(4.3,7.7,p.y)
  p.z-=.38*edge*sm(-60.9,-59.7,p.x)*(1-sm(-54.8,-54.0,p.x))
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ground.data);bm.free();ground.data.update()

# Old bedrock remains the buried continuous core. Its upper rim now sits
# below exposed rock, rather than cutting a light-colored band through it.
wall=SCENE.objects['Cape_Terminus_Bedrock']
for v in wall.data.vertices:
 p=v.co;h=roof(p.x,p.y)
 if h is not None and p.z>h-.12:p.z=h-.12
 if -61.2<p.x<-54.0 and p.y<9.2:
  p.y+=.85*(1-sm(6.8,9.2,p.y))
  p.z-=.55*(1-sm(4.0,8.3,p.y))*sm(.6,3.7,p.z)
wall.data.update()

# Keep existing nearby plant groups on the new substrate. This is asset
# fitting for the effect preview; no passage/continuous movement audit runs.
gt=BVHTree.FromPolygons([v.co for v in ground.data.vertices],[list(p.vertices) for p in ground.data.polygons])
def substrate(x,y):
 p,n,i,d=gt.ray_cast(Vector((x,y,15)),Vector((0,0,-1)),20)
 vals=[v for v in [p.z if p else None,roof(x,y)] if v is not None]
 return max(vals,default=None)
for name in ['Forest_Strict_Grass','Forest_Strict_Understory']:
 o=SCENE.objects.get(name)
 if not o:continue
 for start in range(0,len(o.data.vertices)-14,15):
  vs=[o.data.vertices[start+j] for j in range(15)];base=(vs[0].co+vs[2].co)*.5
  if base.x>-53.6 or base.y>19:continue
  h=substrate(base.x,base.y)
  if h is None or abs(h-base.z)>1.6:continue
  for v in vs:v.co.z+=h+.012-base.z
 o.data.update()

state['enclosure_refined']=True;state['platform_vertices_recessed']=changed
state['stage']='revised geometry with exposed main roofs and buried core'
(R/'authoring-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf8')
(R/'refined-layout.json').write_text(json.dumps(LAYOUT,ensure_ascii=False,indent=2),encoding='utf8')
bpy.data.libraries.write(str(R/'refined-authoring.blend'),{SCENE},fake_user=True,compress=True)
print(json.dumps({'platform_vertices_recessed':changed,'ground_vertices':len(ground.data.vertices),'saved':'refined-authoring.blend'}))
