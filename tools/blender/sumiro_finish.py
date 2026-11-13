"""Blender MCP finish: remove buried old cliff ribs and seat roots on actual terrain."""
import bpy,bmesh,math,json,random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/sumiro-style-review'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
def G(p):return Vector((p[0],-p[2],p[1]))
land=[]
for name in ['Fish_West_Continuous_Land','Fish_East_Continuous_Land']:
    ob=scene.objects[name];east='East' in name;count=(53 if east else 101)*26
    baseline=bpy.data.meshes[name+'_Before_Sumiro']
    kd=KDTree(count)
    for i in range(count):
        p=baseline.vertices[i].co;kd.insert(Vector((p.x,p.y,0)),i)
    kd.balance()
    for v in list(ob.data.vertices)[count:]:
        p=baseline.vertices[v.index].co.copy();z=-p.y
        # Keep the exact rim and the underwater coast. Retire the old protruding ribs
        # behind the imported continuous face; the replacement owns the silhouette.
        x=p.x;nearest=kd.find(Vector((p.x,p.y,0)))[1];top=baseline.vertices[nearest].co.z
        f=max(0,min(1,(top-p.z)/.42));f=f*f*(3-2*f)
        underwater=max(0,min(1,(p.z+2.4)/1.2));underwater=underwater*underwater*(3-2*underwater)
        front=max(0,min(1,(z+.1)/1.5))
        p.y+=2.0*f*underwater*front;v.co=p
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
    # Read the actual top mesh for root and grass anchoring.
    ps=[v.co.copy() for v in ob.data.vertices];polys=[tuple(p.vertices) for p in ob.data.polygons if all(i<count for i in p.vertices)]
    land.append(BVHTree.FromPolygons(ps,polys,all_triangles=False))
def ground(x,z):
    hits=[t.ray_cast(G((x,30,z)),Vector((0,0,-1)),100)[0] for t in land]
    hits=[p for p in hits if p is not None]
    return max(hits,key=lambda p:p.z) if hits else None
report=[]
for info in json.loads((OUT/'authoring.json').read_text())['pine_placement']:
    label=info['label'];obs=[o for o in bpy.data.collections['29_Sumiro_Pines'].objects if o.name.startswith('Sumiro_Pine_'+label+'_')]
    x,y,z=info['root'];x=max(-18.7,min(25.4,x));p=ground(x,z)
    if p is None:
        for testz in [-3.5,-2.8,-2.0,-1.5]:
            p=ground(x,testz)
            if p is not None:z=testz;break
    assert p is not None,label
    shift=p-G(info['root'])+Vector((0,0,-.12))
    for ob in obs:
        # First two groups were seated before an earlier off-coast root failed.
        previous=Vector(ob.get('sumiro_root_fit',list(shift) if label in ['West_01','West_02'] else (0,0,0)))
        for v in ob.data.vertices:v.co+=shift-previous
        ob['sumiro_root_fit']=list(shift)
    report.append({'label':label,'anchor':list(p),'shift':list(shift)})

# The served Sumiro grass uses curved, tapered blade ribbons. Recreate the same
# length/rise/droop recipe here in Blender, not as generated Godot geometry.
col=bpy.data.collections.get('31_Sumiro_Grass') or bpy.data.collections.new('31_Sumiro_Grass')
if col.name not in scene.collection.children:scene.collection.children.link(col)
for ob in list(col.objects):bpy.data.objects.remove(ob,do_unlink=True)
mat=bpy.data.materials.get('Sumiro_Grass') or bpy.data.materials.new('Sumiro_Grass');mat.use_nodes=True
mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(1,1,1,1)
specs=json.loads((OUT/'source/assets/env_pines/placement.json').read_text())['grass']
anchors=[(-17.8,-2.0),(-14.0,1.9),(-11.8,-2.8),(-7.5,2.0),(-3.2,-2.8),(.2,1.5),(17.0,-1.5),(20.6,2.0),(24.2,-2.3)]
rng=random.Random(19071)
for index,(x,z) in enumerate(anchors):
    spec=specs[[8,5,2,6,3,7,8,5,4][index]];verts=[];faces=[];colors=[];weights=[];uv=[]
    for blade in range(spec['count']):
        r=spec['spread']*math.sqrt(rng.random());a=rng.random()*math.tau
        root=ground(x+math.cos(a)*r,z+math.sin(a)*r*.7)
        if root is None:continue
        az=math.radians(spec['az'][0]+(rng.random()+rng.random()-1)*spec['az'][1]);d=Vector((math.sin(az),-math.cos(az),0));side=Vector((-d.y,d.x,0))
        length=rng.uniform(*spec['length']);rise=rng.uniform(*spec['rise']);droop=rng.uniform(*spec['droop']);width=spec['width']*rng.uniform(.7,1.3)
        c=rng.choice(spec['col']);tone=tuple(v/255*rng.uniform(.82,1.12) for v in c)+(1,)
        start=len(verts)
        for j in range(7):
            t=j/6;along=(1-rise*.4)*t+droop*t*t*.9;up=rise*t-droop*t*t*.75;w=width*(1-t)*(1-t*.2)+.004
            for sign in [-1,1]:verts.append(root+(d*along+Vector((0,0,up)))*length+side*sign*w);colors.append(tone);weights.append(t*t);uv.append(((sign+1)/2,t))
            if j:faces.append((start+(j-1)*2,start+(j-1)*2+1,start+j*2+1,start+j*2))
    me=bpy.data.meshes.new('Sumiro_Grass_%02d'%index);me.from_pydata(verts,[],faces);me.materials.append(mat);me.update()
    a=me.uv_layers.new(name='UVMap');b=me.uv_layers.new(name='Wind');ca=me.color_attributes.new(name='GrassColor',type='FLOAT_COLOR',domain='POINT');ca.data.foreach_set('color',[v for c in colors for v in c])
    for loop in me.loops:a.data[loop.index].uv=uv[loop.vertex_index];b.data[loop.index].uv=(weights[loop.vertex_index],0)
    ob=bpy.data.objects.new(me.name,me);col.objects.link(ob)
(OUT/'root-seating.json').write_text(json.dumps(report,indent=2),encoding='utf8')
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
print('SUMIRO_FINISHED',len(report),'root placements, grass',len(col.objects))
