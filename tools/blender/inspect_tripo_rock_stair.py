"""Import the user-supplied reference into an isolated diagnostic scene only."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/tripo-rock-stair-analysis';O.mkdir(exist_ok=True)
file=Path('C:/Users/51440/Downloads/bccfc00f-d7ae-4bae-abab-5cc7e8c254e6.glb')
original=bpy.context.window.scene
name='Tripo_Rock_Stair_Diagnostic_20261119'
assert not bpy.data.scenes.get(name),'Existing diagnostic: inspect rather than duplicate.'
s=bpy.data.scenes.new(name);bpy.context.window.scene=s
try:
    bpy.ops.import_scene.gltf(filepath=str(file))
    obs=[o for o in s.objects if o.type=='MESH'];pts=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
    minimum=Vector([min(p[k] for p in pts) for k in range(3)]);maximum=Vector([max(p[k] for p in pts) for k in range(3)]);size=maximum-minimum
    report={'source':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'bounds_blender':[list(minimum),list(maximum)],'size':list(size),'vertices':sum(len(o.data.vertices) for o in obs),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in obs),'materials':[[m.name for m in o.data.materials] for o in obs],'scope':'Isolated imported reference for analysis. No gameplay asset changed.'}
    (O/'tripo-inspection.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
    s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
    s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
    world=bpy.data.worlds.new('TripoDiagnosticWorld');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.19,.22,.25,1);world.node_tree.nodes['Background'].inputs[1].default_value=.7;s.world=world
    # Diagnostic floor and lights live only in this scene and are never exported.
    me=bpy.data.meshes.new('DiagnosticFloor');me.from_pydata([(-3,-3,-.008),(3,-3,-.008),(3,3,-.008),(-3,3,-.008)],[],[(0,1,2,3)]);floor=bpy.data.objects.new('DiagnosticFloor',me);s.collection.objects.link(floor)
    mat=bpy.data.materials.new('DiagnosticFloorMat');mat.diffuse_color=(.17,.19,.21,1);me.materials.append(mat)
    for key,power,pos,scale in [('Key',90,(-1.4,-1.8,2.6),1.4),('Fill',35,(1.8,-.4,1.6),1.8),('Rim',60,(.4,1.6,2.1),1.0)]:
        data=bpy.data.lights.new('TripoDiagnostic'+key,'AREA');data.energy=power;data.shape='DISK';data.size=scale;o=bpy.data.objects.new(data.name,data);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,.20))-o.location).to_track_quat('-Z','Y').to_euler()
    data=bpy.data.cameras.new('TripoDiagnosticCamera');camera=bpy.data.objects.new(data.name,data);s.collection.objects.link(camera);s.camera=camera;data.type='ORTHO';data.ortho_scale=1.45
    center=(minimum+maximum)*.5;center.z=.20
    clay=bpy.data.materials.new('DiagnosticClay');clay.use_nodes=True;clay.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.46,.48,.47,1);clay.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85
    materials={o.name:list(o.data.materials) for o in obs}
    for angle in [-35,0,35,160]:
        a=math.radians(angle);camera.location=center+Vector((math.sin(a)*2.4,-math.cos(a)*2.4,1.05));camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
        s.render.filepath=str(O/('tripo-native-%s.png'%str(angle).replace('-','m')));bpy.ops.render.render(write_still=True)
        if angle in [0,35]:
            for o in obs:
                for i in range(len(o.data.materials)):o.data.materials[i]=clay
            s.render.filepath=str(O/('tripo-clay-%s.png'%angle));bpy.ops.render.render(write_still=True)
            for o in obs:
                for i,m in enumerate(materials[o.name]):o.data.materials[i]=m
    bpy.data.libraries.write(str(O/'diagnostic.blend'),{s},fake_user=True,compress=True)
    print(json.dumps(report))
finally:bpy.context.window.scene=original
