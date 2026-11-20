"""Bake and export the authored material sample inside Blender via MCP.
Reuses prior UVs and preserves prior delivery files. The timer merely divides long operations so MCP can return job acceptance.
Completion is determined from the status file and output readback, not dispatch.
"""
import bpy,math,json,time,traceback,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/tripo-replica-review';A=R/'assets/layered_island/tripo_replica';T=A/'textures_grit';T.mkdir(exist_ok=True)
base=bpy.data.scenes['Tripo_Stone_Grit_Review_20261119']
assert base['revision']=='grit-material-polished-2'
SN='Tripo_Grit_Textured_Delivery_20261119';assert not bpy.data.scenes.get(SN),'Inspect existing bake job; do not restart.'
s=bpy.data.scenes.new(SN);bpy.context.window.scene=s
meshes=[]
for ob in base.objects:
    cp=ob.copy();cp.data=ob.data.copy();s.collection.objects.link(cp)
    if cp.type=='CAMERA':s.camera=cp
    if ob.name in ['Grit_Rocks','Grit_Stairs']:
        cp.name='Grit_Delivery_Rocks' if 'Rocks' in ob.name else 'Grit_Delivery_Stairs';meshes.append(cp)
        face_ids=np.empty(len(cp.data.polygons),dtype=np.int32);cp.data.polygons.foreach_get('material_index',face_ids)
        originals=list(cp.data.materials);cp.data.materials.clear()
        for mat in originals:cp.data.materials.append(mat.copy())
        cp.data.polygons.foreach_set('material_index',face_ids)
        cp['expected_material_faces']=np.bincount(face_ids,minlength=4).tolist()
s.world=base.world.copy();s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=False
s.render.resolution_x=1200;s.render.resolution_y=960;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.view_settings.view_transform='AgX';s.view_settings.look=base.view_settings.look
s.render.bake.margin=12;s.render.bake.use_clear=True;s.render.bake.use_selected_to_active=False
device='CPU'
try:
    pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
    enabled=[]
    for d in pref.devices:d.use=d.type=='OPTIX';enabled.append((d.name,d.type,d.use))
    if any(x[2] for x in enabled):s.cycles.device='GPU';device='OPTIX'
except Exception:pass
state={'status':'running','stage':'prepared','started':time.time(),'device':device,'completed':[],'errors':[]}
status_path=O/'roughness-bake-status.json'
def status(stage):
    state['stage']=stage;state['updated']=time.time();status_path.write_text(json.dumps(state,indent=2),encoding='utf8')
status('prepared')
jobs=[];images={};original_mats={}
def select(ob):
    for x in s.objects:x.select_set(False)
    ob.hide_set(False);ob.select_set(True);bpy.context.view_layer.objects.active=ob
def unwrap(ob):
    status('UV: '+ob.name);select(ob)
    assert ob.data.uv_layers, 'Keep existing authored UV.'
    original_mats[ob.name]=list(ob.data.materials)
    state['completed'].append(ob.name+':UV')
def target_image(ob,kind):
    size=4096 if ob.name=='Grit_Delivery_Rocks' else 2048
    im=bpy.data.images.new(ob.name+'_'+kind,width=size,height=size,alpha=False,float_buffer=False)
    im.colorspace_settings.name='sRGB' if kind=='basecolor' else 'Non-Color'
    im.generated_color=(.15,.13,.10,1) if kind=='basecolor' else (.5,.5,1,1)
    for m in ob.data.materials:
        for nd in m.node_tree.nodes:nd.select=False
        nd=m.node_tree.nodes.new('ShaderNodeTexImage');nd.image=im;nd.name='BAKE_TARGET_'+kind;nd.select=True;m.node_tree.nodes.active=nd
    images[(ob.name,kind)]=im;return im
def save_image(im,ob,kind):
    im.filepath_raw=str(T/(ob.name.lower()+'_'+kind+'.png'));im.file_format='PNG';im.save();im.pack()
