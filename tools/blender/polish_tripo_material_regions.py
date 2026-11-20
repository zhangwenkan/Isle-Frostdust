"""Final lookdev corrections via Blender MCP, before UV baking."""
import bpy,numpy as np,json
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/tripo-replica-review';A=R/'assets/layered_island/tripo_replica'
s=bpy.data.scenes['Tripo_Authored_Material_Sample_20261119'];bpy.context.window.scene=s
assert s['revision']=='authored-material-refined-3'
m=bpy.data.materials['Authored_Warm_Fractured_Stone']
for n in m.node_tree.nodes:
    if n.type=='MIX_RGB':
        c=n.inputs[2].default_value
        if abs(c[0]-.37)<.0001 and abs(c[1]-.334)<.0001:n.inputs[2].default_value=(.255,.226,.175,1)
    if n.type=='VALTORGB':
        e=n.color_ramp.elements
        if abs(e[0].position-.59)<.0001:
            e[0].position=.71;e[-1].position=.98;e[-1].color=(.7,.7,.7,1)
        if abs(e[0].position-.32)<.0001 and abs(e[-1].position-.60)<.0001:
            e[0].position=.43;e[0].color=(0,0,0,1);e[-1].position=.63
        if abs(e[0].color[0]-.028)<.0001 and abs(e[0].color[1]-.043)<.0001:
            e[0].color=(.023,.029,.009,1);e[-1].color=(.075,.091,.023,1)
ob=s.objects['Textured_Measured_Rocks'];me=ob.data
cent=np.empty(len(me.polygons)*3,np.float32);me.polygons.foreach_get('center',cent);cent=cent.reshape(-1,3)
ids=np.empty(len(me.polygons),np.int32);me.polygons.foreach_get('material_index',ids)
ids[ids==1]=0
for pa,pb,width,zmin in [((.119,.063),(.164,-.056),.0175,.344),((-.178,.043),(-.137,-.079),.014,.345)]:
    a=np.array(pa);b=np.array(pb);v=b-a;t=np.clip(((cent[:,:2]-a)@v)/(v@v),0,1)
    dist=np.linalg.norm(cent[:,:2]-(a+t[:,None]*v),axis=1)
    ids[(dist<width)&(cent[:,2]>zmin)&(cent[:,2]<.39)]=1
me.polygons.foreach_set('material_index',ids);me.update()
# The low-resolution stair mesh needs analytic nose masks, not a vertex
# smoothing radius inherited from the much denser rock mesh.
st=s.objects['Textured_Authored_Stairs'];v=np.array([x.co[:] for x in st.data.vertices])
st.data.attributes['Authored_Structural_Curvature'].data.foreach_set('value',np.full(len(v),.5,dtype=np.float32))
s['revision']='authored-material-polished-4'
s.render.filepath=str(O/'authored-material-polished-35.png');bpy.ops.render.render(write_still=True)
bpy.data.libraries.write(str(A/'tripo_material_authoring.blend'),{s},fake_user=True,compress=True)
(O/'material-polished.json').write_text(json.dumps({'revision':s['revision'],'wood_faces':int(np.count_nonzero(ids==1)),'status':'Rendered, pending texture bake.'},indent=2),encoding='utf8')
print('Material polish rendered.')
