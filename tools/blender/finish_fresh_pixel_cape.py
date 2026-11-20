"""Color and fracture pass on freshly authored sample; run via Blender MCP."""
import bpy,math,json,bmesh
from pathlib import Path
from mathutils import Vector
root=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Fresh_Pixel_Cape'];bpy.context.window.scene=scene
assert scene['revision']=='fresh-cape-color-study-2'

def color(name,h):
    m=bpy.data.materials['Fresh_'+name];rgb=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    c=[v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    m.diffuse_color=(*c,1);m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1)
    m['srgb']='#'+h
color('Rock_Base','9b9e94');color('Rock_Pale','b1b4a0');color('Rock_Cool','788b89');color('Rock_Dark','506966')
color('Step','b6b6a1');color('Step_Variant','a5ab9b')
color('Grass_Main','81924e');color('Grass_Light','9eab61');color('Grass_Shade','5c7848')

# Refine the NEW crown facets into cut stone planes; retain broad calm faces.
for ob in bpy.data.collections['Fresh_02_Rock_Faces'].objects:
    for mod in ob.modifiers:
        if mod.type=='DISPLACE':mod.strength=.16;mod.texture.noise_scale=.78
        if mod.type=='DECIMATE':mod.ratio=.52
    if 'Lower' in ob.name or 'Bed' in ob.name:
        for v in ob.data.vertices:
            v.co.x+=.15*math.sin(v.co.z*1.2+v.co.y*.5)

# A few narrow wedge-shaped fractures are actual dark recess accents, aligned
# with the main oblique bedding, not repeated marks across the entire surface.
col=bpy.data.collections['Fresh_02_Rock_Faces']
dark=bpy.data.materials['Fresh_Rock_Dark']
light=bpy.data.materials['Fresh_Rock_Pale']
accents=[
('A',[(-9.4,-3.60,2.28),(-8.6,-3.56,2.17),(-7.8,-3.30,2.20),(-8.65,-3.57,2.12)]),
('B',[(-6.1,-3.79,2.31),(-5.55,-3.75,2.20),(-4.85,-3.52,2.23),(-5.55,-3.76,2.16)]),
('C',[(-3.30,-3.87,1.40),(-2.95,-3.80,1.31),(-2.58,-3.62,1.29),(-2.95,-3.81,1.26)]),
]
for name,vs in accents:
    data=bpy.data.meshes.new('Fresh_Fracture_'+name);data.from_pydata(vs,[],[(0,1,3),(1,2,3)]);data.update()
    ob=bpy.data.objects.new('Fresh_Sparse_Fracture_'+name,data);col.objects.link(ob);data.materials.append(dark)
    ob['fresh_sample']=True;ob['authored_from']='local fracture accent on new sample'

# Broaden bamboo leaves enough to survive the final screen pixel size; remove
# some crossed fans, keeping distinct airy group silhouettes.
bcol=bpy.data.collections['Fresh_05_Bamboo']
for ob in list(bcol.objects):
    if 'CounterFan' in ob.name:
        stem=int(ob.name.split('_')[1]);branch=int(ob.name.rsplit('_',1)[1])
        if (stem+branch)%3==0:
            bpy.data.objects.remove(ob,do_unlink=True);continue
    if 'Fan' in ob.name:
        for i in range(0,len(ob.data.vertices),5):
            verts=ob.data.vertices
            mid=(verts[i+1].co+verts[i+4].co)*.5
            verts[i+1].co=mid+(verts[i+1].co-mid)*1.55
            verts[i+4].co=mid+(verts[i+4].co-mid)*1.55
    if '_Stem' in ob.name:
        # Slight bend through intermediate segments would be useful later;
        # avoid exaggerated thick near-camera trunks in this first sample.
        pass

# Clean the factory-startup scene only, keeping the new editable scene.
default=bpy.data.scenes.get('Scene')
if default and set(o.name for o in default.objects)=={'Cube','Camera','Light'}:
    for ob in list(default.objects):bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.scenes.remove(default)
scene['revision']='fresh-cape-color-study-3'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/fresh_pixel_cape/fresh_pixel_cape.blend'))
print(json.dumps({'revision':scene['revision'],'scenes':[s.name for s in bpy.data.scenes]}))
