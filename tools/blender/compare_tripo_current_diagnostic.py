"""Analysis only: duplicate meshes into a temporary Blender scene via MCP.

No game source is saved, exported, transformed or assigned new materials.
Current floor/base copies are clipped only to frame the local stair assembly.
"""
import bpy, bmesh, math, json, hashlib
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path('D:/自己做着玩的/孤屿霜尘')
OUT=ROOT/'artifacts/tripo-rock-stair-analysis'
original=bpy.context.window.scene
main=bpy.data.scenes['Layered_Island_20261116']
ref=bpy.data.scenes.get('Tripo_Rock_Stair_Diagnostic_20261119')
assert ref, 'Read existing imported diagnostic; do not reimport blindly.'
name='Rock_Stair_Comparative_Diagnostic_20261119'
assert not bpy.data.scenes.get(name), 'Diagnostic already exists; inspect saved outputs.'

def fingerprint(scene):
    h=hashlib.sha256()
    for o in sorted(scene.objects,key=lambda x:x.name):
        h.update(o.name.encode());h.update(str(tuple(o.matrix_world)).encode())
        if o.type=='MESH':
            for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
            for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
            for uv in o.data.uv_layers:
                for d in uv.data:h.update(str(tuple(d.uv)).encode())
            h.update(str([m.name if m else None for m in o.data.materials]).encode())
    return h.hexdigest()

before=fingerprint(main)
files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
       for p in [ROOT/'assets/layered_island/layered_island.blend',ROOT/'assets/layered_island/layered_island.glb',ROOT/'assets/layered_island/layout.json']}
s=bpy.data.scenes.new(name);bpy.context.window.scene=s
try:
    s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True
    s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
    s.view_settings.look='AgX - Medium High Contrast'
    world=bpy.data.worlds.new(name+'_World');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.13,.14,1)
    world.node_tree.nodes['Background'].inputs[1].default_value=.5;s.world=world
    clay=bpy.data.materials.new(name+'_Clay');clay.use_nodes=True
    bsdf=clay.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value=(.27,.29,.30,1);bsdf.inputs['Roughness'].default_value=.85
    groups={};reports={}
    own_names=['WALK_Forest_Ground','Cape_Terminus_Bedrock','WALK_Cape_Stairs','Cape_Stair_Support']
    own_names += ['Cape_Strict_Rock_'+x for x in ['Sea_West','Sea_Front','Stair_Left','Stair_Right','Root_West','Toe_West','Toe_West_Inset','Toe_Right','Toe_Right_Low']]
    source_groups={'current':[main.objects[n] for n in own_names],
                   'tripo':[o for o in ref.objects if o.type=='MESH' and o.name!='DiagnosticFloor']}
    for key,source in source_groups.items():
        copies=[]
        for src in source:
            o=src.copy();o.data=src.data.copy();o.name=name+'_'+key+'_'+src.name
            s.collection.objects.link(o);o.hide_render=False;o.hide_set(False)
            # Transform the diagnostic copy's vertices to world space only.
            for v in o.data.vertices:v.co=src.matrix_world@v.co
            o.matrix_world=Matrix.Identity(4)
            if key=='current' and src.name in ['WALK_Forest_Ground','Cape_Terminus_Bedrock']:
                bm=bmesh.new();bm.from_mesh(o.data)
                for point,normal in [((-69,0,0),(-1,0,0)),((-59,0,0),(1,0,0)),((0,2,0),(0,-1,0)),((0,17,0),(0,1,0))]:
                    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=point,plane_no=normal,clear_outer=True,clear_inner=False)
                bm.to_mesh(o.data);bm.free()
            copies.append(o)
        pts=[v.co.copy() for o in copies for v in o.data.vertices]
        lo=Vector([min(p[k] for p in pts) for k in range(3)]);hi=Vector([max(p[k] for p in pts) for k in range(3)])
        center=(lo+hi)*.5;center.z=lo.z
        # Equal overall assembly height. Relative width/depth and all internal
        # proportions are preserved; this is not a claim of real metre scale.
        scale=.481292724609375/(hi.z-lo.z)
        rot=Matrix.Rotation(-math.atan2(.8,4.8) if key=='current' else 0,4,'Z')
        for o in copies:
            for v in o.data.vertices:v.co=rot@((v.co-center)*scale)
            o.data.materials.clear();o.data.materials.append(clay)
            for p in o.data.polygons:p.material_index=0
            o.data.update()
        groups[key]=copies
        reports[key]={'source_objects':[o.name for o in source], 'source_bounds':[list(lo),list(hi)],'uniform_diagnostic_scale':scale,'source_size':list(hi-lo)}
    me=bpy.data.meshes.new(name+'_Floor');me.from_pydata([(-3,-3,-.012),(3,-3,-.012),(3,3,-.012),(-3,3,-.012)],[],[(0,1,2,3)])
    floor=bpy.data.objects.new(me.name,me);s.collection.objects.link(floor)
    fm=bpy.data.materials.new(name+'_Floor_Mat');fm.use_nodes=True
    fm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.19,.20,.21,1)
    me.materials.append(fm)
    for key,power,pos,size in [('Key',65,(-2,-3,4),3),('Fill',25,(3,-1,3),3),('Rim',35,(1,3,3),2)]:
        d=bpy.data.lights.new(name+'_'+key,'AREA');d.energy=power;d.size=size
        o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=pos
        o.rotation_euler=(Vector((0,0,.2))-o.location).to_track_quat('-Z','Y').to_euler()
    d=bpy.data.cameras.new(name+'_Camera');cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam);s.camera=cam
    d.type='ORTHO';d.ortho_scale=1.65
    for angle in [0,35]:
        a=math.radians(angle);target=Vector((0,0,.23))
        cam.location=target+Vector((math.sin(a)*2.4,-math.cos(a)*2.4,1.05))
        cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        for key in ['tripo','current']:
            for k,obs in groups.items():
                for o in obs:o.hide_render=k!=key
            s.render.filepath=str(OUT/(key+'-matched-clay-'+str(angle)+'.png'))
            bpy.ops.render.render(write_still=True)
    after=fingerprint(main)
    assert before==after, 'Game scene was changed during analysis.'
    assert all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in files.items())
    report={'scope':'Diagnostic mesh copies only; game scene/file unchanged. No walk or passage tests.',
            'normalization':'Equal total assembly height; uniform scale preserves internal proportions. Current staircase axis rotated toward the reference front. Not calibrated real world dimensions.',
            'current_floor_clipping':'Copies of ground/bedrock clipped to x [-69,-59], y [2,17] for local framing; cut edges are diagnostic boundaries.',
            'lighting_camera':'Same clay material, world, three area lights, orthographic scale and elevation for both. Source normals retained.',
            'groups':reports,'game_scene_sha256_before':before,'game_scene_sha256_after':after,'protected_file_sha256':files}
    (OUT/'matched-diagnostic.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    bpy.data.libraries.write(str(OUT/'matched-diagnostic.blend'),{s},fake_user=True,compress=True)
    print(json.dumps({'outputs':4,'game_scene_unchanged':before==after,'report':str(OUT/'matched-diagnostic.json')}))
finally:
    bpy.context.window.scene=original
