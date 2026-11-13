"""Authored in the live Blender scene through Blender MCP only.

Sparse individual near culms, a short creek separation, and a continuous rising wooded bank.
Reruns restore this pass's baseline; they do not re-run earlier cape remapping.
"""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/forest-visibility-review'
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
def collection(name):
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in scene.collection.children:scene.collection.children.link(c)
    return c
archive=collection('90_Before_Forest_Visibility');archive.hide_render=True
current=collection('32_Open_Bamboo_Creek_Valley')
for ob in list(current.objects):bpy.data.objects.remove(ob,do_unlink=True)
def active():return [o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
def signature(o):
    h=hashlib.sha256()
    for v in o.data.vertices:h.update(str(tuple(v.co)).encode())
    for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
    for uv in o.data.uv_layers:
        for d in uv.data:h.update(str(tuple(d.uv)).encode())
    h.update(str(o.matrix_world).encode());return h.hexdigest()
if not (O/'baseline-signatures.json').exists():
    (O/'baseline-signatures.json').write_text(json.dumps({o.name:signature(o) for o in active()},indent=2),encoding='utf-8')
def stash(o):
    for c in list(o.users_collection):c.objects.unlink(o)
    archive.objects.link(o);o.hide_set(True);o.hide_render=True
for ob in list(active()):
    if ob.name.startswith('ValleyDepth_') or ob.name in ['Depth_Bamboo_Main_02','Depth_Bamboo_Main_06','InkSample_Bamboo_03','InkSample_Bamboo_04','InkSample_Bamboo_05']:stash(ob)
def baseline(o):
    name='VisibilityBaseline_'+o.name
    saved=bpy.data.objects.get(name)
    if saved is None:
        saved=o.copy();saved.data=o.data.copy();saved.name=name;archive.objects.link(saved);saved.hide_set(True);saved.hide_render=True
    return saved
def restore(o):
    saved=baseline(o);o.data=saved.data.copy();o.matrix_world=saved.matrix_world.copy();return saved
def clamp(t):return max(0.,min(1.,t))
def smooth(a,b,v):
    t=clamp((v-a)/(b-a));return t*t*(3-2*t)
def G(p):return Vector((p[0],-p[2],p[1]))
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def height(t,x,z):
    p=t.ray_cast(G((x,60,z)),Vector((0,0,-1)))[0];return p.z if p is not None else None
land=scene.objects['Fish_West_Continuous_Land'];base=restore(land);old_tree=tree(base)
def road_y(x):
    return height(old_tree,x,0) or (3.1-.14*(x+6))
def lower_west(x,y):
    weight=smooth(-15.1,-12.2,x)*(1-smooth(.5,4.0,x))
    return y-max(0,y-1.5)*.40*weight
def reshape(p):
    x,y,z=p.x,p.z,-p.y
    w=smooth(-15.1,-12.7,x)*(1-smooth(.5,3.4,x))*smooth(1.15,3.2,-z)*smooth(-.5,1.8,y)
    target=road_y(x)-.08-.30*max(0.,-z-2.0)
    p.z-=max(0.,y-target)*w
    p.z=lower_west(x,p.z)
    return p
for v in land.data.vertices:v.co=land.matrix_world.inverted()@reshape(land.matrix_world@v.co)
land.data.normals_split_custom_set([(0,0,0)]*len(land.data.loops));land.data.update();land_tree=tree(land)
changed=['Fish_West_Continuous_Land']
# Reattach only affected vegetation/rocks, using the same vertical terrain delta.
for ob in list(active()):
    if not ob.name.startswith(('Coast_Low_Grass_','InkSample_Path_Grass','InkSample_Rock_','Cliff_Fern_West_','Cliff_Fractures_West')):continue
    source=baseline(ob);points=[source.matrix_world@v.co for v in source.data.vertices]
    if not any(-15.2<p.x<4.0 for p in points):continue
    restore(ob);inv=ob.matrix_world.inverted()
    if ob.name=='Cliff_Fractures_West':
        for v,p in zip(ob.data.vertices,points):v.co=inv@reshape(p.copy())
    elif 'Rock' in ob.name:
        x=sum(p.x for p in points)/len(points);z=-sum(p.y for p in points)/len(points)
        a=height(old_tree,x,z);b=height(land_tree,x,z)
        delta=(b-a) if a is not None and b is not None else 0
        ob.location.z+=delta
    else:
        adj=[[] for _ in ob.data.vertices]
        for e in ob.data.edges:a,b=e.vertices;adj[a].append(b);adj[b].append(a)
        remaining=set(range(len(adj)))
        while remaining:
            seed=remaining.pop();stack=[seed];ids=[]
            while stack:
                vi=stack.pop();ids.append(vi)
                for k in adj[vi]:
                    if k in remaining:remaining.remove(k);stack.append(k)
            foot=min((points[k] for k in ids),key=lambda p:p.z)
            a=height(old_tree,foot.x,-foot.y);b=height(land_tree,foot.x,-foot.y)
            delta=(b-a) if a is not None and b is not None else 0
            for k in ids:ob.data.vertices[k].co=inv@(points[k]+Vector((0,0,delta)))
        ob.data.update()
    changed.append(ob.name)
def color(h):
    def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
    return tuple(lin(int(h[i:i+2],16)/255) for i in [0,2,4])+(1,)
def mat(name,h):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color(h);bs.inputs['Roughness'].default_value=1
    vc=m.node_tree.nodes.get('ForestPigment') or m.node_tree.nodes.new('ShaderNodeVertexColor');vc.name='ForestPigment';vc.layer_name='ForestPigment'
    m.node_tree.links.new(vc.outputs['Color'],bs.inputs['Base Color']);return m
mats=[mat('ForestValley_Turf','6d8254'),mat('ForestValley_Rock','777d69'),mat('ForestValley_Stream','315f59'),mat('ForestValley_Fall','89b3a1'),mat('ForestValley_Foam','b7cbb9')]
def mesh(name,verts,faces,ids,layer=0):
    me=bpy.data.meshes.new(name);me.from_pydata([G(p) for p in verts],[],faces);me.update()
    for m in mats:me.materials.append(m)
    ob=bpy.data.objects.new(name,me);current.objects.link(ob)
    for p,mi in zip(me.polygons,ids):p.material_index=mi
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
    ca=me.color_attributes.new(name='ForestPigment',type='FLOAT_COLOR',domain='CORNER');uv=me.uv_layers.new(name='SurfaceUV')
    for p in me.polygons:
        mi=p.material_index;p.use_smooth=True
        for li in p.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co;x,y,z=v.x,v.z,-v.y
            tone=(.96+.045*math.sin(x*.32+z*.19))
            palette=['728457','7f8272','325e59','89b3a1','b7cbb9']
            if mi==0 and z<-19:palette[0]='78886a'
            if mi==1:
                # Authored large plane tones: warm top ledges and cooler clefts.
                palette[1]='9c9a83' if p.normal.z>.58 else '737b70'
                tone*=.91+.12*max(0,p.normal.dot(Vector((-.35,-.6,.65)).normalized()))
            c=color(palette[mi]);ca.data[li].color=tuple(v*tone for v in c[:3])+(1,)
            uv.data[li].uv=(x*.17,z*.17 if mi!=1 else y*.21)
    if not name.endswith('Creek'):
        normals=[n.vector.copy() for n in me.corner_normals]
        me.normals_split_custom_set([tuple(normals[li].lerp(p.normal,.38 if p.material_index==1 else .04).normalized()) for p in me.polygons for li in p.loop_indices])
    me.color_attributes.active_color=ca;ob['forest_visibility_layer']=layer
    return ob
def grid_mesh(name,rows,ids,layer=0,closed=True):
    width=len(rows[0]);verts=[p for row in rows for p in row];faces=[];material=[]
    for j in range(len(rows)-1):
        for i in range(width-1):
            a=j*width+i;b=a+width
            faces.extend([(a,a+1,b+1),(a,b+1,b)]);mi=ids(j,i)
            material.extend([mi,mi])
    if closed:
        perimeter=list(range(width))+[j*width+width-1 for j in range(1,len(rows))]+[(len(rows)-1)*width+i for i in range(width-2,-1,-1)]+[j*width for j in range(len(rows)-2,0,-1)]
        lower=[]
        for index in perimeter:
            x,y,z=verts[index];lower.append(len(verts));verts.append((x,-3.8,z))
        for k,index in enumerate(perimeter):
            q=(k+1)%len(perimeter);faces.append((index,lower[k],lower[q],perimeter[q]));material.append(1)
        faces.append(tuple(reversed(lower)));material.append(1)
    return mesh(name,verts,faces,material,layer)

# A compact, connected valley: a sinuous creek at its foot, with oblique
# ridges rising continuously away from the player. No separate rock props.
def bend(x):return 1.00*math.sin((x+12)*.35)-.013*max(x+6,0)**2
def near_z(x):return -5.8+bend(x)+.65*math.sin(x*.67+.3)+smooth(-1,3.8,x)*1.7
def far_z(x):return near_z(x)-(3.3+1.3*math.sin((x+10)*.39))-1.2*math.exp(-((x+10)/3.8)**2)
def creek_level(x):return 4.75-.85*smooth(-14.5,2.4,x)+1.30*(1-smooth(-15.3,-11.6,x))
xs=[-15.3+i*(17.7/30) for i in range(31)]
near_rows=[]
for j in range(7):
    row=[]
    for x in xs:
        back=near_z(x);front=-2.55+smooth(.5,3.8,x)*.8;t=j/6
        z=front+(back-front)*t
        z+=.40*math.sin(x*.83+.6)*math.sin(t*math.pi)
        start=height(land_tree,x,front)
        start=start if start is not None else lower_west(x,road_y(x))-.1
        water=creek_level(x)
        y=start+(water-.14-start)*smooth(0,1,t)
        y+=.23*math.exp(-((t-.84)/.13)**2)
        y+=.28*math.sin(x*.63+1.2)*math.sin(t*math.pi)
        h=height(land_tree,x,z)
        if j<=1 and h is not None:y=max(y,h+.055)
        row.append((x,y,z))
    near_rows.append(row)
near=grid_mesh('ForestVisibility_Near_Bank',near_rows,lambda j,i:0)
near_uv=near.data.uv_layers.new(name='ValleySurface')
for p in near.data.polygons:
    for li in p.loop_indices:
        v=near.data.vertices[near.data.loops[li].vertex_index]
        exposure=1-smooth(.66,.96,abs(v.normal.z))
        pocket=.5+.5*math.sin(v.co.x*.92+v.co.y*.7)
        near_uv.data[li].uv=(clamp(exposure*(.92-.28*pocket)),0)
near_normals=[n.vector.copy() for n in near.data.corner_normals]
near.data.normals_split_custom_set([tuple(near_normals[li].lerp(p.normal,.55 if near_uv.data[li].uv.x>.5 else .06).normalized()) for p in near.data.polygons for li in p.loop_indices])
stream_rows=[];bed_rows=[]
for j in range(9):
    t=j/8
    stream_rows.append([(x,creek_level(x),near_z(x)+(far_z(x)-near_z(x))*t) for x in xs])
    bed_rows.append([(x,creek_level(x)-.13-.72*math.sin(t*math.pi),near_z(x)+(far_z(x)-near_z(x))*t) for x in xs])
stream=grid_mesh('ForestVisibility_Creek',stream_rows,lambda j,i:2,closed=False)
bed=grid_mesh('ForestVisibility_Creek_Bed',bed_rows,lambda j,i:1)
# UV0 carries physical along-channel distance and bank-to-bank position, so
# flow follows the authored bend instead of sliding across world X/Z.
for li in stream.data.loops:
    vi=li.vertex_index;stream.data.uv_layers[0].data[li.index].uv=((xs[vi%len(xs)]+15.3),vi//len(xs)/8)

# The elevated creek turns over an authored bedrock lip behind the west end
# of the bridge. All sheet/support/foam geometry is made in this Blender pass.
out_x=xs[-1];out_level=creek_level(out_x)
out_near=near_z(out_x);out_far=far_z(out_x)
out_center=(out_near+out_far)*.5;out_width=out_near-out_far
fall_path=[(0,0),(.20,-.015),(.40,-.09),(.59,-.27),(.76,-.59),(.87,-1.10),(.95,-1.68),(1.02,-2.30),(1.10,-2.98),(1.22,-3.50),(1.40,.035-out_level)]
fall_rows=[];support_rows=[]
for k,(dx,dy) in enumerate(fall_path):
    progress=k/(len(fall_path)-1);row=[];rock_row=[]
    for i in range(13):
        across=i/12
        turn=.55*smooth(0,.4,progress)
        cross=(across-.5)*out_width*(1+.12*progress)
        z=out_center+.45*smooth(0,.6,progress)+cross*math.cos(turn)
        y=out_level+dy+.025*math.sin(across*math.pi*5)*math.sin(progress*math.pi)
        x=out_x+dx-cross*math.sin(turn)+.025*math.sin(across*math.pi*4)*math.sin(progress*math.pi)
        row.append((x,y,z))
        rock_row.append((x-.15*smooth(0,.4,progress),y-.20,z+(across-.5)*.24))
    fall_rows.append(row);support_rows.append(rock_row)
fall=grid_mesh('ForestVisibility_Creek_Waterfall',fall_rows,lambda j,i:3,closed=False)
support_rock=grid_mesh('ForestVisibility_Creek_Spill_Rock',support_rows,lambda j,i:1)
for li in fall.data.loops:
    vi=li.vertex_index;fall.data.uv_layers[0].data[li.index].uv=(vi%13/12,vi//13/(len(fall_rows)-1))
# An irregular, small landing patch follows the impact; it is not a rigid ring.
foam_verts=[(out_x+1.50,.035,out_center+.45)];foam_faces=[]
for ring in [.28,.62,1.0]:
    for i in range(40):
        a=i*math.tau/40;r=ring*(1+.11*math.sin(a*3)+.07*math.cos(a*7))
        foam_verts.append((out_x+1.50+math.cos(a)*1.25*r,.035,out_center+.45+math.sin(a)*out_width*.72*r))
for i in range(40):foam_faces.append((0,1+i,1+(i+1)%40))
for j in range(2):
    for i in range(40):
        a=1+j*40+i;b=1+j*40+(i+1)%40
        foam_faces.append((a,b,b+40,a+40))
foam=mesh('ForestVisibility_Creek_Foam',foam_verts,foam_faces,[4]*len(foam_faces))
for li in foam.data.loops:
    v=foam.data.vertices[li.vertex_index].co
    foam.data.uv_layers[0].data[li.index].uv=((v.x-out_x-1.50)/2.6+.5,(-v.y-out_center-.45)/(out_width*1.5)+.5)

bx=[-35+i*.8 for i in range(51)]
offsets=[0,.3,.7,1.15,1.7,2.4,3.2,4.2,5.3,6.6,8,9.5,11.2,13,15,17.2,19.5,22,25]
rows=[]
for j,d in enumerate(offsets):
    row=[]
    for i,x in enumerate(bx):
        tx=(x+35)/40
        xx=x-3.4*smooth(4,22,d)*smooth(.60,1,tx)
        front=far_z(x)-max(0,-x-18)*.38
        # Broken, connected shore projections, with different crests behind.
        shore=.56*math.sin(x*.77)+.24*math.sin(x*1.71+.8)
        z=front-d+shore*math.exp(-d*.22)+.34*math.sin(x*.31+d*.35)*smooth(1,5,d)
        foot=creek_level(x)-.25
        lip_height=1.05+.38*math.sin(x*.67+.4)+.24*math.cos(x*1.27)
        lip=lip_height*smooth(.08,.85+.40*(.5+.5*math.sin(x*.58)),d)
        # Local diagonal spurs grow out of an inclined valley floor. Unlike
        # full-width elevation steps these overlap only part of the panorama.
        rise=.27*d+.06*max(0,d-7)
        crest_a=5.7+.27*(x+14)
        crest_b=11.5-.31*(x+5)
        spur_a=2.0*math.exp(-((x+14)/5.2)**4)*math.exp(-((d-crest_a)/(1.05 if d<crest_a else 4.3))**2)
        spur_b=2.1*math.exp(-((x+5)/5.3)**2)*math.exp(-((d-crest_b)/(2.0 if d<crest_b else 5.5))**2)
        rear_spur=2.4*math.exp(-((x+26)/7.0)**2)*math.exp(-((d-13)/5.0)**2)
        ravine=1.0*math.exp(-((x+11-d*.18)/2.9)**2)*smooth(1.5,8,d)
        h=foot+lip+rise-ravine+spur_a+spur_b+rear_spur
        # Eastern mouth descends out of the forest view before the bridge.
        end=smooth(-1.0,5.0,x)
        h=h*(1-end*.97)-end*.15
        if x<2.65 and d<2.4:
            h=max(h,creek_level(x)-.25+.50*smooth(0,1,d))
        # Back closure is outside the woodland framing and falls away gently.
        if d>22:h-=smooth(22,25,d)*2.2
        row.append((xx,h,z))
    rows.append(row)
bank=grid_mesh('ForestVisibility_Opposite_Rock_Slope',rows,lambda j,i:0,1)
# One surface with rock-to-soil blends follows its actual slopes. No broad
# rectangular face assignments and no disconnected boulder caps.
me=bank.data;uv2=me.uv_layers.new(name='ValleySurface')
for p in me.polygons:
    for li in p.loop_indices:
        co=me.vertices[me.loops[li].vertex_index].co;x,z=co.x,-co.y
        d=max(0.,far_z(x)-max(0,-x-18)*.38-z)
        rocky=(1-smooth(.48,.80,abs(p.normal.z)))*.82
        pocket=.5+.5*math.sin(x*.61+d*.48)
        rocky=clamp(rocky-.22*pocket)
        if d>2.5:
            # Exposed rock follows two finite spur faces, not parallel stripes.
            exposure=max(math.exp(-((x+14)/5.8)**4),math.exp(-((x+5)/5.0)**2),math.exp(-((x+26)/6.0)**2))
            rocky*=exposure
        if d<.7:rocky=max(rocky,.48)
        uv2.data[li].uv=(rocky,d/25)
normals=[n.vector.copy() for n in me.corner_normals]
me.normals_split_custom_set([tuple(normals[li].lerp(p.normal,.68 if uv2.data[li].uv.x>.6 else .07).normalized()) for p in me.polygons for li in p.loop_indices])
ground_trees=[land_tree,tree(near),tree(bank)]
def support(x,z):
    hs=[height(t,x,z) for t in ground_trees];return max((h for h in hs if h is not None),default=None)

def components(me):
    adj=[[] for _ in me.vertices]
    for e in me.edges:a,b=e.vertices;adj[a].append(b);adj[b].append(a)
    remaining=set(range(len(adj)));groups=[]
    while remaining:
        seed=min(remaining);remaining.remove(seed);stack=[seed];ids=[]
        while stack:
            vi=stack.pop();ids.append(vi)
            for k in adj[vi]:
                if k in remaining:remaining.remove(k);stack.append(k)
        groups.append(sorted(ids))
    return groups
sources={}
for index in [3,4,5]:
    src=scene.objects['InkSample_Bamboo_%02d'%index];groups=components(src.data)
    owner={v:min(ids) for ids in groups for v in ids}
    roots=[src.matrix_world.inverted()@G(r) for r in json.loads(src['root_positions_godot'])]
    starts=sorted((owner[min(src.data.vertices,key=lambda v:(v.co-r).length_squared).index],i) for i,r in enumerate(roots))
    sources[index]=(src,roots,starts)
bamboo_report=[]
def culm(name,index,chosen,x,z,scale,angle,layer):
    src,roots,starts=sources[index];start,k=starts[chosen%len(starts)]
    end=starts[chosen+1][0] if chosen+1<len(starts) else len(src.data.vertices)
    ob=src.copy();ob.data=src.data.copy();ob.name=name;current.objects.link(ob);ob.hide_set(False);ob.hide_render=False
    me=ob.data;root=roots[k];top=max((v.co.z for v in me.vertices[start:end]));H=top-root.z
    keep=set(range(start,end));removed=0
    for ids in components(me):
        if ids[0]<start or ids[0]>=end:continue
        lo=min(me.vertices[v].co.z for v in ids)-root.z
        horizontal=max((me.vertices[v].co-root).xy.length for v in ids)
        # Whole low branches/leaves are removed. Main segmented culm/node rings remain.
        is_lateral=horizontal>.16 and len(ids) not in [14,21]
        if is_lateral and lo<H*(.62 if layer==0 else .40):
            keep.difference_update(ids);removed+=1
    bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in keep],context='VERTS');bm.to_mesh(me);bm.free()
    h=support(x,z);assert h is not None,(name,x,z)
    ob.matrix_world=Matrix.Translation(G((x,h-.06,z)))@Matrix.Rotation(angle,4,'Z')@Matrix.Diagonal((scale*.92,scale*.92,scale,1))@Matrix.Translation(-root)
    ob['root_positions_godot']=json.dumps([(x,h-.06,z)]);ob['forest_visibility_layer']=layer
    # Dark stems in the near view; restrained atmospheric color on the rear slope.
    ca=me.color_attributes.get('InkColor')
    stem_ids={v for p in me.polygons if p.material_index==0 for v in p.vertices}
    if ca and ca.domain=='POINT' and layer==0:
        for vi in stem_ids:
            c=ca.data[vi].color;ca.data[vi].color=(c[0]*.49,c[1]*.60,c[2]*.56,c[3])
    me.update();bamboo_report.append({'name':name,'root':[x,h-.06,z],'layer':layer,'removed_low_components':removed,'uv':[u.name for u in me.uv_layers]})
    return ob
near_specs=[(-14.2,-1.7,1.30,.15),(-12.2,-2.1,1.20,-.45),(-9.0,-1.8,1.40,.4),(-7.9,-2.2,1.28,-.2),(-4.3,-1.8,1.38,.5),(-1.7,-1.9,1.20,-.3),(.1,-2.1,1.08,.6)]
for i,(x,z,s,a) in enumerate(near_specs):culm('ForestVisibility_Near_Bamboo_%02d'%i,3+i%3,i%6,x,z,s,a,0)
# Trees are rooted to three different elevations; groups have uneven gaps.
rear_specs=[(-27,-15.8,1.13),(-24,-14.8,1.00),(-21,-14.0,1.10),(-18,-14.8,1.02),(-15.6,-15.7,1.1),(-12.8,-15.8,1.0),(-9.4,-16.3,1.04),(-6.2,-17.4,1.0),(-3.5,-18.6,.95),
            (-29,-23,1.12),(-25.5,-22,1.05),(-22.6,-23.5,1.12),(-18.9,-22.6,1.04),(-16.1,-24,1.08),(-12.7,-24.7,1.03),(-9.2,-24.5,1.1),(-5.8,-25.0,1.0),
            (-30,-29,1.15),(-26,-29.8,1.08),(-22.6,-28.7,1.12),(-18.2,-29.1,1.08),(-14.5,-30,1.12),(-11.1,-30.6,1.03),(-7.2,-30.2,1.04)]
for i,(x,z,s) in enumerate(rear_specs):
    z-=max(0.,-x-19)*.28
    culm('ForestVisibility_Rear_Bamboo_%02d'%i,3+i%3,(i+2)%6,x,z,s,(i%5-2)*.32,1 if i<9 else 2)

# A few existing ink grass clusters soften selected bank contacts and root
# bases. Leave most of the creek edge open so it remains readable.
grass_source=scene.objects['Coast_Low_Grass_01.003']
grass_points=[grass_source.matrix_world@v.co for v in grass_source.data.vertices]
grass_center=Vector((sum(p.x for p in grass_points)/len(grass_points),sum(p.y for p in grass_points)/len(grass_points),min(p.z for p in grass_points)))
grass_specs=[(-13.1,-3.4,.58),(-8.8,-3.0,.62),(-7.1,near_z(-7.1)+.5,.48),(-3.4,near_z(-3.4)+.4,.55),
             (-22,far_z(-22)-3.6,.72),(-16,far_z(-16)-4.5,.68),(-11.4,far_z(-11.4)-4.1,.78),(-6.4,far_z(-6.4)-4.3,.65)]
for i,(x,z,s) in enumerate(grass_specs):
    y=support(x,z)
    if y is None:continue
    ob=grass_source.copy();ob.data=grass_source.data.copy();ob.name='ForestVisibility_Bank_Grass_%02d'%i;current.objects.link(ob)
    ob.matrix_world=Matrix.Translation(G((x,y-.04,z)))@Matrix.Rotation(i*.73,4,'Z')@Matrix.Scale(s,4)@Matrix.Translation(-grass_center)@grass_source.matrix_world
    ob['forest_visibility_layer']=0 if i<4 else 1;ob.hide_set(False);ob.hide_render=False

report={'changed_originals':changed,'near_culms':len(near_specs),'rear_culms':len(rear_specs),'bamboo':bamboo_report,'objects':[o.name for o in current.objects]}
(O/'authoring.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export','exec'))
print('FOREST_VISIBILITY_EXPORTED',len(near_specs),len(rear_specs),changed)
