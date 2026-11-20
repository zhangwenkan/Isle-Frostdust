"""Final composition color and depth pass on the new scene. Blender MCP."""
import bpy
from pathlib import Path
exec((Path('D:/自己做着玩的/孤屿霜尘/tools/blender/pixel_cavern_lib.py')).read_text(encoding='utf-8'),globals())
scene=bpy.data.scenes[SCENE];bpy.context.window.scene=scene
assert scene['revision']=='pixel-cavern-organic-detail-5'
P=palette();back=collection('11_Mountain_Depths');sea=collection('06_Shore')

def recolor(key,h):
    v=[int(h[i:i+2],16)/255 for i in (0,2,4)];v=[x/12.92 if x<.04045 else ((x+.055)/1.055)**2.4 for x in v]
    m=P[key];m.diffuse_color=(*v,1);m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*v,1);m['source_srgb']=h
for key,h in [('stone','87958c'),('stone_light','a1ad9a'),('stone_shadow','62786f'),('grass','72884b'),('grass_light','99a95e'),('leaf','5a814b'),('leaf_lit','84a35b'),('bamboo','748c4e'),('sand','b4aa85')]:recolor(key,h)

# The right route is a rocky ledge, not a wide empty lawn in front of the cave.
for ob in scene.objects:
    if ob.type!='MESH':continue
    if ob.name in ['Rock_Right_Continuous_Core','Soil_Right_Root_Bank','Grass_Right_Terrace'] or ob.name.startswith(('Rock_Cliff_RBridge','Rock_Cliff_RFront','Rock_Cliff_REdge','Plant_Moss_Rock_Cliff_RBridge','Plant_Moss_Rock_Cliff_RFront','Plant_Moss_Rock_Cliff_REdge')):
        for v in ob.data.vertices:
            if v.co.y<1.0:v.co.y=1.0+(v.co.y-1.0)*.65
    if ob.name.startswith(('Foliage_Tree','Shadow_Foliage_Tree')):
        coords=[v.co for v in ob.data.vertices];c=sum(coords,Vector())/len(coords)
        for v in ob.data.vertices:
            q=v.co-c;v.co=Vector((q.x*1.05,q.y,q.z*.78))+c

# Replace the simple near peak profile with a volumetric karst neck, narrowing
# in unequal terraces. Its foot remains concealed by the distant cloud volume.
old=scene.objects['Mountain_Near_Pillar'];archive=bpy.data.collections.new('PCC_Archive_Triangular_Near_Peak')
for c in list(old.users_collection):c.objects.unlink(old)
archive.objects.link(old);old['pixel_cavern']=False
levels=[(-5,7.0,4.2,0),(2,4.9,3.5,-.6),(5.5,3.2,2.6,.15),(8.2,2.7,2.3,.55),(10.2,1.8,1.8,.15),(11.4,1.95,1.55,.36),(12.8,1.1,1.3,.15),(13.8,.7,.8,.25)]
vs=[];sides=12
for li,(z,rx,ry,offset) in enumerate(levels):
    for j in range(sides):
        a=j*math.tau/sides;scale=1+.08*math.sin(j*2.4+li*.4)
        vs.append((4.7+offset+rx*math.cos(a)*scale,35+ry*math.sin(a)*scale,z+.22*math.sin(j*2.1+li)))
fs=[]
for li in range(len(levels)-1):
    for j in range(sides):fs.append((li*sides+j,li*sides+(j+1)%sides,(li+1)*sides+(j+1)%sides,(li+1)*sides+j))
fs.append(tuple(range((len(levels)-1)*sides,len(levels)*sides)))
mesh('Mountain_Karst_Near',vs,fs,back,[P['mountain_near']])

# Interrupted foam arcs at the sand-water boundary, authored as thin geometry.
curve=[(-18.2,-9.1),(-17.3,-10.8),(-15.8,-12.1),(-13.7,-12.9),(-11.1,-13.2),(-8.9,-12.8),(-7,-12.15),(-5.4,-11.3),(-4.1,-10.25)]
vs=[];fs=[]
for i in range(len(curve)-1):
    a=Vector(curve[i]);b=Vector(curve[i+1]);d=(b-a).normalized();p=Vector((-d.y,d.x))
    for j in range(5):
        if (i+j)%4==1:continue
        c=a.lerp(b,(j+.15)/5);e=a.lerp(b,(j+.85)/5);w=.07+.045*math.sin(i+j*2)**2;k=len(vs)
        vs.extend([(c.x,c.y,.028),(e.x,e.y,.028),(e.x+p.x*w,e.y+p.y*w,.028),(c.x+p.x*w*.8,c.y+p.y*w*.8,.028)])
        fs.append((k,k+1,k+2,k+3))
mesh('Foam_Shore_Broken_Arcs',vs,fs,sea,[P['foam']])
scene['revision']='pixel-cavern-color-depth-6';export_scene(scene['revision'])
