"""Check exported gritty material, then render same-light comparisons via MCP."""
import bpy,json,math,numpy as np,traceback,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/tripo-replica-review';A=R/'assets/layered_island/tripo_replica'
assert json.loads((O/'roughness-bake-status.json').read_text())['status']=='complete'
base=bpy.data.scenes['Tripo_Grit_Textured_Delivery_20261119'];assert base['revision']=='grit-textures-baked-3'
SN='Tripo_Grit_GLB_Readback_20261119';assert not bpy.data.scenes.get(SN)
s=bpy.data.scenes.new(SN);bpy.context.window.scene=s;bpy.ops.import_scene.gltf(filepath=str(A/'tripo_replica_grit.glb'))
meshes=[o for o in s.objects if o.type=='MESH'];assert len(meshes)==2
mats=set(m for ob in meshes for m in ob.data.materials)
ims=set(n.image for m in mats for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image)
assert len(ims)==6
report={'status':'rendering','views':[],'mesh_count':len(meshes),'material_count':len(mats),'images':[],'surface_inputs':[],'unchanged_geometry_uv':{}}
for im in ims:
    first=im.pixels[:4];assert im.has_data and min(im.size)>=2048
    report['images'].append({'name':im.name,'size':list(im.size),'packed':bool(im.packed_file),'colorspace':im.colorspace_settings.name})
for m in mats:
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    assert bs.inputs['Base Color'].is_linked and bs.inputs['Normal'].is_linked and bs.inputs['Roughness'].is_linked
    report['surface_inputs'].append(m.name)
def mesh_hash(ob):
    me=ob.data;arrays=[]
    for data,prop,n,dtype in [(me.vertices,'co',3,np.float32),(me.loops,'vertex_index',1,np.int32),(me.uv_layers.active.data,'uv',2,np.float32)]:
        a=np.empty(len(data)*n,dtype=dtype);data.foreach_get(prop,a);arrays.append(a.tobytes())
    return hashlib.sha256(b''.join(arrays)).hexdigest()
for new,old in [('Grit_Delivery_Rocks','Delivery_Rocks'),('Grit_Delivery_Stairs','Delivery_Stairs')]:
    equal=mesh_hash(base.objects[new])==mesh_hash(bpy.data.scenes['Tripo_Textured_Delivery_20261119'].objects[old]);report['unchanged_geometry_uv'][new]=equal;assert equal
for ob in base.objects:
    if ob.type in {'LIGHT','CAMERA'} or ob.name.startswith('DiagnosticFloor'):
        cp=ob.copy();cp.data=ob.data.copy();s.collection.objects.link(cp)
        if cp.type=='CAMERA':s.camera=cp
s.world=base.world.copy();s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=960;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.view_settings.view_transform='AgX';s.view_settings.look=base.view_settings.look
jobs=[(35,'roughness-final-three-quarter.png',False),(0,'roughness-final-front.png',False),(35,'roughness-diagnostic-without-normal.png',True)]
def save(): (O/'roughness-readback.json').write_text(json.dumps(report,indent=2),encoding='utf8')
save()
def step():
    try:
        angle,f,disable=jobs.pop(0);report['current_view']=f;save();bpy.context.window.scene=s
        target=Vector((0,0,.21));a=math.radians(angle);cam=s.camera
        cam.location=target+Vector((math.sin(a)*2.4,-math.cos(a)*2.4,1.05));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        restored=[]
        if disable:
            for m in mats:
                if '_Stone' not in m.name:continue
                bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');link=bs.inputs['Normal'].links[0];restored.append((m,link.from_socket,bs.inputs['Normal']));m.node_tree.links.remove(link)
        try:s.render.filepath=str(O/f);bpy.ops.render.render(write_still=True)
        finally:
            for m,src,dst in restored:m.node_tree.links.new(src,dst)
        report['views'].append(f)
        if not jobs:report['status']='complete'
        save();return 1.0 if jobs else None
    except Exception:report['status']='failed';report['error']=traceback.format_exc();save();return None
bpy.app.timers.register(step,first_interval=1.0)
print(json.dumps({'status':'dispatched','image_count':len(ims),'material_count':len(mats),'geometry_uv':report['unchanged_geometry_uv']}))
