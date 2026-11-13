import bpy,json
from pathlib import Path
scene=bpy.data.scenes['Island_Refined'];report=[]
for i in [0,2,3,4]:
    ob=scene.objects['InkSample_Rock_%02d'%i]
    report.append({'name':ob.name,'vertices':[list(v.co) for v in ob.data.vertices],
        'faces':[{'index':p.index,'vertices':list(p.vertices),'normal':list(p.normal),'center':list(p.center),'area':p.area} for p in ob.data.polygons]})
Path('D:/自己做着玩的/孤屿霜尘/artifacts/rock-weathering-review/source-faces.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('WEATHERING_SOURCE_INSPECTED')
