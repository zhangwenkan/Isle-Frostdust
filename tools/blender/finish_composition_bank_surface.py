"""Remove duplicate thin ground skirts; articulate the connected near-bank core."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf8').read(),'left_finish_common.py','exec'))
R=ROOT/'artifacts/rock-stair-composition-review';state=LAYOUT['reference_cape']['rock_stair_composition']
assert not state.get('bank_surface_finished')
ground=SCENE.objects['WALK_Forest_Ground'];bm=bmesh.new();bm.from_mesh(ground.data)
bad=[]
for f in bm.faces:
 c=f.calc_center_median()
 if -60.9<c.x<-53.9 and c.y<8.8 and f.normal.z<.78:bad.append(f)
bmesh.ops.delete(bm,geom=bad,context='FACES');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ground.data);bm.free();ground.data.update()

# The continuous core has a broad forward shoulder and a recessed seam,
# rather than a straight architectural facade. The original end boundary
# remains fixed, so the existing forest cliff connects without a sea slit.
wall=SCENE.objects['Cape_Terminus_Bedrock'];bm=bmesh.new();bm.from_mesh(wall.data)
for x in [-59.65,-57.7,-56.1,-54.9]:
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(x,0,0),plane_no=(1,0,0),dist=.00001)
for v in bm.verts:
 p=v.co;wx=sm(-61.0,-59.6,p.x)*(1-sm(-54.9,-53.96,p.x));front=1-sm(4.0,8.2,p.y)
 shape=.22*max(0,1-abs(p.x+57.7)/1.8)-.18*max(0,1-abs(p.x+55.6)/1.2)
 p.y+=(shape+.13*max(0,1-abs(p.z-1.8)/1.25))*wx*front
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(wall.data);bm.free();wall.data.update()

# Slightly deeper mineral palette at the feet and facade keeps upper rock
# planes readable without the pale, uniform block appearance of the first
# colored preview. These are the authored images, not a new noise layer.
import numpy as np
for name in state['rocks']+['Cape_Terminus_Bedrock','Cape_Stair_Support']:
 m=SCENE.objects[name].data.materials[0]
 for n in m.node_tree.nodes:
  if n.type!='TEX_IMAGE' or not n.image:continue
  im=n.image;data=np.asarray(im.pixels[:],dtype=np.float32).reshape(-1,4)
  ratio=np.array([.90,.92,.94]) if 'Toe_' in name or name=='Cape_Terminus_Bedrock' else np.array([.95,.96,.98])
  data[:,:3]*=ratio;im.pixels.foreach_set(data.ravel());im.save();im.pack()
state['bank_surface_finished']=True;state['duplicate_skirt_faces_removed']=len(bad)
state['stage']='static colored sample, pending user evaluation'
export('rock-stair-composition-effect-review')
(R/'authoring-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'duplicate_ground_skirt_faces_removed':len(bad)}))
