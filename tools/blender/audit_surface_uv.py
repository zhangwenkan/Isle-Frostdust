import bpy, json
from pathlib import Path
scene=bpy.context.scene
report={'file':bpy.data.filepath,'scene':scene.name,'materials':{},'objects':{}}
for m in bpy.data.materials:
 if m.name not in ['grass','rock','rock_light','rock_dark','moss','bark','wood','wet_rock']:continue
 imgs=[{'image':n.image.name,'size':list(n.image.size),'path':n.image.filepath} for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if m.use_nodes else []
 report['materials'][m.name]=imgs
for name in ['Sample_Hero_Pine_Rooted_Trunk','Sample_Split_Monolith','Bridge_Plank_00','Bridge_Weathered_Posts_Cross_Braces','West_Island_Grass_Soil']:
 ob=bpy.data.objects.get(name)
 if ob:
  caps=[list(p.vertices) for p in ob.data.polygons if len(p.vertices)>4]
  report['objects'][name]={'vertices':len(ob.data.vertices),'polygons':len(ob.data.polygons),'materials':[m.name for m in ob.data.materials],'caps':caps[:20],'bounds':[list(v) for v in ob.bound_box],'matrix':[list(v) for v in ob.matrix_world]}
path=Path('D:/自己做着玩的/孤屿霜尘/artifacts/surface-review/uv-before.json')
path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