def bake_color(ob,kind='basecolor'):
    status(kind+': '+ob.name);select(ob);im=target_image(ob,kind);restore=[]
    for m in ob.data.materials:
        n=m.node_tree.nodes;l=m.node_tree.links;out=next(x for x in n if x.type=='OUTPUT_MATERIAL');bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
        old=out.inputs['Surface'].links[0].from_socket;em=n.new('ShaderNodeEmission')
        inp=bs.inputs['Base Color' if kind=='basecolor' else 'Roughness']
        if inp.is_linked:l.new(inp.links[0].from_socket,em.inputs['Color'])
        elif kind=='basecolor':em.inputs['Color'].default_value=inp.default_value
        else:em.inputs['Color'].default_value=(inp.default_value,)*3+(1,)
        l.new(em.outputs[0],out.inputs['Surface']);restore.append((m,old,out,em))
    try:bpy.ops.object.bake(type='EMIT')
    finally:
        for m,old,out,em in restore:m.node_tree.links.new(old,out.inputs['Surface']);m.node_tree.nodes.remove(em)
    save_image(im,ob,kind);state['completed'].append(ob.name+':'+kind)
def bake_normal(ob):
    status('Normal: '+ob.name);select(ob);im=target_image(ob,'normal')
    bpy.ops.object.bake(type='NORMAL',normal_space='TANGENT');save_image(im,ob,'normal');state['completed'].append(ob.name+':normal')
def replace_materials(ob):
    status('Portable materials: '+ob.name)
    face_ids=np.empty(len(ob.data.polygons),dtype=np.int32);ob.data.polygons.foreach_get('material_index',face_ids)
    mats=[]
    for i,old in enumerate(original_mats[ob.name]):
        m=bpy.data.materials.new(ob.name+'_'+['Stone','Wood','Static_Flame','Hearth'][i]);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF')
        color=n.new('ShaderNodeTexImage');color.image=images[(ob.name,'basecolor')];color.location=(-600,200);l.new(color.outputs['Color'],bs.inputs['Base Color'])
        normal=n.new('ShaderNodeTexImage');normal.image=images[(ob.name,'normal')];normal.location=(-600,-200);nm=n.new('ShaderNodeNormalMap');nm.location=(-300,-200);l.new(normal.outputs['Color'],nm.inputs['Color']);l.new(nm.outputs[0],bs.inputs['Normal'])
        rough=n.new('ShaderNodeTexImage');rough.image=images[(ob.name,'roughness')];rough.location=(-600,-450);l.new(rough.outputs['Color'],bs.inputs['Roughness']);bs.inputs['Specular IOR Level'].default_value=.25 if i==0 else .22
        if i==2:l.new(color.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.35
        m['source']='Authored material bake; source texture colors not transferred.';mats.append(m)
    ob.data.materials.clear()
    for m in mats:ob.data.materials.append(m)
    ob.data.polygons.foreach_set('material_index',face_ids)
    restored=np.empty(len(ob.data.polygons),dtype=np.int32);ob.data.polygons.foreach_get('material_index',restored)
    assert np.bincount(restored,minlength=4).tolist()==list(ob['expected_material_faces'])
    state['completed'].append(ob.name+':portable_materials')
def finish():
    status('Saving and exporting')
    s['revision']='grit-textures-baked-3';s.cycles.samples=48;s.cycles.use_denoising=True
    for x in s.objects:x.select_set(False)
    for ob in meshes:ob.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0]
    for im in images.values():im.pack()
    bpy.data.libraries.write(str(A/'tripo_replica_grit.blend'),{s},fake_user=True,compress=True)
    bpy.ops.export_scene.gltf(filepath=str(A/'tripo_replica_grit.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
    state['completed'].append('blend+glb');state['status']='complete';status('Complete')
for ob in meshes:
    jobs.extend([(unwrap,ob),(bake_color,ob),(bake_normal,ob),(lambda ob:bake_color(ob,'roughness'),ob),(replace_materials,ob)])
jobs.append((finish,None))
def step():
    try:
        if not jobs:return None
        fn,ob=jobs.pop(0)
        bpy.context.window.scene=s
        if ob is None:fn()
        else:fn(ob)
        status(state['stage'])
        return 1.0 if jobs else None
    except Exception:
        state['status']='failed';state['errors'].append(traceback.format_exc());status('Failed');return None
bpy.app.timers.register(step,first_interval=1.0)
print(json.dumps({'status':'dispatched','status_file':str(status_path),'device':device,'meaning':'Not completion; inspect status and output files.'}))
