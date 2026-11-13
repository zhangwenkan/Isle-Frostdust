"""Blender MCP only: underwater shelf using the same authored coastline."""
import bpy,bmesh,math,json
from mathutils import Vector
from pathlib import Path
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
col=bpy.data.collections['14_Fish_Landscape']
old=bpy.data.objects.get('Fish_Seabed')
if old:bpy.data.objects.remove(old,do_unlink=True)
def linear(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
def color(s):return tuple(linear(int(s[i:i+2],16)/255) for i in [0,2,4])+(1,)
def mix(a,b,t):return tuple(x*(1-t)+y*t for x,y in zip(a,b))
segments=[]
for name in ['Fish_West_Continuous_Land','Fish_East_Continuous_Land']:
 ob=bpy.data.objects[name]
 points=[ob.matrix_world@v.co for v in ob.data.vertices if v.co.z < -2.74]
 # Last shell ring is ordered in the authoring mesh; extract coastline beneath.
 for a,b in zip(points,points[1:]+points[:1]):segments.append((Vector((a.x,-a.y)),Vector((b.x,-b.y))))
def distance(p,a,b):
 d=b-a;t=max(0,min(1,(p-a).dot(d)/max(d.length_squared,1e-8)));return (p-a-t*d).length
verts=[];faces=[];colors=[]
nx,nz=130,110
for iz in range(nz+1):
 z=-65+iz*1.0
 for ix in range(nx+1):
  x=-60+ix*1.0;p=Vector((x,z));d=min(distance(p,a,b) for a,b in segments)
  y=-3.0-min(13,d*.48)-.1*math.sin(x*.2+z*.1)
  verts.append((x,-z,y))
  c=mix(color('b6b493'),color('738c83'),min(1,d/22));colors.append(c)
for iz in range(nz):
 for ix in range(nx):
  a=iz*(nx+1)+ix;faces.append((a,a+1,a+nx+2,a+nx+1))
me=bpy.data.meshes.new('Fish_Seabed_Mesh');me.from_pydata(verts,[],faces);me.update()
ob=bpy.data.objects.new('Fish_Seabed',me);col.objects.link(ob)
me.materials.append(bpy.data.materials['Fish_Terrain_Painted'])
c=me.color_attributes.new(name='LandscapeColor',type='FLOAT_COLOR',domain='POINT')
for i,r in enumerate(colors):c.data[i].color=r
for p in me.polygons:p.use_smooth=True
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
ob['source']='Blender-authored submerged shelf sampled from current coast; no reference mesh copy'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/island_blender/nameless_island.blend'))
print('Seabed authored',len(verts),'vertices')
