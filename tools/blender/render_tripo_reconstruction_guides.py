"""Measured orthographic guides for faithful reconstruction, through Blender MCP."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/tripo-replica-review';OUT.mkdir(exist_ok=True)
s=bpy.data.scenes['Tripo_Coast_Processing_20261119'];old=bpy.context.window.scene;bpy.context.window.scene=s
assert not s.get('guide_rendered'),'Already rendered guides.'
review=bpy.data.collections.new('Tripo_Reconstruction_Reference_Views');s.collection.children.link(review)
base=bpy.data.scenes['Tripo_Rock_Stair_Diagnostic_20261119']
for o in base.objects:
    if o.type in {'CAMERA','LIGHT'}:
        cp=o.copy();cp.data=o.data.copy();review.objects.link(cp)
        if cp.type=='CAMERA':s.camera=cp
s.world=base.world.copy();s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.film_transparent=True
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
cam=s.camera;cam.data.ortho_scale=1.20;target=Vector((0,0,.24));views=[]
for name,position,up in [('front',(0,-2.4,.24),'Z'),('top',(0,0,2.5),'Y'),('right',(2.4,0,.24),'Z')]:
    cam.location=position;cam.rotation_euler=(target-cam.location).to_track_quat('-Z',up).to_euler()
    s.render.filepath=str(OUT/('guide-'+name+'.png'));bpy.ops.render.render(write_still=True)
    views.append({'name':name,'camera':position,'target':list(target),'ortho_scale':1.2})
s['guide_rendered']=True
(OUT/'guide-views.json').write_text(json.dumps(views,indent=2),encoding='utf8')
bpy.context.window.scene=old
print('Three measured orthographic reference views rendered. No reference geometry changed.')
