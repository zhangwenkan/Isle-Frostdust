from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘')
AUDIT_PHASE='review'
exec(compile((R/'tools/blender/audit_forest_backwall.py').read_text(encoding='utf8'),'audit_forest_backwall.py','exec'))
assert result['degenerate_triangles']==0
assert result['negative_top_orientation_count']==0
t=trees['after'];profiles=[]
for x in [-14,-10,-6,-2]:
 row={'x':x,'samples':[]}
 for depth in [2.5,4.5,5.5,6.8,8.5,10,12]:
  p=t.ray_cast(Vector((x,depth,40)),Vector((0,0,-1)))[0]
  row['samples'].append({'depth':depth,'height':p.z if p else None})
 profiles.append(row)
unused=True
for ob in s.objects:
 if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
 for mat in ob.data.materials:
  if mat and mat.use_nodes:
   for n in mat.node_tree.nodes:
    if n.type=='TEX_IMAGE' and n.image and 'forest_backdrop' in n.image.name:unused=False
assert unused
(O/'terrace-profiles.json').write_text(json.dumps({'profiles':profiles,'painted_backdrop_not_used':unused},indent=2),encoding='utf8')
print('TERRACE_PROFILES',json.dumps(profiles))
