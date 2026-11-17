"""Second form/UV pass on the existing Blender MCP-authored sample."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path('D:/自己做着玩的/孤屿霜尘');out=root/'assets/layered_island'
scene=bpy.data.scenes['Layered_Island_20261116'];bpy.context.window.scene=scene
assert scene.objects.get('Space_Continuous_Cliff')
assert not scene.get('spatial_form_pass2',False),'Already refined'
upper=scene.objects['Land_Relief']
tree=BVHTree.FromPolygons([upper.matrix_world@v.co for v in upper.data.vertices],[list(p.vertices) for p in upper.data.polygons])
def ground(x,y):
    if y<4:return 2.85+.72*max(0,min(1,(y-2.7)/1.24))
    hit=tree.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))
    assert hit[0] is not None,(x,y)
    return hit[0].z
for im in bpy.data.images:
    if im.source=='FILE' and '/spatial_textures/' in im.filepath.replace('\\','/'):
        im.reload();im.pack()
# The cliff's upper ring actually meets its top; the previous 10 cm air gap is gone.
cliff=scene.objects['Space_Continuous_Cliff'];n=15
for v in cliff.data.vertices:
    if v.index>=3*n:v.co.z+=.10
cliff.data.update()
# Independent angular shoulders emerge from the body at unequal depth/height.
for name,cx,cy,shift_y,sx in [('West',-12.5,-2.15,-.70,1.18),('Main',-9.3,-2.55,-.72,1.08),('Stair',-6.9,-1.95,-.45,1.0),('Bridge',-1.7,-1.05,-.52,1.06)]:
    ob=scene.objects['Space_Rock_'+name]
    for v in ob.data.vertices:
        p=v.co;ring=v.index//6;k=v.index%6
        p.x=cx+(p.x-cx)*sx+(0.10 if ring==1 and k in [0,4] else 0)
        p.y+=shift_y*(.65 if ring==2 else 1.)
        if ring==2:
            p.z+=[.21,.04,-.10,.17,.12,.22][k]
            p.x+=.13 if name in ['Main','Stair'] else -.08
        elif ring==1:p.z+=.14 if k in [0,1,5] else -.12
    ob.data.update()
# UV density is suited to a surface, not 1.5 metre mirrored wallpaper.
for ob in scene.objects:
    if ob.type!='MESH' or not any(c.name=='40_Spatial_Foundation' for c in ob.users_collection):continue
    if not ob.data.uv_layers:continue
    uv=ob.data.uv_layers[0]
    for poly in ob.data.polygons:
        for li in poly.loop_indices:
            p=ob.data.vertices[ob.data.loops[li].vertex_index].co
            if ob.name in ['WALK_Space_Beach','Space_Beach_Edge']:
                uv.data[li].uv=((p.x+13.0)/12.4,(p.y+7.2)/5.2)
            elif ob.name=='WALK_Space_Ground':uv.data[li].uv=(p.x*.26,p.y*.34)
            elif ob.name.startswith('Space_Rock') or ob.name=='Space_Continuous_Cliff':
                normal=poly.normal
                if abs(normal.z)>.6:uv.data[li].uv=(p.x*.24,p.y*.30)
                elif abs(normal.x)>abs(normal.y):uv.data[li].uv=(p.y*.30,p.z*.31)
                else:uv.data[li].uv=(p.x*.25,p.z*.30)
            elif ob.name=='WALK_Space_Stairs':uv.data[li].uv=(p.x*.34,p.y*.7 if abs(poly.normal.z)>.65 else p.z*.55)
# Move two clumps off the walk corridor; all roots are raycast onto the upper terrain.
for idx,newx,newy in [(7,-10.3,6.4),(11,-14.6,9.8)]:
    ob=scene.objects['Space_Bamboo_%02d'%idx]
    oldx=[-8.0,-11.9][[7,11].index(idx)];oldy=[6.2,9.6][[7,11].index(idx)]
    delta=Vector((newx-oldx,newy-oldy,ground(newx,newy)-ground(oldx,oldy)))
    for v in ob.data.vertices:v.co+=delta
    ob.data.update()
scene['spatial_form_pass2']=True
live=[o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
bpy.data.libraries.write(str(out/'layered_island.blend'),{scene},fake_user=True,compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in live:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=cliff
bpy.ops.export_scene.gltf(filepath=str(out/'layered_island.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
print('Refined cliff junction, exposed shoulders, UV density and two plant roots')
