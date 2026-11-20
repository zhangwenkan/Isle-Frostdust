"""Layered peaks and authored render quad for complete new sample."""
import bpy
from pathlib import Path
exec((Path('D:/自己做着玩的/孤屿霜尘/tools/blender/pixel_cavern_lib.py')).read_text(encoding='utf-8'),globals())
scene=bpy.data.scenes[SCENE];bpy.context.window.scene=scene
assert scene['revision']=='pixel-cavern-foliage-2'
P=palette();back=collection('11_Mountain_Depths');stage=collection('90_Render')

def ridge(name,y,points,depth,material):
    # Profile and foothill are continuous across this ridge. Different depth
    # layers overlap only in the distance, leaving the central cloud valley open.
    n=len(points);vs=[]
    for i,(x,z) in enumerate(points):
        vs.extend([(x,y-depth*.5,-8),(x,y-depth*.32,z*.42),(x+.25*math.sin(i),y,z),(x,y+depth*.55,z*.3),(x,y+depth,-8)])
    fs=[]
    for i in range(n-1):
        for k in range(4):fs.append((i*5+k,(i+1)*5+k,(i+1)*5+k+1,i*5+k+1))
    ob=mesh(name,vs,fs,back,[material]);return ob

ridge('Mountain_Far_Ridge',88,[(-88,13),(-68,19),(-53,22),(-44,29),(-39,27),(-33,31),(-27,23),(-20,21),(-10,25),(-2,24),(7,31),(11,27),(19,25),(28,29),(39,24),(52,27),(65,20),(90,17)],25,P['mountain_far'])
ridge('Mountain_Mid_Left',55,[(-55,8),(-36,13),(-28,21),(-25,20),(-21,25),(-18,23),(-14,14),(-7,9),(0,6)],15,P['mountain_mid'])
ridge('Mountain_Mid_Right',63,[(0,5),(7,12),(14,25),(17,27),(20,24),(25,15),(29,18),(36,22),(42,16),(55,14),(74,6)],17,P['mountain_mid'])
ridge('Mountain_Near_Pillar',35,[(-5,-2),(-1,4),(1.3,12),(2.8,16.8),(3.7,15.6),(4.6,18.2),(5.7,16.5),(6.5,17.3),(7.5,13.6),(8.6,6),(13,2),(16,-2)],7,P['mountain_near'])
ridge('Mountain_Near_Right',43,[(17,-3),(20,7),(23,14),(25,16),(26.5,19),(28,17.5),(31,11),(35,10),(40,15),(44,12),(51,4),(57,-2)],10,P['mountain_near'])

# Shader quad authored in Blender, then placed in clip space by Godot.
mesh('Render_Pixel_Edges',[(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)],[(0,1,2,3)],stage,[P['stone']])
scene['revision']='pixel-cavern-complete-3'
export_scene(scene['revision'])
