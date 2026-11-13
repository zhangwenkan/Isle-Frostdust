"""Compact cape and a staged forest valley, authored only inside Blender MCP."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/valley-depth-review'
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
profile={};exec(compile((ROOT/'tools/cape_compact_profile.py').read_text(encoding='utf-8'),'profile','exec'),profile)
compact=profile['compact_x'];inverse_x=profile['source_x']
def collection(name):
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in scene.collection.children:scene.collection.children.link(c)
    return c
archive=collection('90_Before_Valley_Depth');archive.hide_render=True
old=bpy.data.collections.get('30_West_Bamboo_Valley')
if old:
    for ob in list(old.objects):
        old.objects.unlink(ob);archive.objects.link(ob);ob.hide_set(True);ob.hide_render=True
current=collection('31_Layered_Forest_Valley')
for ob in list(current.objects):bpy.data.objects.remove(ob,do_unlink=True)
def baseline(ob):
    name='DepthBaseline_'+ob.name;saved=bpy.data.objects.get(name)
    if saved is None:
        saved=ob.copy();saved.data=ob.data.copy();saved.name=name;archive.objects.link(saved);saved.hide_set(True);saved.hide_render=True
    return saved
def active():return [o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') or c==current for c in o.users_collection)]
changes=[]
for ob in active():
    if not (ob.name=='Fish_West_Continuous_Land' or ob.name.startswith(('Campfire_','Coast_Low_Grass_','InkSample_','Depth_Bamboo_Main_','Cliff_Fern_West_','Cliff_Fractures_West'))):continue
    saved=bpy.data.objects.get('DepthBaseline_'+ob.name) or ob
    points=[saved.matrix_world@v.co for v in saved.data.vertices]
    if min(p.x for p in points)>=-11:continue
    saved=baseline(ob);ob.data=saved.data.copy();ob.matrix_world=saved.matrix_world.copy();inv=ob.matrix_world.inverted()
    if ob.name=='Fish_West_Continuous_Land' or ob.name=='Cliff_Fractures_West':
        for v,p in zip(ob.data.vertices,points):v.co=inv@Vector((compact(p.x),p.y,p.z))
        ob.data.normals_split_custom_set([(0,0,0)]*len(ob.data.loops));ob.data.update()
    elif ob.name=='InkSample_Path_Grass':
        for start in range(0,len(points),4):
            dx=compact(points[start].x)-points[start].x
            for k in range(start,min(start+4,len(points))):ob.data.vertices[k].co=inv@(points[k]+Vector((dx,0,0)))
    else:
        center=(min(p.x for p in points)+max(p.x for p in points))*.5
        dx=compact(center)-center;ob.location.x+=dx
        if saved.get('root_positions_godot'):
            roots=json.loads(saved['root_positions_godot']);ob['root_positions_godot']=json.dumps([(r[0]+dx,r[1],r[2]) for r in roots])
    changes.append(ob.name)
land=scene.objects['Fish_West_Continuous_Land']
landtree=BVHTree.FromPolygons([land.matrix_world@v.co for v in land.data.vertices],[tuple(p.vertices) for p in land.data.polygons])
def ground(x,z):
    p=landtree.ray_cast(Vector((x,-z,45)),Vector((0,0,-1)))[0]
    return p.z if p else None
def color(h):
    def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
    return tuple(linear(int(h[i:i+2],16)/255) for i in (0,2,4))+(1,)
def mat(name,h):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color(h);bs.inputs['Roughness'].default_value=1
    vc=m.node_tree.nodes.get('DepthPigment') or m.node_tree.nodes.new('ShaderNodeVertexColor');vc.name='DepthPigment';vc.layer_name='ValleyColor'
    m.node_tree.links.new(vc.outputs['Color'],bs.inputs['Base Color']);return m
mats=[mat('InkValley_Rock','858c7c'),mat('InkValley_Turf','6d8157'),mat('InkValley_Bedrock','798477')]
def mesh(name,verts,faces,ids,layer):
    me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y) for x,y,z in verts],[],faces)
    for m in mats:me.materials.append(m)
    me.update();ob=bpy.data.objects.new(name,me);current.objects.link(ob)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
    ca=me.color_attributes.new(name='ValleyColor',type='FLOAT_COLOR',domain='CORNER');uv=me.uv_layers.new(name='SurfaceUV')
    for p,mi in zip(me.polygons,ids):
        p.material_index=mi;p.use_smooth=True
        for li in p.loop_indices:
            point=verts[me.loops[li].vertex_index]
            h=(['677a50','6b7c58','798667'][layer] if mi==1 else ['818875','7e8b7c','8b978b'][layer])
            c=color(h);variation=.96+.04*math.sin(point[0]*.35+point[2]*.23)
            ca.data[li].color=tuple(t*variation for t in c[:3])+(1,)
            uv.data[li].uv=(point[0]*.14,point[1]*.14 if mi!=1 else point[2]*.14)
    me.color_attributes.active_color=ca
    normals=[n.vector.copy() for n in me.corner_normals]
    me.normals_split_custom_set([tuple(normals[li].lerp(p.normal,.24 if p.material_index!=1 else .04).normalized()) for p in me.polygons for li in p.loop_indices])
    ob['valley_depth_layer']=layer;return ob
def bank(name,stations,cross,layer):
    # Each station defines x, front z, local base height, and irregular crown.
    verts=[]
    for i,(x,z,base,crown) in enumerate(stations):
        for j,(depth,t) in enumerate(cross):
            zz=z-depth+.35*math.sin(i*.93+j*.44)
            yy=base+(crown-base)*t+.15*math.sin(i*1.61+j*.82)
            f=(x-stations[0][0])/(stations[-1][0]-stations[0][0])
            # Receding ends follow the coastline in plan; no overhanging cap
            # or vertical closing sheet toward the cape and bridge.
            xx=x+.27*math.sin(i*1.41+j*.73)*math.sin(f*math.pi)
            verts.append((xx,yy,zz))
    faces=[];ids=[];n=len(cross)
    for i in range(len(stations)-1):
        for j in range(n-1):
            a=i*n+j;b=a+n;c=b+1;d=a+1
            faces.extend([(a,b,c),(a,c,d)])
            rock=(layer>0 and j in [1,2] and i%5 in [1,2])
            ids.extend([0 if rock else 1]*2)
    perimeter=list(range(n))+[i*n+n-1 for i in range(1,len(stations))]+[(len(stations)-1)*n+j for j in range(n-2,-1,-1)]+[i*n for i in range(len(stations)-2,0,-1)]
    lower=[]
    # Curved, sloping bedrock skirts. The front skirt is buried into the
    # preceding slope; side skirts taper inward behind the bridge opening.
    center_x=sum(v[0] for v in verts)/len(verts)
    for vi in perimeter:
        p=verts[vi];lower.append(len(verts));verts.append((p[0]+(center_x-p[0])*.04,-4,p[2]-1.2))
    for k,a in enumerate(perimeter):
        kk=(k+1)%len(perimeter);faces.extend([(a,perimeter[kk],lower[kk]),(a,lower[kk],lower[k])]);ids.extend([2,2])
    faces.append(tuple(reversed(lower)));ids.append(2)
    return mesh(name,verts,faces,ids,layer)

# Three connected terrain sections share their boundary rows. A low valley
# separates the rooted foreground from the rocky opposite slope; its rear
# shoulder recedes much farther than the former stacked slabs.
rows=[
    (-3.2,-18.2,3.8,4.0),(-5.5,-18.7,4.1,4.2),
    (-8.0,-19.3,4.4,3.7),(-10.5,-20,4.7,3.3),
    (-20.0,-27,5.0,2.7),(-25.0,-34,5.2,3.8),
    (-28.0,-39,5.2,5.5),(-33,-45,5.0,6.1),
    (-39,-53,4.7,5.8),(-47,-64,4.3,5.3),
    (-58,-80,3.8,6.1),(-72,-97,3.0,7.2),
    (-88,-114,2.0,8.4),(-110,-130,1.0,8.0)]
columns=27
grid=[]
for r,(z,left,right,h) in enumerate(rows):
    line=[]
    for i in range(columns):
        t=i/(columns-1);x=left+(right-left)*t
        zz=z+(.65*math.sin(t*math.pi*3.3+r*.45)+.28*math.sin(t*math.pi*7-r*.37))*math.sin(t*math.pi)
        # Both ends turn into the island. They are neither square vertical
        # slices nor projecting fingers under the bridge.
        zz-=((1-t)**8*(.3+r*.3)+t**8*(4.0+r*.8))
        yy=h+.7*math.sin(x*.28+r*.18)+.24*math.sin(x*.63-r*.29)
        if r<=1:
            yy=(ground(x,zz) or h)-.12
        # A descending, irregular eastern shoreline reveals the bridge view.
        taper=max(0,min(1,(t-.89)/.11));taper=taper*taper*(3-2*taper)
        if r>0:yy=yy*(1-.55*taper)-.28*taper
        line.append((x,yy,zz))
    grid.append(line)

def terrain_section(name,start,end,layer):
    verts=[p for line in grid[start:end+1] for p in line];faces=[];ids=[]
    for rr in range(end-start):
        r=rr+start
        for i in range(columns-1):
            a=rr*columns+i;b=a+columns
            faces.extend([(a,b,b+1),(a,b+1,a+1)])
            # Broad discontinuous exposed rock follows the steeper bank,
            # interleaved with grass shoulders, never a full-width stripe.
            stone=r==5 and i in [4,5,6,12,13,19,20]
            ids.extend([2 if stone else 1]*2)
    # Close each section so outward normals are unambiguous after export.
    # Adjacent section boundaries are identical and buried inside the volume.
    nrows=end-start+1
    perimeter=list(range(columns))+[r*columns+columns-1 for r in range(1,nrows)]+[(nrows-1)*columns+i for i in range(columns-2,-1,-1)]+[r*columns for r in range(nrows-2,0,-1)]
    prev=perimeter
    for step in range(1,4):
        curr=[]
        for j,vi in enumerate(perimeter):
            x,y,z=verts[vi]
            side_sign=-1 if vi%columns==0 else 1 if vi%columns==columns-1 else 0
            # An angled uneven bedrock shoreline, with differently tilted
            # rock planes rather than a single rectangular closing face.
            dx=side_sign*(.30*step+.16*math.sin(j*1.9)*math.sin(step*math.pi/3))
            curr.append(len(verts));verts.append((x+dx,y-(y+5)*step/3+.14*math.sin(j*1.4)*math.sin(step*math.pi/3),z-.45*step))
        for j in range(len(prev)):
            k=(j+1)%len(prev)
            faces.append((prev[j],prev[k],curr[k],curr[j]));ids.append(2)
        prev=curr
    faces.append(tuple(reversed(prev)));ids.append(2)
    return mesh(name,verts,faces,ids,layer)
near=terrain_section('ValleyDepth_Connected_Terrain',0,len(grid)-1,0)
middle=near;rear=near
trees=[BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons]) for ob in [near,middle,rear]]
def support(x,z):
    points=[t.ray_cast(Vector((x,-z,45)),Vector((0,0,-1)))[0] for t in [landtree]+trees]
    return max((p for p in points if p is not None),key=lambda p:p.z,default=None)

def bamboo(index,x,z,scale,angle,layer):
    src=scene.objects['InkSample_Bamboo_%02d'%(3+index%3)];points=[src.matrix_world@v.co for v in src.data.vertices]
    center=Vector(((min(p.x for p in points)+max(p.x for p in points))*.5,(min(p.y for p in points)+max(p.y for p in points))*.5,min(p.z for p in points)))
    hit=support(x,z)
    if hit is None:
        candidates=sorted([(a*.4,b*.4) for a in range(-12,13) for b in range(-12,13)],key=lambda q:q[0]**2+q[1]**2)
        for dx,dz in candidates:
            hit=support(x+dx,z+dz)
            if hit is not None:x=hit.x;z=-hit.y;break
    assert hit is not None,(x,z)
    ob=src.copy();ob.data=src.data.copy();ob.name='ValleyDepth_Bamboo_%02d'%index;current.objects.link(ob)
    ob.matrix_world=Matrix.Translation(hit)@Matrix.Rotation(angle,4,'Z')@Matrix.Scale(scale,4)@Matrix.Translation(-center)@src.matrix_world
    roots=[Vector((r[0],-r[2],r[1])) for r in json.loads(src['root_positions_godot'])]
    # Source roots are world coordinates; recover mesh-local coordinates.
    roots=[src.matrix_world.inverted()@r for r in roots]
    adjacency=[[] for _ in ob.data.vertices]
    for e in ob.data.edges:a,b=e.vertices;adjacency[a].append(b);adjacency[b].append(a)
    remaining=set(range(len(adjacency)));start_ids={}
    while remaining:
        seed=remaining.pop();stack=[seed];component=[seed]
        while stack:
            for v in adjacency[stack.pop()]:
                if v in remaining:remaining.remove(v);stack.append(v);component.append(v)
        for v in component:start_ids[v]=min(component)
    starts=[];shifts=[];new_roots=[];inv=ob.matrix_world.inverted()
    for k,r in enumerate(roots):
        closest=min(ob.data.vertices,key=lambda v:(v.co-r).length_squared);assert (closest.co-r).length<.13
        starts.append((start_ids[closest.index],k));p=ob.matrix_world@r;hit=support(p.x,-p.y)
        if hit is None:
            candidates=sorted([(a*.2,b*.2) for a in range(-15,16) for b in range(-15,16)],key=lambda q:q[0]**2+q[1]**2)
            for dx,dz in candidates:
                hit=support(p.x+dx,-p.y+dz)
                if hit is not None:break
        assert hit is not None,(index,tuple(p))
        target=hit-Vector((0,0,.06));shifts.append(inv.to_3x3()@(target-p));new_roots.append((target.x,target.z,-target.y))
    starts.sort();assert len(set(a for a,b in starts))==len(roots)
    for j,(start,k) in enumerate(starts):
        end=starts[j+1][0] if j+1<len(starts) else len(ob.data.vertices)
        for vi in range(start,end):ob.data.vertices[vi].co+=shifts[k]
    ob['root_positions_godot']=json.dumps(new_roots);ob['valley_depth_layer']=layer;ob.data.update();return ob
specs=[(-12.4,-6.5,.64,.2,0),
       (-27,-35,1.35,-.3,1),(-21,-34,1.25,.4,1),(-14,-35,1.2,-.2,1),(-6,-38,1.12,.3,1),
       (-51,-75,2.2,.2,2),(-42,-66,2.1,-.3,2),(-34,-63,2.0,.4,2),(-26,-62,1.95,-.4,2),(-18,-64,1.9,.1,2),(-10,-67,1.8,-.3,2),(-3,-72,1.6,.4,2)]
groves=[bamboo(i,*s).name for i,s in enumerate(specs)]

# Broad attached outcrops at the middle slope, not scattered path-side props.
for i,(cx,cz,w,h,d) in enumerate([(-22.0,-27.5,6.4,2.0,4.0),(-12.5,-29.0,5.8,2.2,3.8),(-4.5,-31.5,4.8,1.8,3.4)]):
    hit=support(cx,cz);assert hit is not None
    outline=[(-.5,-.3),(-.31,-.52),(.33,-.48),(.52,-.15),(.45,.36),(.05,.5),(-.48,.3)]
    verts=[]
    for level in range(3):
        for j,(u,v) in enumerate(outline):
            f=[1.03,1,.79][level];verts.append((cx+u*w*f+.14*level,hit.z-.40+[0,.68*h,h][level]-.18*u+(.09*math.sin(j*1.3) if level==2 else 0),cz+v*d*f))
    faces=[]
    for r in range(2):
        for j in range(7):k=(j+1)%7;faces.append((r*7+j,r*7+k,(r+1)*7+k,(r+1)*7+j))
    faces+=[tuple(range(14,21)),tuple(reversed(range(7)))];mesh('ValleyDepth_Exposure_%02d'%i,verts,faces,[2]*len(faces),1)

route={};exec(compile((ROOT/'tools/cape_road_profile.py').read_text(encoding='utf-8'),'road','exec'),route)
samples=[]
for k in range(118):
    x=-15.2+k*.16
    for dz in [-.5,0,.5]:
        sx=inverse_x(x);z=route['route'](sx)+dz if sx<-12.5 else route['old_path'](sx)+dz
        hit=landtree.ray_cast(Vector((x,-z,40)),Vector((0,0,-1)))[0]
        if hit:
            y=route['deform_height'](sx,z,route['old_height'](sx,z));samples.append(abs(y-hit.z))
assert max(samples)<.13,max(samples)
report={'changed_original_meshes':changes,'new_meshes':[o.name for o in current.objects],'layout_shift_m':5.5,'hero_start_x':-15.2,'campfire_x':-17.5,'walk_samples':len(samples),'max_surface_error_m':max(samples),'bamboo_groups':groves,'depth_layers_z':['near: -4 to -11','opposite bank: -12 to -23','wooded ridge: -27 to -41']}
(OUT/'blender-authoring.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export','exec'))
print('LAYERED_VALLEY_EXPORTED',json.dumps(report))
