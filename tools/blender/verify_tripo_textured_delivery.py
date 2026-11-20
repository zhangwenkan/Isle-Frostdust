"""Re-import the final GLB and render it, via Blender MCP. Static verification."""
import bpy,json,math,time,traceback,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/tripo-replica-review';A=R/'assets/layered_island/tripo_replica'
state=json.loads((O/'material-bake-status.json').read_text(encoding='utf8'));assert state['status']=='complete'
base=bpy.data.scenes['Tripo_Textured_Delivery_20261119'];assert base['revision']=='authored-textures-baked-6-material-slots-preserved'
SN='Tripo_Textured_GLB_Readback_20261119';s=bpy.data.scenes.get(SN)
if s:
    assert len(s.objects)==2 and not s.camera,'Only resume the initial image-load assertion.'
    bpy.context.window.scene=s
else:
    s=bpy.data.scenes.new(SN);bpy.context.window.scene=s;bpy.ops.import_scene.gltf(filepath=str(A/'tripo_replica_textured.glb'))
meshes=[o for o in s.objects if o.type=='MESH'];assert len(meshes)==2
materials=set(m for o in meshes for m in o.data.materials)
ims=set(nd.image for m in materials for nd in m.node_tree.nodes if nd.type=='TEX_IMAGE' and nd.image)
assert len(ims)==4, 'Both albedo and normal maps required for both objects.'
report={'status':'rendering','scope':'Standalone textured GLB imported in an isolated Blender scene. No Godot/gameplay tests.',
 'meshes':[],'images':[],'glb_bytes':(A/'tripo_replica_textured.glb').stat().st_size,'views':[]}
for ob in meshes:
    ids=np.empty(len(ob.data.polygons),np.int32);ob.data.polygons.foreach_get('material_index',ids)
    uv=ob.data.uv_layers.active;assert uv
    data=np.empty(len(uv.data)*2,np.float32);uv.data.foreach_get('uv',data)
    assert np.isfinite(data).all() and data.min()>=-.0001 and data.max()<=1.0001
    report['meshes'].append({'name':ob.name,'vertices':len(ob.data.vertices),'triangles':len(ob.data.polygons),'uv_bounds':[float(data.min()),float(data.max())],
        'materials':[{'name':m.name,'faces':int(np.count_nonzero(ids==i))} for i,m in enumerate(ob.data.materials)]})
assert max(len(ob.data.materials) for ob in meshes)>=4, 'Material roles were lost.'
for im in ims:
    pixel0=im.pixels[:4]  # Embedded image buffers load lazily after import.
    assert im.has_data and min(im.size)>=2048 and len(pixel0)==4
    report['images'].append({'name':im.name,'size':list(im.size),'packed':bool(im.packed_file),'colorspace':im.colorspace_settings.name})
for ob in base.objects:
    if ob.type in {'CAMERA','LIGHT'} or ob.name.startswith('DiagnosticFloor'):
        cp=ob.copy();cp.data=ob.data.copy();s.collection.objects.link(cp)
        if cp.type=='CAMERA':s.camera=cp
s.world=base.world.copy();s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=960;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.view_settings.view_transform='AgX';s.view_settings.look=base.view_settings.look
ref=bpy.data.scenes['Tripo_Material_Reference_20261119']
for ob in list(ref.objects):
    if ob.type in {'LIGHT','CAMERA'}:bpy.data.objects.remove(ob,do_unlink=True)
for ob in s.objects:
    if ob.type in {'CAMERA','LIGHT'} or ob.name.startswith('DiagnosticFloor'):
        cp=ob.copy();cp.data=ob.data.copy();ref.collection.objects.link(cp)
        if cp.type=='CAMERA':ref.camera=cp
ref.world=s.world.copy();ref.cycles.samples=48;ref.cycles.use_denoising=True
ref.render.resolution_x=1200;ref.render.resolution_y=960;ref.render.resolution_percentage=100
ref.render.image_settings.file_format='PNG';ref.view_settings.view_transform=s.view_settings.view_transform;ref.view_settings.look=s.view_settings.look
jobs=[(s,0,'textured-final-front.png'),(s,35,'textured-final-three-quarter.png'),(s,-35,'textured-final-left.png'),(s,155,'textured-final-back.png'),
      (ref,0,'textured-reference-front.png'),(ref,35,'textured-reference-three-quarter.png')]
def save():
    (O/'textured-readback.json').write_text(json.dumps(report,indent=2),encoding='utf8')
save()
def step():
    try:
        if not jobs:return None
        scene,angle,file=jobs.pop(0);report['current_view']=file;save();bpy.context.window.scene=scene
        target=Vector((0,0,.21));a=math.radians(angle);cam=scene.camera
        cam.location=target+Vector((math.sin(a)*2.4,-math.cos(a)*2.4,1.05));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(O/file);bpy.ops.render.render(write_still=True);report['views'].append(file)
        if not jobs:
            report['status']='complete';bpy.context.window.scene=s
            a=math.radians(35);s.camera.location=target+Vector((math.sin(a)*2.4,-math.cos(a)*2.4,1.05));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler()
        save();return 1.0 if jobs else None
    except Exception:
        report['status']='failed';report['error']=traceback.format_exc();save();return None
bpy.app.timers.register(step,first_interval=1.0)
print(json.dumps({'status':'dispatched','readback_report':str(O/'textured-readback.json'),'meshes':len(meshes),'images':len(ims)}))
