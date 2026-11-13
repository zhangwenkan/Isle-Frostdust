"""Author the western bamboo valley in Blender through MCP.
Existing island, route, bamboo wind data and camera are not rebuilt.
"""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/bamboo-valley-review'
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
NAME='30_West_Bamboo_Valley'
def original_objects():
    return [o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') or c.name==NAME for c in o.users_collection)]
def digest(o):
    m=o.data
    return hashlib.sha256(json.dumps({'v':[list(v.co) for v in m.vertices],'p':[list(p.vertices) for p in m.polygons],'n':[list(n.vector) for n in m.corner_normals],'uv':[[list(d.uv) for d in u.data] for u in m.uv_layers],'matrix':[list(r) for r in o.matrix_world]}).encode()).hexdigest()
before={o.name:digest(o) for o in original_objects()}
collection=bpy.data.collections.get(NAME)
if collection:
    for o in list(collection.objects):bpy.data.objects.remove(o,do_unlink=True)
else:
    collection=bpy.data.collections.new(NAME);scene.collection.children.link(collection)

def color(h):
    def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
    return tuple(linear(int(h[i:i+2],16)/255) for i in [0,2,4])+(1,)
def material(name,h):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color(h);bs.inputs['Roughness'].default_value=1
    vc=m.node_tree.nodes.get('ValleyColor') or m.node_tree.nodes.new('ShaderNodeVertexColor');vc.name='ValleyColor';vc.layer_name='ValleyColor'
    m.node_tree.links.new(vc.outputs['Color'],bs.inputs['Base Color'])
    return m
stone=material('InkValley_Rock','738776');turf=material('InkValley_Turf','74834f');bedrock=material('InkValley_Bedrock','798477')
land=scene.objects['Fish_West_Continuous_Land']
landtree=BVHTree.FromPolygons([land.matrix_world@v.co for v in land.data.vertices],[tuple(p.vertices) for p in land.data.polygons])
def ground(x,z):
    p=landtree.ray_cast(Vector((x,-z,40)),Vector((0,0,-1)))[0]
    return p.z if p else None
def smooth(a,b,x):
    t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def mesh_object(name,vertices,faces,material_ids,vertex_colors):
    me=bpy.data.meshes.new(name);me.from_pydata([(p[0],-p[2],p[1]) for p in vertices],[],faces);me.materials.append(stone);me.materials.append(turf);me.materials.append(bedrock);me.update()
    ob=bpy.data.objects.new(name,me);collection.objects.link(ob)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    ca=me.color_attributes.new(name='ValleyColor',type='FLOAT_COLOR',domain='CORNER')
    uv=me.uv_layers.new(name='ValleyWorldUV')
    for p,mi in zip(me.polygons,material_ids):
        p.material_index=mi;p.use_smooth=True
        for li in p.loop_indices:
            vi=me.loops[li].vertex_index
            if mi!=1:
                pnt=vertices[vi];shade=.5+.5*math.sin(pnt[0]*.40+pnt[1]*.19)
                a=color('798477');b=color('8a9282');ca.data[li].color=tuple(a[k]*(1-shade)+b[k]*shade for k in range(4))
            else:ca.data[li].color=vertex_colors[vi]
            point=vertices[vi]
            if mi==0:
                cell=p.index//2;ci=cell//(rows-1);cj=cell%(rows-1)
                uv.data[li].uv=(vi//rows-ci,vi%rows-cj)
            else:uv.data[li].uv=(point[0]*.14,point[1]*.14 if mi==2 else point[2]*.14)
    me.color_attributes.active_color=ca;me.color_attributes.render_color_index=0
    me.update()
    # Keep the structural plane breaks while softening triangulation within each band.
    auto=[n.vector.copy() for n in me.corner_normals]
    me.normals_split_custom_set([tuple(auto[li].lerp(p.normal,.30 if p.material_index==0 else .07).normalized()) for p in me.polygons for li in p.loop_indices])
    return ob

# Hand-arranged stations: alternating outward shoulders and deeper recessed bays.
# x, nearest toe z, first bench height, upper crest height, bend into the valley.
stations=[
    (-16.9,-4.7,0.0,6.4,-.2),(-15.5,-4.6,.7,10.6,.6),
    (-13.7,-4.6,1.5,12.2,1.0),(-12.2,-4.7,1.7,12.9,.4),
    (-10.6,-4.5,1.0,12.0,-.9),(-8.9,-4.8,.7,10.8,-1.6),
    (-7.0,-4.4,1.7,11.6,.4),(-5.3,-4.4,2.0,12.3,1.4),
    (-3.5,-4.5,.8,10.7,-.7),(-1.8,-4.3,1.2,10.6,-.9),
    (-.2,-4.0,1.8,10.2,.5),(1.1,-4.1,1.1,8.8,.7),
    (2.2,-4.4,.35,6.4,.2),(3.1,-5.2,0.0,2.5,-.3)]
vertices=[];cols=[]
for i,(x,z,bench,crest,bend) in enumerate(stations):
    toe=ground(x,z)
    if toe is None:toe=max(.2,4.7-(x+17)*.15)
    # At the narrowing east end the old rear cliff is already below the sea.
    # Extend the inland bank at tread height, retaining its buried joining toe.
    base=max(toe,ground(x,-2.0) or .2)
    crest=max(base+.55,crest-2.0*smooth(-16.9,-13.7,x)*(1.0-smooth(1.1,3.1,x)))
    # Two rock scarps separated by a real turf shelf, not overlapping flat backdrops.
    end_weight=smooth(-16.9,-13.8,x)*(1-smooth(.0,3.1,x))
    bench=base+bench*.65
    cross=[(0,toe-.24,1),(-.8,base+.25*end_weight,1),(-1.65,bench,0),
           (-3.5,bench+.20*end_weight,1),(-5.2,base+.15*end_weight,1),
           (-7.1,base+.30*end_weight,1),(-8.6,base+1.6*end_weight,1),
           (-10.1,max(base+.5,crest-2.0),0),(-11.8,crest-.7,1),
           (-14.0,crest,1),(-16.0,crest-.65,1),(-20.0,max(.1,crest-4.3),1)]
    for j,(dz,y,grass) in enumerate(cross):
        # The outermost shoulders taper into the existing island at the cape/bridge ends.
        spread=smooth(3,9,j)*.48
        px=-6.8+(x+6.8)*(1+spread)+(j/11)*(.6*math.sin(i*.55)+(.35 if i<3 else -.65))
        pz=z+dz+bend*math.sin(j*.48)+.22*math.sin(i*1.9+j*.7)*end_weight
        y+=.22*math.sin(i*1.6+j*1.3)*end_weight if j>0 else 0
        # The western base sweeps inland under the cape, keeping the seaward
        # opening unobstructed while the taller wooded bank spreads behind it.
        px=max(px,-15.55-.30*(y+5)+.035*(pz+20))
        vertices.append((px,y,pz))
        if grass:
            palette=['788653','718152','7e8b59','6a7b50']
        else:palette=['7a8b7a','708474','829080','768574']
        cols.append(color(palette[(i//2+j//3)%len(palette)]))
faces=[];mids=[];rows=12
for i in range(len(stations)-1):
    for j in range(rows-1):
        a=i*rows+j;b=(i+1)*rows+j;c=b+1;d=a+1
        # Grass ledges alternate with tall, inclined faces.
        mi=0 if (j==1 and i in [2,3,6,7,10]) or (j==6 and i in [3,4,7,10]) else 1
        tris=[(a,b,d),(b,c,d)] if (i+j)%2 else [(a,b,c),(a,c,d)]
        faces.extend(tris);mids.extend([mi,mi])
# Close end profiles and rear below sea level so no light leaks reveal a hollow shell.
perimeter=list(range(rows))+[i*rows+rows-1 for i in range(1,len(stations))]+[(len(stations)-1)*rows+j for j in range(rows-2,-1,-1)]+[i*rows for i in range(len(stations)-2,0,-1)]
rings=[perimeter]
for level in [1,2]:
    ring=[]
    for k,vi in enumerate(perimeter):
        p=vertices[vi];y=p[1]*.54-1.15 if level==1 else -5.0
        outward=Vector((p[0]+6.8,p[2]+12.0)).normalized()
        width=(.28+.32*math.sin(k*.73)) if level==1 else .65
        x=p[0]+outward.x*width;z=p[2]+outward.y*width
        x=max(x,-15.55-.30*(y+5)+.035*(z+20))
        ring.append(len(vertices));vertices.append((x,y,z));cols.append(color('798477'))
    rings.append(ring)
for upper,lower in zip(rings,rings[1:]):
    for k,a in enumerate(upper):
        kn=(k+1)%len(upper);b=upper[kn];c=lower[kn];d=lower[k]
        faces.extend([(a,b,c),(a,c,d)]);mids.extend([2,2])
faces.append(tuple(reversed(rings[-1])));mids.append(2)
valley=mesh_object('InkValley_Connected_Terraces',vertices,faces,mids,cols)
tree=BVHTree.FromPolygons([valley.matrix_world@v.co for v in valley.data.vertices],[tuple(p.vertices) for p in valley.data.polygons])

# A few bamboo groups on the deeper shelves make the back read as woodland depth.
# Copies retain authored leaf silhouettes, UV2 wind weights and original color layers.
bamboo_specs=[(-16.0,-18.0,.90,.22),(-12.2,-18.0,.92,-.26),(-8.8,-18.5,.90,.43),(-5.5,-17.4,.90,-.38),(-2.5,-18.2,.86,.19),(1.3,-16.1,.83,-.31),
              (-14.0,-10.5,.90,.31),(-10.8,-11.0,1.0,-.43),(-7.5,-10.6,1.04,.51),(-4.2,-10.2,.95,-.23),(-.7,-10.0,.92,.40),
              (-13.0,-14.3,.9,-.55),(-6.3,-14.4,1.0,.24),(.8,-13.8,.88,-.45)]
bamboos=[]
for idx,(x,z,scale,angle) in enumerate(bamboo_specs):
    src=scene.objects['InkSample_Bamboo_%02d'%(3+idx%3)]
    points=[src.matrix_world@v.co for v in src.data.vertices]
    center=Vector(((min(p.x for p in points)+max(p.x for p in points))*.5,(min(p.y for p in points)+max(p.y for p in points))*.5,min(p.z for p in points)))
    hit=tree.ray_cast(Vector((x,-z,40)),Vector((0,0,-1)))[0]
    assert hit is not None
    ob=src.copy();ob.data=src.data.copy();ob.name='InkValley_Bamboo_%02d'%idx;collection.objects.link(ob)
    ob.matrix_world=Matrix.Translation(hit-Vector((0,0,.10)))@Matrix.Rotation(angle,4,'Z')@Matrix.Scale(scale,4)@Matrix.Translation(-center)@src.matrix_world
    # Conform intact bamboo culms and their branch/leaf pieces to actual shelf heights.
    roots=[Vector((r[0],-r[2],r[1])) for r in json.loads(src['root_positions_godot'])]
    offsets=[];new_roots=[]
    for root in roots:
        p=ob.matrix_world@root
        support=tree.ray_cast(Vector((p.x,p.y,40)),Vector((0,0,-1)))[0]
        assert support is not None,(ob.name,tuple(p))
        offsets.append(support.z-.07-p.z);new_roots.append((p.x,support.z-.07,-p.y))
    adjacency=[[] for v in ob.data.vertices]
    for e in ob.data.edges:
        a,b=e.vertices;adjacency[a].append(b);adjacency[b].append(a)
    remaining=set(range(len(adjacency)));inverse=ob.matrix_world.inverted();component_start={}
    while remaining:
        seed=remaining.pop();component=[seed];stack=[seed]
        while stack:
            for v in adjacency[stack.pop()]:
                if v in remaining:remaining.remove(v);stack.append(v);component.append(v)
        start=min(component)
        for vi in component:component_start[vi]=start
    # The source author appends complete plants in root order. Find each first
    # root tube, then translate its full vertex span so branches never tear.
    starts=[]
    for ri,root in enumerate(roots):
        nearest=min(ob.data.vertices,key=lambda v:(v.co-root).length_squared)
        assert (nearest.co-root).length<.12
        starts.append((component_start[nearest.index],ri))
    starts.sort();assert len({s[0] for s in starts})==len(roots)
    for k,(start,ri) in enumerate(starts):
        end=starts[k+1][0] if k+1<len(starts) else len(ob.data.vertices)
        shift=inverse.to_3x3()@Vector((0,0,offsets[ri]))
        for vi in range(start,end):ob.data.vertices[vi].co+=shift
    ob['root_positions_godot']=json.dumps(new_roots);ob.data.update()
    bamboos.append({'name':ob.name,'x':x,'z':z,'base_y':hit.z,'scale':scale,'root_embed_m':.07,'roots':new_roots,'uv_layers':[u.name for u in ob.data.uv_layers]})

# Sparse rooted grass tufts on shelves. Long blade shapes match the current ink sample.
gv=[];gf=[];gc=[];gu=[];gw=[];root_samples=[]
for i in range(1,len(stations)-2):
    for j in [2,3,7,8]:
        anchor=Vector(vertices[i*rows+j]);nextp=Vector(vertices[(i+1)*rows+j])
        for k in range(3):
            p=anchor.lerp(nextp,(k+.35)/3);x=p.x;z=p.z-.14-.22*math.sin(i+k)
            hit=tree.ray_cast(Vector((x,-z,40)),Vector((0,0,-1)))[0]
            if hit is None:continue
            root_samples.append(tuple(hit))
            for b in range(5):
                root=hit+Vector(((b-2)*.048,.028*math.sin(b+i),-.018))
                tip=root+Vector(((b-2)*.07+.05*math.sin(i),.07*math.cos(i+b),.18+.15*(.5+.5*math.sin(i+b*2))))
                mid=root.lerp(tip,.48);w=.024
                pts=[root,mid+Vector((-w,0,0)),mid+Vector((w,0,0)),tip];start=len(gv)
                gv.extend(pts);gf.extend([(start,start+1,start+2),(start+1,start+3,start+2)])
                gc.extend([color(['637747','71814e','596e47'][i%3])]*4);gu.extend([(.5,0),(0,.48),(1,.48),(.5,1)]);gw.extend([0,.48,.48,1])
me=bpy.data.meshes.new('InkValley_Ledge_Grass');me.from_pydata(gv,[],gf);me.materials.append(bpy.data.materials['InkSample_Grass']);me.update()
ob=bpy.data.objects.new('InkValley_Ledge_Grass',me);collection.objects.link(ob)
ca=me.color_attributes.new(name='InkColor',type='FLOAT_COLOR',domain='POINT');ca.data.foreach_set('color',[v for c in gc for v in c]);me.color_attributes.active_color=ca
uv=me.uv_layers.new(name='BrushUV');wind=me.uv_layers.new(name='WindWeight')
for li in me.loops:uv.data[li.index].uv=gu[li.vertex_index];wind.data[li.index].uv=(gw[li.vertex_index],0)

after={o.name:digest(o) for o in original_objects()};assert before==after,'Existing assets unexpectedly changed'
report={'original_unchanged_meshes':len(before),'new_collection':NAME,'new_objects':[o.name for o in collection.objects],'terrace_vertices':len(vertices),'terrace_faces':len(faces),'bamboo':bamboos,'grass_clusters':len(root_samples),'authoring':'Blender MCP; two connected rock scarps, uneven turf shelves, open bridge mouth'}
(OUT/'blender-authoring.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
mp=ROOT/'assets/island_blender/asset_manifest.json';m=json.loads(mp.read_text(encoding='utf-8'));m['revision']='Western bamboo valley terraces; distant ridges revealed at bridge'
if '../../artifacts/bamboo-valley-review/README.md' not in m['source_manifests']:m['source_manifests'].append('../../artifacts/bamboo-valley-review/README.md')
mp.write_text(json.dumps(m,indent=2),encoding='utf-8')
print('BAMBOO_VALLEY_EXPORTED',json.dumps(report))
