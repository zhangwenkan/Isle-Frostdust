"""Ground the grouped understory and keep its bent stems continuous, through MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
import ast
rc=LAYOUT['reference_cape'];rw=rc['rocky_terminus']['reference_rework'];assert not rw.get('fern_settled')
COL=bpy.data.collections[rw['collection']]
MATS['relief_top']=bpy.data.materials['ForestCoast_relief_top'];MATS['relief_side']=bpy.data.materials['ForestCoast_relief_side']
# The broad cliff shares a base with these three inclined fracture shoulders.
# They are embedded in the core rather than an independent perimeter of pillars.
src=ast.parse((ROOT/'tools/blender/polish_terminus_reference_relief.py').read_text(encoding='utf8'))
for node in src.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='shapes' for t in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'rock-footprints','exec'))
    if isinstance(node,ast.FunctionDef) and node.name=='angular':exec(compile(ast.Module(body=[node],type_ignores=[]),'rock-planes','exec'))
for i,(name,x,y,w,d,base,h,angle) in enumerate([('Cape_Terminus_Cliff_Shoulder_Near',-59.6,6.20,3.8,2.1,2.35,2.8,-.21),('Cape_Terminus_Cliff_Shoulder_Return',-56.75,3.35,3.45,2.25,1.6,2.8,.15),('Cape_Terminus_Cliff_Shoulder_West',-66.95,10.9,2.0,2.65,1.2,3.15,.23)]):
    angular(name,x,y,w,d,base,h,angle,(.12,.10),(.28,-.24),i);rc['cliff_masses'].append(name)
rw['embedded_fracture_shoulders']=3
def tree(o):return BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
trees=[tree(SCENE.objects[n]) for n in ['WALK_Forest_Ground']+rc['cliff_masses']]
def support(x,y):
    hits=[t.ray_cast(Vector((x,y,40)),Vector((0,0,-1)))[0] for t in trees]
    return max(p.z for p in hits if p is not None)
# Broader clustered grass silhouettes, grounded again after changing each tuft.
g=SCENE.objects['Forest_Grass_Terminus'];centers=[(-65.5,15.7),(-64.8,17.6),(-63.0,17.9),(-61.8,17.8),(-60.2,16.1),(-58.1,16.2),(-57.1,15.2),(-61.0,14.7),(-59.6,14.9),(-58.0,14.7),(-57.0,14.8),(-55.6,14.85),(-60.7,10.8),(-59.2,10.3),(-58.2,9.2),(-57.1,8.7),(-55.9,8.0),(-60.7,7.6),(-58.6,6.9),(-56.9,6.0),(-65.8,10.5)]
for start in range(0,len(g.data.vertices),5):
    cx,cy=centers[start//(5*13)];root=(g.data.vertices[start].co+g.data.vertices[start+1].co)*.5
    target=Vector((cx+(root.x-cx)*1.28,cy+(root.y-cy)*1.28,0));target.z=support(target.x,target.y)+.012
    for k in range(5):
        p=g.data.vertices[start+k].co-root;g.data.vertices[start+k].co=target+Vector((p.x*1.16,p.y*1.16,p.z*1.16))
g.data.update()
ferns=Mesh('Forest_Grass_Terminus_Ferns_Rooted');roots=[]
for i,(x,y) in enumerate([(-65.0,15.8),(-63.1,15.9),(-60.3,16.2),(-58.35,16.4),(-59.4,8.5),(-57.7,7.8),(-61.0,10.6)]):
    z=support(x,y)+.012;root=Vector((x,y,z));roots.append([x,y,z])
    for j in range(5):
        a=j*math.tau/5+i*.61;direction=Vector((math.cos(a),math.sin(a),0));side=Vector((-direction.y,direction.x,0));length=.48+.12*(j%3)
        pts=[root+direction*length*t+Vector((0,0,.34*math.sin(t*math.pi*.7))) for t in [0,.2,.4,.6,.8,1]]
        tube(ferns,pts,[.015,.012,.010,.008,.006,.003],'grass_blade',sides=5,weights=[0,.2,.4,.6,.8,1])
        for k in range(4):
            t=(k+1)/5;c=pts[k+1];w=.15*(1-t*.65)
            for sign in [-1,1]:
                end=c+side*w*sign+direction*.13+Vector((0,0,-.03));mid=(c+end)*.5+Vector((0,0,.025))
                ferns.part([c,mid-direction*.042,end,mid+direction*.043],[(0,1,2),(0,2,3)],'grass_blade',weights=[t*.4,t*.65,t,t*.65],colors=[(.84,1.02,.65,1)]*4)
new=ferns.build();old=SCENE.objects['Forest_Grass_Terminus_Ferns'];old.data=new.data;bpy.data.objects.remove(new,do_unlink=True)
rw['fern_settled']={'roots':roots,'stems':'connected from fixed roots to bent pinnate fronds','geometry':'Blender MCP'}
export('reference-forest-coast-relief-review')
