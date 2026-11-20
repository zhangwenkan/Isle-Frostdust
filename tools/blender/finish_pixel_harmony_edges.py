"""Final grass fringe and asymmetric bamboo fans, through Blender MCP."""
import bpy,math,random,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
exec((ROOT/'tools/blender/pixel_cavern_lib.py').read_text(encoding='utf-8'),globals())
s=bpy.data.scenes[SCENE];bpy.context.window.scene=s
assert s['revision']=='pixel-cavern-vegetation-harmony-10'
live=collection('15_Composed_Vegetation');P=palette();r=random.Random(1782)
def bvh(obs):
    v=[];f=[]
    for o in obs:
        k=len(v);v.extend(o.matrix_world@q.co for q in o.data.vertices);f.extend(tuple(k+i for i in p.vertices) for p in o.data.polygons)
    return BVHTree.FromPolygons(v,f)
obs=[o for o in s.objects if o.type=='MESH' and o.get('pixel_cavern')]
floors=bvh([o for o in obs if o.name.startswith('Grass_')]);blocks=bvh([o for o in obs if o.name.startswith(('Path_','Step_','Rock_Cliff_','Rock_Cave_'))])
verts=[];faces=[];roots=[];weights=[];phases=[];norms=[]
for ix in range(72):
    for iy in range(8):
        x=-17.1+ix*.22+r.uniform(-.06,.06);y=-5.18+iy*.21+r.uniform(-.05,.05)
        if y>=-3.61:continue
        p,n,_,_=floors.ray_cast(Vector((x,y,18)),Vector((0,0,-1)),22)
        if p is None or n.z<.8:continue
        q,_,_,_=blocks.ray_cast(Vector((x,y,18)),Vector((0,0,-1)),22)
        if q is not None and q.z>p.z-.06:continue
        f=.5+.27*math.sin(x*.76+y*.31)+.20*math.cos(y*1.04-x*.23);t=max(0,min(1,(f-.36)/.38));t=t*t*(3-2*t)
        dx=.27*.76*math.cos(x*.76+y*.31)+.20*.23*math.sin(y*1.04-x*.23);dy=.27*.31*math.cos(x*.76+y*.31)-.20*1.04*math.sin(y*1.04-x*.23)
        normal=Vector((-dx*2.1,-dy*2.1,1)).normalized()
        for j in range(4):
            origin=p+Vector((r.uniform(-.04,.04),r.uniform(-.04,.04),-.018));a=j*1.83+x*.7;d=Vector((math.cos(a)*.16,math.sin(a)*.16,1)).normalized();side=d.cross(Vector((.1,-1,.5))).normalized();h=(.15+.23*t)*r.uniform(.85,1.12);w=r.uniform(.032,.048);k=len(verts)
            for u,spread in ((0,.12),(.24,.82),(.50,1),(.77,.63),(1,0)):
                c=origin+d*h*u+Vector((.025*u*u,0,0))
                for sign in (-1,1):
                    verts.append(tuple(c+side*w*spread*sign));roots.append(origin);weights.append(u*u);phases.append((x*.17+y*.21)%1);norms.append(tuple(normal))
            for z in range(4):
                a=k+2*z;faces.extend(((a,a+1,a+3),(a,a+3,a+2)))
if verts:
    o=mesh('LiveGrass_Shore_Fringe',verts,faces,live,[P['grass']]);me=o.data;uv=me.uv_layers[0];uv2=me.uv_layers.new(name='Wind');aa=[];bb=[]
    for l in me.loops:
        i=l.vertex_index;p=roots[i];aa.extend((p.x,1+p.y));bb.extend((p.z,1-weights[i]))
    uv.data.foreach_set('uv',aa);uv2.data.foreach_set('uv',bb)
    colors=me.color_attributes.new(name='WindPivot',type='FLOAT_COLOR',domain='POINT');colors.data.foreach_set('color',[v for i in range(len(verts)) for v in (math.sqrt(weights[i]),phases[i],0,1)]);me.color_attributes.active_color=colors
    me.normals_split_custom_set_from_vertices(norms);o['wind_data_layout']='uv_xz_uv2_y_weight_color_leaf_phase'
# Break paired, comb-like rhythm inside each fan while retaining its direction.
for o in obs:
    if not o.name.startswith('LiveBambooLeaf_'):continue
    me=o.data;norms=[tuple(n.vector) for n in me.corner_normals]
    for k in range(0,len(me.vertices),10):
        origin=(me.vertices[k].co+me.vertices[k+1].co)*.5
        phase=origin.x*1.7+origin.y*2.3+origin.z*.8+(k//10)*.9
        turn=.16*math.sin(phase);scale=.94+.14*math.sin(phase*.57)
        rot=Matrix.Rotation(turn,3,'Z')
        for j in range(10):
            q=me.vertices[k+j].co-origin;u=(j//2)/4
            me.vertices[k+j].co=origin+(rot@q)*scale+Vector((0,0,.055*math.sin(phase)*u*u))
    me.update();me.normals_split_custom_set(norms)
s['revision']='pixel-cavern-vegetation-harmony-11'
bpy.data.libraries.write(str(OUT/'pixel_cavern_coast.blend'),{s},fake_user=True,compress=True)
print(json.dumps({'revision':s['revision'],'shore_blades':len(verts)//10}))
