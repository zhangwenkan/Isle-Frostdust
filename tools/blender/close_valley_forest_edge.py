"""Complete the right-side forest enclosure in the live Blender scene."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf-8').read(),'left_finish_common.py','exec'))
import ast
COL=bpy.data.collections['44_Valley_Forest_Backdrop']
assert not LAYOUT['forest_extension']['valley_enclosed'].get('right_edge_closed')
tree=ast.parse((ROOT/'tools/blender/build_valley_forest_backdrop.py').read_text(encoding='utf-8'))
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name in ['sm2','valley_height']:
        exec(compile(ast.Module(body=[node],type_ignores=[]),'valley_height','exec'))
ground=SCENE.objects['Forest_Valley_Ground']
for v in ground.data.vertices:
    if v.co.x>2.0:v.co.x=2.0+(v.co.x-2.0)*3.0
    v.co.z=valley_height(v.co.x,v.co.y)
for li,loop in enumerate(ground.data.loops):
    p=ground.data.vertices[loop.vertex_index].co
    ground.data.uv_layers[0].data[li].uv=((p.x+50)/54,(min(p.y,38)+4)/40)
ground.data.update()
for row,last,spacing in [(0,10,8.7),(1,12,8.0),(2,13,7.6)]:
    for j in range(1,4):
        for part in [0,1]:
            src=SCENE.objects['Forest_Bamboo_Valley_%d_%02d_%d'%(row,last,part)]
            ob=src.copy();ob.data=src.data.copy();ob.name='Forest_Bamboo_ValleyEdge_%d_%d_%d'%(row,j,part);COL.objects.link(ob)
            for v in ob.data.vertices:
                x,y,z=v.co;nx=x+j*spacing
                v.co=(nx,y,z+valley_height(nx,y)-valley_height(x,y))
            ob.data.update()
            LAYOUT['forest_extension']['groves'].append({'name':ob.name,'band':'valley_far' if row>0 else 'valley_middle'})
LAYOUT['forest_extension']['valley_enclosed']['right_edge_closed']=True
LAYOUT['forest_extension']['valley_enclosed']['bounds']=[-98,28.4,29,92.55]
export('valley-forest-edge')
