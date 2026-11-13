"""Author five original interlocking cliff modules and a representative study via MCP.
Only new explicit profiles are used; never reads or derives any reference game's mesh.
"""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/original_coastal_rock';O=R/'artifacts/original-shore-review';O.mkdir(exist_ok=True)
old=bpy.context.window.scene
if bpy.data.scenes.get('Original_Shore_Studio'):bpy.data.scenes.remove(bpy.data.scenes['Original_Shore_Studio'])
s=bpy.data.scenes.new('Original_Shore_Studio');bpy.context.window.scene=s
def material(name,fn):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=1
 tx=m.node_tree.nodes.get('OriginalPaint') or m.node_tree.nodes.new('ShaderNodeTexImage');tx.name='OriginalPaint';tx.image=bpy.data.images.load(str(A/fn),check_existing=True);tx.image.reload();m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color']);return m
side=material('Original_Coast_Stone_Side','warm_rock_sides.png');topmat=material('Original_Coast_Stone_Top','warm_rock_tops.png')
# Unequal corner spacing creates large mineral faces plus narrower oblique breaks.
profiles=[
 [(-.50,-.12),(-.40,-.39),(-.18,-.51),(.19,-.49),(.43,-.28),(.51,.06),(.36,.39),(.02,.48),(-.34,.34)],
 [(-.51,-.24),(-.25,-.49),(.14,-.45),(.38,-.34),(.50,-.02),(.37,.30),(.10,.46),(-.28,.42),(-.48,.16)],
 [(-.48,-.27),(-.23,-.41),(.10,-.53),(.38,-.38),(.53,-.10),(.40,.35),(.06,.45),(-.38,.32),(-.52,.02)],
 [(-.51,-.06),(-.36,-.41),(-.06,-.46),(.28,-.39),(.48,-.17),(.45,.20),(.22,.43),(-.13,.47),(-.41,.24)],
 [(-.50,-.19),(-.32,-.38),(.06,-.49),(.39,-.30),(.51,.04),(.33,.36),(-.03,.49),(-.35,.35),(-.46,.09)]
]
# x/y center, breadth/depth/height, top offset, lean, profile. Broad connected sections.
modules=[
 [(-1.30,.18,3.5,2.6,5.5,0.,.42,0),(1.28,.38,2.8,2.8,5.1,-.21,-.38,1),(.15,-.64,3.3,1.1,2.5,-2.35,.65,3)],
 [(-1.50,.25,2.25,2.7,5.3,-.24,-.40,2),(.65,.16,4.3,2.9,5.8,0.,.32,4),(-1.10,-.64,1.7,1.3,3.6,-1.70,-.40,1)],
 [(-1.28,.32,3.8,2.7,5.4,0.,.38,1),(1.50,.29,2.4,2.65,5.65,-.17,-.42,3),(1.35,-.68,3.4,1.4,2.6,-2.15,.55,2)],
 [(-1.62,.30,2.5,2.7,5.5,-.21,.45,4),(.75,.16,3.95,2.8,5.6,0.,-.36,0),(-1.15,-.55,2.8,1.2,4.0,-1.20,.48,3)],
 [(-1.08,.26,4.0,2.8,5.7,0.,-.40,3),(1.65,.30,2.3,2.6,5.4,-.27,.48,2),(.15,-.67,3.5,1.1,2.3,-2.8,-.55,4)]
]
def make_block(spec,tile):
 cx,cy,w,d,h,ztop,lean,pid=spec;outline=profiles[pid];N=len(outline)
 # Carefully stepped side profile: irregular shoulders, a local cut, tapered sea foot.
 seam=[.36,.57,.43,.61,.29,.49,.38,.54,.66,.42,.59,.33,.47,.63,.36][tile%15]
 levels=[0,.13,seam-.035,seam+.025,.79,1.0]
 scales=[.93,1.015,1.0,.965,.98,.84]
 verts=[];faces=[];mats=[];uvs=[]
 lengths=[0.]
 for j in range(N):
  a=Vector(outline[j]);b=Vector(outline[(j+1)%N]);lengths.append(lengths[-1]+(b-a).length)
 for k,t in enumerate(levels):
  for j,(x,y) in enumerate(outline):
   # Changes stay on broad planes; adjacent faces share the same joint corners.
   variation=[-.04,.018,-.018,.035,-.028,.025,.005,-.024,.012][(j+pid)%N]
   slant=[-.07,.03,.08,-.02,-.08,.035,.065,-.04,.01][(j+tile)%N]
   facet=[.035,-.015,.02,-.035,.01,-.02,.015,-.01,.025][(j+tile)%N]
   cut=[0,.02,.055,-.01,-.045,-.055,.025,.01,-.02][(k+pid)%9]
   local_cut=([.0,.06,-.035,.025,-.02,.045,-.015,.01,-.025][(j+tile)%N] if k in [2,3] else 0)
   xx=cx+x*w*(scales[k]+facet*t+local_cut)+lean*t+variation*w*(t*.7)+cut*w*.35
   yy=cy+y*d*(scales[k]+facet*t+local_cut)+.10*t*(1 if pid%2 else -1)
   zz=ztop-h*t+slant*math.sin(math.pi*t)*2.5
   zz+=(x*.34+min(0,[0,-.09,-.025,-.14,-.07,-.02,-.10,-.04,-.12][(j+pid)%N]))*(1-t)
   # Oblique joints occupy a few faces, with different heights and depths around the rock.
   if k in [2,3]:zz+=(-x*.52+y*.18)*(-1 if tile%3==1 else 1)
   if 1<=j<=3 and k==3:yy+=.11*(1 if j==2 else .3)
   verts.append((xx,yy,zz))
 def suv(u,t):return ((tile%4+(.007+.986*u))/4,1-(tile//4+(.012+.976*t))/4)
 for k in range(len(levels)-1):
  for j in range(N):
   jj=(j+1)%N;faces.append((k*N+j,k*N+jj,(k+1)*N+jj,(k+1)*N+j));mats.append(0)
   u0,u1=lengths[j]/lengths[-1],lengths[j+1]/lengths[-1];uvs.extend([suv(u0,levels[k]),suv(u1,levels[k]),suv(u1,levels[k+1]),suv(u0,levels[k+1])])
 faces.append(tuple(reversed(range(N))));mats.append(1)
 for j in reversed(range(N)):
  x,y=outline[j];uvs.append(((tile%4+.05+(x+.53)*.85)/4,1-(tile//4+.05+(y+.53)*.85)/4))
 faces.append(tuple((len(levels)-1)*N+j for j in range(N)));mats.append(0);uvs.extend([suv(.5,1)]*N)
 me=bpy.data.meshes.new('OriginalMineralBlock_%02d'%tile);me.from_pydata(verts,[],faces);me.materials.append(side);me.materials.append(topmat);me.update();uv=me.uv_layers.new(name='MineralUV');uv.data.foreach_set('uv',[v for pair in uvs for v in pair])
 for p,m in zip(me.polygons,mats):p.material_index=m;p.use_smooth=False
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new('OriginalBlock_%02d'%tile,me);s.collection.objects.link(ob)
 # Small physical corner chamfers catch daylight; large faces remain planar.
 mod=ob.modifiers.new('MineralCornerWear','BEVEL');mod.width=.008;mod.segments=1;mod.limit_method='ANGLE';mod.angle_limit=.72;mod.affect='EDGES'
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);ob.select_set(False)
 return ob
templates=[]
for i,definition in enumerate(modules):
 blocks=[make_block(spec,i*3+j) for j,spec in enumerate(definition)]
 bpy.ops.object.select_all(action='DESELECT')
 for ob in blocks:ob.select_set(True)
 bpy.context.view_layer.objects.active=blocks[0];bpy.ops.object.join();ob=blocks[0];ob.name='Original_Shore_Module_%02d'%i;ob['authoring']='Original explicit mineral profiles, Blender MCP';ob.location.x=i*7.6;ob.location.z=5.8;templates.append(ob)
camd=bpy.data.cameras.new('OriginalRockStudy');cam=bpy.data.objects.new('OriginalRockStudy',camd);s.collection.objects.link(cam);s.camera=cam
target=Vector((15.2,0,3));cam.location=(19,-34,15);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=39
world=bpy.data.worlds.new('OriginalRockStudyWorld');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.28,.32,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65;s.world=world
ld=bpy.data.lights.new('OriginalRockStudySun','SUN');ld.energy=2.1;ld.angle=.12;light=bpy.data.objects.new('OriginalRockStudySun',ld);s.collection.objects.link(light);light.rotation_euler=(.5,-.45,-.5)
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1600;s.render.resolution_y=650;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard';s.render.image_settings.file_format='PNG';s.render.filepath=str(O/'original-modules.png');bpy.ops.render.render(write_still=True,scene=s.name)
bpy.data.libraries.write(str(A/'original_coastal_rock.blend'),{s},path_remap='ABSOLUTE',fake_user=True,compress=True)
(A/'geometry-design.json').write_text(json.dumps(dict(profiles=profiles,modules=modules,source='new explicit profiles; no imported model data'),indent=2),encoding='utf8')
bpy.context.window.scene=old
print('ORIGINAL_MODULES_READY',len(templates))
