import bpy,json
from pathlib import Path
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
scene=bpy.data.scenes['Island_Refined']
out=[]
for ob in scene.objects:
    if ob.type!='MESH' or any(c.name.startswith('90_') for c in ob.users_collection):continue
    pts=[ob.matrix_world@v.co for v in ob.data.vertices]
    lo=[min(v[a] for v in pts) for a in range(3)]
    hi=[max(v[a] for v in pts) for a in range(3)]
    if lo[0]>-12 or hi[0]<-30:continue
    out.append({'name':ob.name,'bounds_blender':[lo,hi],'vertices':len(pts),
        'materials':[m.name for m in ob.data.materials], 'uv':[u.name for u in ob.data.uv_layers]})
(ROOT/'artifacts/west-cape-opening-review/source-inspection.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out))
