"""Refresh neutral diagnostic copies from the actual MCP authoring scene."""
import bpy,json,bmesh,math
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘/artifacts/rock-stair-composition-review')
state=json.loads((R/'authoring-state.json').read_text(encoding='utf8'))
source=bpy.data.scenes['Layered_Island_20261116'];d=bpy.data.scenes['Rock_Stair_Composition_Grey_20261119']
gray=bpy.data.materials['StrictCoast_Composition_Gray']
for o in list(d.objects):
 if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
for name in state['rocks']+['WALK_Cape_Stairs','Cape_Stair_Support','WALK_Forest_Ground']:
 o=source.objects[name];cp=o.copy();cp.data=o.data.copy();d.collection.objects.link(cp);cp.hide_render=False;cp.hide_set(False);cp.data.materials.clear();cp.data.materials.append(gray)
 for p in cp.data.polygons:p.material_index=0
 if name=='WALK_Forest_Ground':
  bm=bmesh.new();bm.from_mesh(cp.data)
  for point,normal in [((-69,0,0),(-1,0,0)),((-54,0,0),(1,0,0)),((0,0,0),(0,-1,0)),((0,19,0),(0,1,0))]:
   bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=point,plane_no=normal,clear_outer=True)
  bm.to_mesh(cp.data);bm.free()
old=bpy.context.window.scene;bpy.context.window.scene=d
try:
 target=Vector((-61.8,9.3,2.4))
 for angle in [0,28]:
  a=math.radians(angle);cam=d.camera;cam.location=target+Vector((math.sin(a)*30,-math.cos(a)*30,15));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
  d.render.filepath=str(R/('refined-grey-'+str(angle)+'.png'));bpy.ops.render.render(write_still=True)
finally:bpy.context.window.scene=old
print('Refined grey assembly rendered from actual source.')
