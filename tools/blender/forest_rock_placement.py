"""Move existing road-side stones into two forest pockets, via Blender MCP.

Reference study: Wandering Sword's small solid rocks + painted top/side value
groups. Reuses our own authored angular stones and existing paint, no new pile.
"""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/bamboo-mist-depth-review'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
assert Path(bpy.data.filepath)==R/'assets/island_blender/nameless_island.blend'
arc=bpy.data.collections.get('90_Before_Forest_Rock_Pockets') or bpy.data.collections.new('90_Before_Forest_Rock_Pockets')
if arc.name not in scene.collection.children:scene.collection.children.link(arc)
arc.hide_render=True
floor=scene.objects['PixelForest_Low_Floor'];ft=BVHTree.FromPolygons([floor.matrix_world@v.co for v in floor.data.vertices],[tuple(p.vertices) for p in floor.data.polygons])
def ground(x,y):
    p=ft.ray_cast(Vector((x,y,50)),Vector((0,0,-1)))[0];assert p is not None,(x,y);return p.z
mat=bpy.data.materials.get('ForestRock_Moss')
if mat is None:
    mat=bpy.data.materials['InkSample_Rock_Angular'].copy();mat.name='ForestRock_Moss'
report=[]
for name,x,z,width,depth,height,angle in [('InkSample_Rock_02',-10.85,-5.1,2.25,1.52,1.03,-.18),('InkSample_Rock_03',-9.55,-4.65,1.15,1.05,.62,.36),('InkSample_Rock_04',-4.55,-8.2,1.95,1.5,.81,-.42)]:
    ob=scene.objects[name];saved=bpy.data.objects.get('ForestRockBaseline_'+name)
    if saved is None:
        saved=ob.copy();saved.data=ob.data.copy();saved.name='ForestRockBaseline_'+name;arc.objects.link(saved);saved.hide_set(True);saved.hide_render=True
    ob.data=saved.data.copy();points=[saved.matrix_world@v.co for v in ob.data.vertices]
    lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
    ob.matrix_world=Matrix.Identity(4);rotation=Matrix.Rotation(angle,4,'Z')
    center_y=ground(x,-z);embed=.24
    for v,p in zip(ob.data.vertices,points):
        rel=rotation@Vector((((p.x-lo.x)/(hi.x-lo.x)-.5)*width,((p.y-lo.y)/(hi.y-lo.y)-.5)*depth,0))
        q=(p.z-lo.z)/(hi.z-lo.z)
        h=ground(x+rel.x,-z+rel.y)
        # Bottom follows the soil; upper corners retain the authored slanted cuts.
        v.co=(x+rel.x,-z+rel.y,(h-embed)*(1-q)+(center_y+height-embed)*q)
    me=ob.data;me.update();me.normals_split_custom_set([(0,0,0)]*len(me.loops))
    me.materials.clear();me.materials.append(mat)
    while len(me.uv_layers)>1:me.uv_layers.remove(me.uv_layers[-1])
    uv2=me.uv_layers.new(name='ForestRockHeight')
    for p in me.polygons:
        p.material_index=0;p.use_smooth=False
        for li in p.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co
            uv2.data[li].uv=(max(0,min(1,(v.z-center_y+embed)/height)),0)
    ob['forest_rock_pocket']=True
    bottom=[v.co for v in me.vertices if v.co.z<ground(v.co.x,v.co.y)-.10]
    report.append(dict(name=name,center_godot=[x,center_y,z],width=width,depth=depth,exposed_height=height-embed,embedded_vertices=len(bottom),source='Existing island angular rock, not a copied game rock'))
(O/'rock-placement.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export','exec'))
print('FOREST_ROCKS_MOVED',len(report),report)
