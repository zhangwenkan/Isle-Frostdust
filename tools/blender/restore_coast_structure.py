"""Restore continuous cape structure and transplant the proven stair construction.
All geometry edits run inside Blender through blender-mcp. Main source is read only.
"""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/coast-structure-recovery';A=R/'assets/layered_island/coast_recovery';A.mkdir(exist_ok=True)
SN='Coast_Structure_Recovery_20261120';assert not bpy.data.scenes.get(SN)
s=bpy.data.scenes.new(SN);bpy.context.window.scene=s
base=bpy.data.scenes['Coast_Recovery_Strict_Baseline_20261120'];original=bpy.data.scenes['Coast_Recovery_Original_Readonly_20261120']
layout=json.loads((R/'assets/layered_island/layout.json').read_text())
def obj(sc,key):return next(o for o in sc.objects if o.name.split('.')[0]==key)
def sm(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def expand(p):
 q=p.copy();q.x-=max(0,-64.0-p.x)*1.15*(1-sm(17,24,p.y));return q
report={'scene':SN,'revision':'continuous-platform-original-stair-1','replace':[],'objects':{},'source_stair':'WALK_Left_Stairs_00','stair_steps':15}
def copy(sc,key,game=None,deform=None):
 old=obj(sc,key);o=old.copy();o.data=old.data.copy();o.name='Recovery_'+(game or key);o['game_name']=game or key;s.collection.objects.link(o);o.hide_render=False;o.hide_set(False)
 if deform:
  inv=o.matrix_world.inverted()
  for v in o.data.vertices:v.co=inv@deform(o.matrix_world@v.co)
  o.data.update()
 report['replace'].append(game or key);report['objects'][o.name]={'source_scene':sc.name,'source_object':old.name,'vertices':len(o.data.vertices)}
 return o
# Restore the continuous pre-Tripo ground and bedrock, then extend the left
# platform in plan. The stair notch, inner forest route and roots are preserved.
for key in ['WALK_Forest_Ground','Cape_Terminus_Bedrock','Forest_Strict_Grass','Forest_Strict_Understory','Forest_Strict_Flowers']:
 copy(base,key,deform=expand)
# Sand and the existing thin swash carrier follow the same seaward footprint.
for key in ['WALK_Cape_Sand','Cape_Swash_Film']:
 copy(original,key,deform=expand)
for key in ['Cape_Strict_Paving','Cape_Timber_Seat','Cape_Timber_Endgrain']:
 try:copy(original,key,deform=expand)
 except StopIteration:pass
for old in original.objects:
 key=old.name.split('.')[0]
 if key.startswith(('Cape_Fire_Ring_','Cape_Fire_Log_')):copy(original,key,deform=expand)
# Source flight includes individual 2/3-piece treads, full foundation and fitted
# side curbs. Retain its topology and thickness instead of inventing a new flight.
a=Vector((-5.496454,-3.198341,.15));b=Vector((-4.728013,-.180178,2.849998))
c=Vector((-62.5,4,.15));d=Vector((-63.3,8.8,3.8564))
u=Vector((b.x-a.x,b.y-a.y,0));source_run=u.length;u.normalize();v=Vector((u.y,-u.x,0))
U=Vector((d.x-c.x,d.y-c.y,0));target_run=U.length;U.normalize();V=Vector((U.y,-U.x,0))
def stair_map(p):
 rel=p-a;return c+U*(rel.dot(u)*target_run/source_run)+V*(rel.dot(v)*1.10)+Vector((0,0,rel.z*(d.z-c.z)/(b.z-a.z)))
flight=copy(original,'WALK_Left_Stairs_00','WALK_Cape_Stairs',stair_map)
# A clean restrained base for this structure check; material roles are explicit.
def stone(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.94;return m
face=stone('Recovery_Face_Stone',(.28,.30,.265));tread=stone('Recovery_Tread_Stone',(.38,.39,.335));edge=stone('Recovery_Edge_Stone',(.31,.33,.28))
for o in s.objects:
 if o.type!='MESH':continue
 if o['game_name']=='WALK_Cape_Stairs':
  for i,m in enumerate(list(o.data.materials)):o.data.materials[i]=tread if any(k in m.name for k in ['tread','paving']) else (edge if 'rock_a' in m.name else face)
 elif o['game_name']=='Cape_Terminus_Bedrock':
  o.data.materials.clear();o.data.materials.append(face)
  for p in o.data.polygons:p.material_index=0
 elif o['game_name']=='WALK_Forest_Ground':
  for i,m in enumerate(list(o.data.materials)):
   if not any(k in m.name for k in ['Floor','floor']):o.data.materials[i]=face
# Keep the runtime scene's old island source and anchors immutable on disk.
def godot(p):return [p.x,p.z,-p.y]
report['anchors']={key:godot(expand(Vector((v[0],-v[2],v[1])))) for key,v in layout['anchors'].items() if 'cape' in key}
fire=layout['reference_cape']['fire_center'];report['fire_center']=godot(expand(Vector((fire[0],-fire[2],fire[1]))))
report['shoreline']=[[expand(Vector((p[0],-p[1],0))).x,p[1]] for p in layout['reference_cape']['shoreline']]
report['retire_extra']=['Cape_Stair_Support']
s['revision']=report['revision']
# Names prefixed for isolation; runtime maps them to their known shader roles.
for o in s.objects:o.select_set(o.type=='MESH')
bpy.context.view_layer.objects.active=flight
bpy.data.libraries.write(str(A/'coast_structure.blend'),{s},fake_user=True,compress=True)
bpy.ops.export_scene.gltf(filepath=str(A/'coast_structure.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_materials='EXPORT',export_vertex_color='ACTIVE',export_all_vertex_colors=True,export_cameras=False,export_lights=False)
(A/'assembly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');(O/'structure-pass1.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('COAST_STRUCTURE_EXPORTED',len(s.objects))
