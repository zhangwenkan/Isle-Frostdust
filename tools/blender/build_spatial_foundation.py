"""Build the walkable coastal sample as actual volumes, ONLY via Blender MCP."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from mathutils.bvhtree import BVHTree
import numpy as np
root=Path('D:/自己做着玩的/孤屿霜尘');out=root/'assets/layered_island';tex=out/'spatial_textures'
scene=bpy.data.scenes['Layered_Island_20261116'];previous=bpy.context.window.scene;bpy.context.window.scene=scene
if bpy.data.collections.get('40_Spatial_Foundation'):
    raise RuntimeError('Sample already exists: refine it instead of rebuilding blindly')
col=bpy.data.collections.new('40_Spatial_Foundation');scene.collection.children.link(col)
archive=bpy.data.collections.new('90_Before_Spatial_Foundation');scene.collection.children.link(archive)
layout=json.loads((out/'layout.json').read_text(encoding='utf-8'))
anchors={k:Vector((p[0],-p[2],p[1])) for k,p in layout['anchors'].items()}
materials={};created=[];archived=[]
def material(name,image=None,color=(.42,.39,.30,1)):
    m=bpy.data.materials.new('SP_'+name);m.use_nodes=True;m.diffuse_color=color
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=.96
    if image:
        im=bpy.data.images.load(str(tex/(image+'.png')),check_existing=True);im.pack()
        node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;m.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
        if image.startswith('bamboo'):
            m.node_tree.links.new(node.outputs['Alpha'],bs.inputs['Alpha']);m.surface_render_method='DITHERED'
    materials[name]=m;return m
rock=material('Rock','rock');sand=material('Sand','sand');ground=material('Ground','grass');stepmat=material('Step','step')
grass=material('Grass',None,(.27,.34,.12,1));culm=material('Culm',None,(.35,.42,.18,1));node_mat=material('Node',None,(.43,.47,.25,1))
for name in ['bamboo_middle','bamboo_front','bamboo_bridge']:material(name,name)

def stash(ob):
    oldname=ob.name
    for c in list(ob.users_collection):c.objects.unlink(ob)
    archive.objects.link(ob);ob.hide_render=True;ob.hide_set(True);ob.name='Before_Space_'+oldname;archived.append(oldname)
def mesh(name,vs,fs,mats,uvs=None,weights=None,indices=None):
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);col.objects.link(ob);created.append(ob)
    for m in mats:me.materials.append(m)
    uv=me.uv_layers.new(name='UVMap');wind=me.uv_layers.new(name='Wind')
    for p in me.polygons:
        if indices:p.material_index=indices[p.index]
        n=p.normal
        for li in p.loop_indices:
            vi=me.loops[li].vertex_index;v=me.vertices[vi].co
            if uvs:coord=uvs[vi]
            elif abs(n.z)>.65:coord=(v.x*.58,v.y*.58)
            elif abs(n.x)>abs(n.y):coord=(v.y*.66,v.z*.62)
            else:coord=(v.x*.66,v.z*.62)
            uv.data[li].uv=coord;wind.data[li].uv=(weights[vi] if weights else 0,0)
    return ob
def cap_indices(points):
    vectors=[Vector(p) for p in points]
    tris=tessellate_polygon([vectors])
    return [tuple(int(v) if isinstance(v,int) else min(range(len(vectors)),key=lambda i:(vectors[i]-v).length_squared) for v in tri) for tri in tris]
def top_h(x,y):return 2.85+.72*max(0,min(1,(y-2.70)/1.24))

# Preserve the upper route, but retire the projected near cliff and beach.
old=scene.objects['Land_Relief'];upper=old.copy();upper.data=old.data.copy();stash(old);upper.name='Land_Relief';col.objects.link(upper);upper.hide_render=False;upper.hide_set(False)
bm=bmesh.new();bm.from_mesh(upper.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_center_median().y<3.85],context='FACES')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bm.to_mesh(upper.data);bm.free();upper.data.update()
for name in ['WALK_Front_Stairs','Foreground_Bottom','Foreground_Right_Rock','Foreground_Right_Leaves','Bamboo_Back','Bamboo_Middle_Left','Bamboo_Middle_Deep','Bamboo_Front_Left','Bamboo_Bridge']:
    if scene.objects.get(name):stash(scene.objects[name])

# A continuous cliff volume. The central notch leaves room for the actual stairs.
outline=[(-16,4.5),(-16,-.8),(-14,-2.0),(-11.5,-2.15),(-9.5,-2.7),(-7,-2.0),(-6.5,-1.6),(-5.68,-.18),(-3.83,-.18),(-3.3,-1.4),(-1.2,-1.0),(.78,.7),(.78,2.5),(-1.8,4.4),(-7,4.5)]
if sum(outline[i][0]*outline[(i+1)%len(outline)][1]-outline[(i+1)%len(outline)][0]*outline[i][1] for i in range(len(outline)))<0:outline.reverse()
n=len(outline);vs=[];fractions=[0,.26,.72,1.]
for ring,f in enumerate(fractions):
    for i,(x,y) in enumerate(outline):
        prev=Vector(outline[(i-1)%n]);nxt=Vector(outline[(i+1)%n]);edge=nxt-prev
        outward=Vector((edge.y,-edge.x)).normalized()
        spread=[.38,.50,.15,0][ring]*(.75+.25*math.sin(i*1.7))
        if -6.7<x<-3.3 and y<.2:spread*=.08
        xx=x+outward.x*spread;yy=y+outward.y*spread
        vs.append((xx,yy,-.62+(top_h(x,y)-.10+.62)*f))
fs=[]
for r in range(3):
    for i in range(n):
        j=(i+1)%n;fs.append((r*n+i,r*n+j,(r+1)*n+j,(r+1)*n+i))
fs.extend([tuple(reversed(t)) for t in cap_indices(vs[:n])])
fs.extend([tuple(3*n+i for i in t) for t in cap_indices(vs[3*n:])])
mesh('Space_Continuous_Cliff',vs,fs,[rock])

# Subdivided top retains a clean silhouette and supplies proper receiving faces.
top=[(x,y,top_h(x,y)) for x,y in outline]
ob=mesh('WALK_Space_Ground',top,cap_indices(top),[ground])
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=6,use_grid_fill=True)
for v in bm.verts:v.co.z=top_h(v.co.x,v.co.y)
bm.to_mesh(ob.data);bm.free();ob.data.update()
uv=ob.data.uv_layers[0]
for l in ob.data.loops:
    p=ob.data.vertices[l.vertex_index].co;uv.data[l.index].uv=(p.x*.55,p.y*.55)

# Low beach shelf closes beneath the water rather than ending at a cut alpha edge.
beach=[(-13.0,-2.0),(-10.5,-2.5),(-7.0,-2.4),(-6.3,-3.05),(-4.6,-3.3),(-3.1,-2.0),(-1.5,-2.3),(-.6,-3.8),(-1.5,-5.7),(-4.4,-6.9),(-7.7,-7.2),(-10.7,-6.2),(-12.8,-4.5)]
center=Vector((-6.9,-4.35));bv=[]
for x,y in beach:bv.append((x,y,.075))
bn=len(beach);bv.append((center.x,center.y,.15))
bf=[(bn,i,(i+1)%bn) for i in range(bn)]
ob=mesh('WALK_Space_Beach',bv,bf,[sand])
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=7,use_grid_fill=True)
for v in bm.verts:
    p=v.co
    # Preserve the exact original starting route height in a broad comfortable area.
    if -9.0<p.x<-3.7 and -5.7<p.y<-2.5:p.z=.15
bm.to_mesh(ob.data);bm.free();ob.data.update()
uv=ob.data.uv_layers[0]
for l in ob.data.loops:
    p=ob.data.vertices[l.vertex_index].co;uv.data[l.index].uv=(p.x*.35,p.y*.35)
sv=[(x,y,.075) for x,y in beach]+[(center.x+(x-center.x)*1.08,center.y+(y-center.y)*1.08,-.65) for x,y in beach]
mesh('Space_Beach_Edge',sv,[(i,(i+1)%bn,(i+1)%bn+bn,i+bn) for i in range(bn)],[sand])

# Solid stepped profile, with top, riser, side and underside surfaces.
a=anchors['stair_bottom'];b=anchors['stair_top'];d=b-a;across=Vector((d.y,-d.x,0)).normalized()*.94;steps=15
profile=[Vector((a.x,a.y,a.z-.13))]
for j in range(steps):
    p=a.lerp(b,j/steps);q=a.lerp(b,(j+1)/steps);profile.append(p.copy());p.z=q.z;profile.append(p.copy())
profile.append(b.copy());end=b.copy();end.z=a.z-.13;profile.append(end)
vs=[p+side*across for side in [-1,1] for p in profile];pn=len(profile);fs=[];mi=[]
for j in range(pn):
    k=(j+1)%pn;fs.append((j,k,pn+k,pn+j));mi.append(1 if abs(profile[k].z-profile[j].z)<.001 else 0)
# Side triangulation is projected into a local vertical profile to retain concavity.
local=[((p-a).dot(Vector((d.x,d.y,0)).normalized()),p.z,0) for p in profile]
for tri in cap_indices(local):fs.append(tuple(reversed(tri)));mi.append(0);fs.append(tuple(pn+i for i in tri));mi.append(0)
mesh('WALK_Space_Stairs',vs,fs,[rock,stepmat],indices=mi)

# Four embedded shoulders share the cliff's direction; no loose stone scatter.
def shoulder(name,x,y,w,depth,h,lean):
    plan=[(-.50,-.35),(-.15,-.56),(.43,-.32),(.52,.20),(.14,.45),(-.45,.27)]
    verts=[]
    for ring in range(3):
        for i,(px,py) in enumerate(plan):
            scale=[1.0,1.04,.79][ring]
            z=[-.25,h*.56,h][ring]+(px*lean if ring==2 else 0)
            verts.append((x+px*w*scale,y+py*depth*scale,z))
    faces=[]
    for ring in range(2):
        for i in range(6):j=(i+1)%6;faces.append((ring*6+i,ring*6+j,(ring+1)*6+j,(ring+1)*6+i))
    faces.extend([tuple(reversed(t)) for t in cap_indices(verts[:6])]);faces.extend([tuple(12+i for i in t) for t in cap_indices(verts[12:])])
    mesh(name,verts,faces,[rock])
for row in [('West',-12.5,-2.15,2.5,1.4,2.45,.40),('Main',-9.3,-2.55,2.4,1.25,2.64,-.33),('Stair',-6.9,-1.95,1.25,1.1,2.32,.28),('Bridge',-1.7,-1.05,2.25,1.1,2.55,-.25)]:shoulder('Space_Rock_'+row[0],*row[1:])

# Bamboo groups now have explicit roots and several depth layers. Short culms
# behind the cards give the nearest clusters actual thickness and cast shadows.
placements=[(-14.1,1.7,5.5,2.65,-.16,0),(-11.7,2.5,6.0,2.8,.10,1),(-8.8,2.7,5.9,2.75,-.10,2),(-6.5,3.2,5.5,2.5,.08,0),(-2.1,2.8,5.8,2.7,-.17,2),
(-13.8,5.3,6.2,3.0,.13,1),(-10.9,5.5,6.6,3.1,-.10,0),(-8.0,6.2,6.1,2.9,.08,2),(-4.0,5.4,6.1,2.8,-.12,1),(-1.4,5.8,6.5,3.2,.09,0),
(-15.2,8.4,7.0,3.4,.1,0),(-11.9,9.6,7.0,3.4,-.1,2),(-10.0,11.0,7.3,3.4,.12,1),(-14.5,12.5,7.0,3.3,-.1,0)]
upper_tree=BVHTree.FromPolygons([upper.matrix_world@v.co for v in upper.data.vertices],[list(p.vertices) for p in upper.data.polygons])
plant_roots=[]
def plant_ground(x,y):
    if y<4.0:return top_h(x,y)
    hit=upper_tree.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))
    if hit[0] is not None:return hit[0].z
    raise RuntimeError('No ground for bamboo at '+str((x,y)))
names=['bamboo_middle','bamboo_front','bamboo_bridge']
for idx,(x,y,h,w,angle,variant) in enumerate(placements):
    base=plant_ground(x,y);vs=[];uvs=[];weights=[];faces=[];nx=24;ny=28
    im=next(n.image for n in materials[names[variant]].node_tree.nodes if n.type=='TEX_IMAGE')
    arr=np.array(im.pixels[:],dtype=np.float32).reshape(im.size[1],im.size[0],4)[:,:,3]
    root_v=[]
    for i in range(nx+1):
        px=int(i/nx*(im.size[0]-1));ys=np.where(arr[:,max(0,px-10):min(im.size[0],px+11)].max(axis=1)>.4)[0]
        root_v.append(min(.23,float(ys[0])/im.size[1]) if len(ys) else 0)
    plant_roots.append({'name':'Space_Bamboo_%02d'%idx,'root':[x,y,base]})
    # Ground each visible culm without moving the canopy or its painted proportions.
    for j in range(ny+1):
        v=j/ny
        for i in range(nx+1):
            u=i/nx;xx=(u-.5)*w;e=max(0,min(1,(v-.25)/.40));e=e*e*(3-2*e);zz=v*h-root_v[i]*h*(1-e)
            vs.append((x+xx*math.cos(angle),y+xx*math.sin(angle)+.06*math.sin(v*math.pi),base+zz))
            uvs.append((u,v));weights.append(max(0,(v-root_v[i])/(1-root_v[i]))**2)
    for j in range(ny):
        for i in range(nx):k=j*(nx+1)+i;faces.append((k,k+1,k+nx+2,k+nx+1))
    mesh('Space_Bamboo_%02d'%idx,vs,faces,[materials[names[variant]]],uvs,weights)
    if idx<5:
        for stem in range(3):
            cx=x+(-.65+stem*.56)*w*.42;cy=y-.02;sh=h*(.80+.065*stem);verts=[];fs=[];inds=[]
            for ring in range(13):
                z=sh*ring/12;r=.045*(1-.28*ring/12)*(1.10 if ring%2==0 else 1)
                for k in range(8):
                    a=k*math.tau/8;verts.append((cx+math.cos(a)*r+.05*z,cy+math.sin(a)*r,base+z))
            for ring in range(12):
                for k in range(8):j=(k+1)%8;fs.append((ring*8+k,ring*8+j,(ring+1)*8+j,(ring+1)*8+k));inds.append(1 if ring%2==0 else 0)
            mesh('Space_Culm_%02d_%d'%(idx,stem),verts,fs,[culm,node_mat],indices=inds)

# Sparse broad grass at cliff edges; roots stay fixed under wind deformation.
for i in range(len(outline)):
    p=Vector(outline[i]);q=Vector(outline[(i+1)%len(outline)])
    if p.y>3.5 or (-6.8<p.x<-3.2 and p.y<.4):continue
    count=max(1,int((q-p).length/1.1))
    for j in range(count):
        c=p.lerp(q,(j+.5)/count);inward=(Vector((-7,2))-c).normalized()*.18;c+=inward;z=top_h(c.x,c.y)
        vs=[];fs=[];weights=[]
        for k in range(5):
            a=k*2.1+i*.7;dx=math.cos(a);dy=math.sin(a);height=.18+.10*((k+i)%3)/2;width=.035
            base=Vector((c.x+dx*.11,c.y+dy*.11,z));side=Vector((-dy,dx,0))*width
            mid=base+Vector((dx*.035,dy*.035,height*.62));tip=base+Vector((dx*.11,dy*.11,height))
            n=len(vs);vs.extend([base-side,base+side,mid-side*.7,mid+side*.7,tip]);weights.extend([0,0,.45,.45,1]);fs.extend([(n,n+1,n+3,n+2),(n+2,n+3,n+4)])
        mesh('Space_Grass_%02d_%02d'%(i,j),vs,fs,[grass],weights=weights)

live=[o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
layout['revision']='spatial-foundation-sample'
layout['camera']['physical_offset']=[0,12,20];layout['camera']['physical_fov']=28.0
layout['spatial_sample']={'hidden_route_surfaces':['WALK_Route_00','WALK_Route_02','WALK_Route_03','WALK_Route_07'],'new_collection':col.name,'scope':'beach stairs platform bridge approach'}
# The shader follows the new solid beach edge, not the retired painting contour.
shore=beach+[beach[0]]
lengths=[0.0]
for p,q in zip(shore,shore[1:]):lengths.append(lengths[-1]+(Vector(q)-Vector(p)).length)
coast=[]
for j in range(32):
    distance=lengths[-1]*j/31
    k=next((k for k in range(len(lengths)-1) if lengths[k+1]>=distance),len(shore)-2)
    p=Vector(shore[k]).lerp(Vector(shore[k+1]),(distance-lengths[k])/(lengths[k+1]-lengths[k]))
    coast.append([p.x*1.025,-p.y*1.025])
layout['shoreline']=coast
layout['objects']=[{'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons)} for o in live]
(out/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.data.libraries.write(str(out/'layered_island.blend'),{scene},fake_user=True,compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in live:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=created[0]
bpy.ops.export_scene.gltf(filepath=str(out/'layered_island.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
report={'created':[o.name for o in created],'archived':archived,'plant_roots':plant_roots,'live_mesh_count':len(live),'new_triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in created)}
(root/'artifacts/spatial-foundation-review/model-build.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.context.window.scene=previous
print(json.dumps({'new_objects':len(created),'archived':archived,'triangles':report['new_triangles']}))
