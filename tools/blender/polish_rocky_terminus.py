"""Refine registered floor material, continuous cliff corners and planted grass."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf8').read(),'left_finish_common.py','exec'))
from mathutils.bvhtree import BVHTree
rc=LAYOUT['reference_cape'];assert rc.get('rocky_terminus') and not rc['rocky_terminus'].get('polish')
COL=bpy.data.collections['52_Forest_Rocky_Terminus']
ground=SCENE.objects['WALK_Forest_Ground']
material=bpy.data.materials.new('Forest_Terminus_Floor');material.use_nodes=True
image=bpy.data.images.load(str(OUT/'rocky_terminus/floor.png'),check_existing=True);image.reload();image.pack()
p=material.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.97
n=material.node_tree.nodes.new('ShaderNodeTexImage');n.image=image;material.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
ground.data.materials.append(material);index=len(ground.data.materials)-1;count=0
for poly in ground.data.polygons:
    if poly.center.x<-54.00001:poly.material_index=index;count+=1

MATS['side']=[m for m in bpy.data.materials if m.name.startswith('RC_cape_side')][-1]
border=[Vector(p) for p in rc['rocky_terminus']['outline']]
middle=[];low=[]
for i,p in enumerate(border):
    prev=border[max(0,i-1)];nxt=border[min(len(border)-1,i+1)];d=nxt-prev;n=Vector((d.y,-d.x,0)).normalized()
    offset=.08+.04*math.sin(i*1.7)
    middle.append(Vector((p.x+n.x*offset,p.y+n.y*offset,p.z*.48)))
    low.append(Vector((p.x+n.x*(offset+.09),p.y+n.y*(offset+.09),-.65)))
b=Mesh('Cape_Terminus_Bedrock_Closed_Corners')
for i,(p,q) in enumerate(zip(border,border[1:])):
    if p.y>8.7 and q.y>8.7 and p.x<-64 and q.x>-63:continue
    b.part([p,q,middle[i+1],middle[i]],[(0,1,2,3)],'side')
    b.part([middle[i],middle[i+1],low[i+1],low[i]],[(0,1,2,3)],'side')
new=b.build();old=SCENE.objects['Cape_Terminus_Bedrock'];old.data=new.data;bpy.data.objects.remove(new,do_unlink=True)

def tree(o):return BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
trees=[tree(SCENE.objects[n]) for n in ['WALK_Forest_Ground']+rc['cliff_masses']]
def support(x,y):
    hs=[t.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))[0] for t in trees]
    return max(h.z for h in hs if h is not None)
grass=Mesh('Forest_Grass_Terminus_Bent_Clumps')
for i,(x,y,z) in enumerate(rc['rocky_terminus']['grass_roots']):
    for j,(dx,dy,h,angle) in enumerate([(-.19,.04,.28,-.9),(-.09,-.06,.37,-.4),(.04,.04,.41,.3),(.17,.02,.31,.8),(.10,-.07,.25,1.2)]):
        cx=x+dx;cy=y+dy;zz=support(cx,cy)+.012
        direction=Vector((math.cos(angle),math.sin(angle),0));side=Vector((-direction.y,direction.x,0))
        root=Vector((cx,cy,zz));mid=root+direction*.065+Vector((0,0,h*.6));tip=root+direction*.20+Vector((0,0,h))
        grass.part([root-side*.045,root+side*.045,mid+side*.030,mid-side*.030,tip],[(0,1,2,3),(3,2,4)],'grass_blade',weights=[0,0,.55,.55,1])
new=grass.build();old=SCENE.objects['Forest_Grass_Terminus'];old.data=new.data;bpy.data.objects.remove(new,do_unlink=True)
rc['rocky_terminus']['polish']={'registered_new_floor_material':material.name,'painted_polygons':count,'shared_cliff_corners':len(middle),'grass':'16 rooted clumps of five tapered bent strips'}
export('forest-rocky-terminus-pass2')
