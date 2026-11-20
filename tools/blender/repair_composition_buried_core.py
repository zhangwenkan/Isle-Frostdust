"""Restore the original connected core boundary, preserving exposed new rocks."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
R=ROOT/'artifacts/rock-stair-composition-review';state=LAYOUT['reference_cape']['rock_stair_composition']
assert not state.get('core_seam_repaired')
wall=SCENE.objects['Cape_Terminus_Bedrock'];material=wall.data.materials[0]
original=SCENE.objects['Composition_Before_Cape_Terminus_Bedrock']
wall.data=original.data.copy();wall.data.materials.clear();wall.data.materials.append(material)
trees=[BVHTree.FromPolygons([v.co for v in SCENE.objects[n].data.vertices],[list(p.vertices) for p in SCENE.objects[n].data.polygons]) for n in state['rocks']]
for v in wall.data.vertices:
 p=v.co;heights=[]
 for t in trees:
  loc,normal,i,d=t.ray_cast(Vector((p.x,p.y,15)),Vector((0,0,-1)),20)
  if loc is not None and normal.z>.22:heights.append(loc.z)
 if heights and p.z>max(heights)-.14:p.z=max(heights)-.14
wall.data.update()
# Core paint projection is restored from actual coordinates; the existing
# six-island painting retains its calm palette rather than the old crack map.
uv=wall.data.uv_layers.get('UVMap') or wall.data.uv_layers.new(name='UVMap')
lo=[min(v.co[i] for v in wall.data.vertices) for i in range(3)];hi=[max(v.co[i] for v in wall.data.vertices) for i in range(3)]
for p in wall.data.polygons:
 p.material_index=0;a=max(range(3),key=lambda i:abs(p.normal[i]));group=a*2+(0 if p.normal[a]>0 else 1);ax=[(1,2),(0,2),(0,1)][a]
 for li in p.loop_indices:
  co=wall.data.vertices[wall.data.loops[li].vertex_index].co
  uv.data[li].uv=((group%3*320+14+(co[ax[0]]-lo[ax[0]])/max(.001,hi[ax[0]]-lo[ax[0]])*292)/960,(group//3*320+14+(co[ax[1]]-lo[ax[1]])/max(.001,hi[ax[1]]-lo[ax[1]])*292)/640)
state['core_seam_repaired']=True;state['core_note']='Original connected boundary restored; no shifted open core or Boolean thin sheets.'
export('rock-stair-composition-core-review')
(R/'authoring-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf8')
