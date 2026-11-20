"""Break up overly uniform grit; all material changes executed via Blender MCP."""
import bpy,json,math
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/tripo-replica-review';A=R/'assets/layered_island/tripo_replica'
s=bpy.data.scenes['Tripo_Stone_Grit_Review_20261119'];bpy.context.window.scene=s
assert s['revision']=='grit-material-lookdev-1'
m=s.objects['Grit_Rocks'].data.materials[0];n=m.node_tree.nodes;l=m.node_tree.links
r=n['Uneven rough patch coverage'].color_ramp
for el,pos,val in zip(r.elements,[.32,.51,.67],[.02,.25,1]):el.position=pos;el.color=(val,val,val,1)
# Whole planes are no longer covered by the same grain strength.
mix=n['Regional mineral pigment'];fac=mix.inputs[0].links[0].from_node;fac.inputs[1].default_value=.12
mul=fac.inputs[0].links[0].from_node;mul.inputs[1].default_value=.56
aggregate=n['Visible mineral tonal variation'].color_ramp
for el,val in zip(aggregate.elements,[.65,.82,1.04,1.23]):el.color=(val,val,val,1)
b=n['Meso shallow broken surface'];b.inputs['Strength'].default_value=.72;b.inputs['Distance'].default_value=.0038
n['Visible shallow fracture relief'].inputs['Scale'].default_value=61
b=n['Uneven mineral aggregate normal'];fac=b.inputs['Strength'].links[0].from_node;fac.inputs[1].default_value=.16
fac.inputs[0].links[0].from_node.inputs[1].default_value=.51
n['Fine grain normal'].inputs['Strength'].default_value=.16
s['revision']='grit-material-polished-2'
s.render.filepath=str(O/'roughness-polished-three-quarter.png');bpy.ops.render.render(write_still=True)
bpy.data.libraries.write(str(A/'tripo_grit_material_authoring.blend'),{s},fake_user=True,compress=True)
print('Regional grit polish saved.')
