"""Resolve over-soft sculpt into readable stone planes, within new sample."""
import bpy,bmesh,math,json
from mathutils import Vector
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Fresh_Pixel_Cape'];bpy.context.window.scene=scene
assert scene['revision']=='fresh-cape-reference-polish-3'
ob=bpy.data.objects['Rock_Continuous_Sculpted_Beds']
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
sm=ob.modifiers.new('Simplify rounded micro relief','SMOOTH');sm.factor=.8;sm.iterations=4
bpy.ops.object.modifier_apply(modifier=sm.name)
dec=ob.modifiers.new('Broad chiseled plane scale','DECIMATE');dec.ratio=.21
bpy.ops.object.modifier_apply(modifier=dec.name)
bm=bmesh.new();bm.from_mesh(ob.data)
bmesh.ops.dissolve_limit(bm,angle_limit=math.radians(9),verts=list(bm.verts),edges=list(bm.edges),use_dissolve_boundaries=False)
bm.to_mesh(ob.data);bm.free()
for p in ob.data.polygons:p.use_smooth=False

# A few exposed mid-scale strata. They follow the actual new sculpted surface.
rockcol=bpy.data.collections['Fresh_02_Rock_Faces']
def strip(name,xzs,width,material):
    vs=[]
    for x,z in xzs:
        for dz in [-width*.5,width*.5]:
            hit,point,normal,idx=ob.ray_cast(Vector((x,-12,z+dz)),Vector((0,1,0)))
            if not hit:return
            vs.append(tuple(point+Vector((0,-.008,0))))
    fs=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(xzs)-1)]
    me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(vs,[],fs);me.update()
    line=bpy.data.objects.new(name,me);rockcol.objects.link(line);me.materials.append(material)
    uv=me.uv_layers.new(name='UVMap')
    for i,l in enumerate(me.loops):p=me.vertices[l.vertex_index].co;uv.data[i].uv=(p.x*.2,p.z*.2)
    line['fresh_sample']=True;line['authored_from']='sparse sculpt-attached stratum'
dark=bpy.data.materials['Fresh_Rock_Dark']
strip('Rock_Stratum_West',[(-10.3,2.32),(-9.95,2.27),(-9.58,2.24),(-9.15,2.28)],.026,dark)
strip('Rock_Stratum_Center',[(-6.6,2.51),(-6.20,2.46),(-5.75,2.48)],.025,dark)
strip('Rock_Stratum_Entry',[(-3.25,1.62),(-2.99,1.68),(-2.71,1.62)],.022,dark)
scene['revision']='fresh-cape-reference-polish-4'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/fresh_pixel_cape/fresh_pixel_cape.blend'))
print(json.dumps({'revision':scene['revision'],'stone_faces':len(ob.data.polygons)}))
