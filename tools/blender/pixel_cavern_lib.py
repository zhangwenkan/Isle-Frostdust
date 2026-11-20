"""New cavern study authoring utilities. Execute ONLY inside Blender via MCP.
No prior project geometry or author scripts are accessed.
"""
import bpy,bmesh,math,random,json
from mathutils import Vector,Matrix
from pathlib import Path
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
SCENE='Pixel_Cavern_Coast'
OUT=ROOT/'assets/pixel_cavern_coast'
rng=random.Random(631127)

def collection(name):
    c=bpy.data.collections.get('PCC_'+name)
    if not c:
        c=bpy.data.collections.new('PCC_'+name);bpy.context.scene.collection.children.link(c)
    return c

def mat(name,h):
    key='PCC_'+name
    m=bpy.data.materials.get(key)
    if m:return m
    v=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    v=[x/12.92 if x<.04045 else ((x+.055)/1.055)**2.4 for x in v]
    m=bpy.data.materials.new(key);m.use_nodes=True;m.diffuse_color=(*v,1)
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*v,1);bs.inputs['Roughness'].default_value=.96
    m['source_srgb']=h
    return m

def palette():
    return {k:mat(k,v) for k,v in {
      'stone':'929786','stone_light':'aab09a','stone_shadow':'69796e','stone_cool':'728782',
      'stone_moss':'65764b','earth':'696a47','grass':'7e914d','grass_light':'a2ae60','grass_dark':'4a6944',
      'path':'b5b18b','step':'a9ac93','step_alt':'9caa94','sand':'b7aa7e','sand_wet':'8c9a82',
      'bamboo':'738b49','bamboo_light':'a5ac61','bamboo_dark':'3d6348','bamboo_node':'a0af71',
      'leaf':'688b4e','leaf_lit':'90a75b','leaf_dark':'355b45','fern':'567b4c',
      'wood':'8e6947','wood_lit':'b58c58','wood_dark':'5c5541','rope':'b79c6e',
      'root':'796247','cave':'263e48','cave_inner':'1d303d','water':'498c8c','foam':'c0d2bb',
      'mountain_near':'6a8a89','mountain_mid':'95acab','mountain_far':'b7c5bd',
      'cloud':'c3d3c8','flower':'c4bc7b'
    }.items()}

def active(ob):
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob

def finish(ob,coll,mats):
    for c in list(ob.users_collection):c.objects.unlink(ob)
    coll.objects.link(ob)
    ob['pixel_cavern']=True;ob['source']='empty scene, new image composition, authored through Blender MCP'
    for m in mats:ob.data.materials.append(m)
    me=ob.data
    uv=me.uv_layers.get('UVMap') or me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        a=(0,1) if abs(p.normal.z)>.6 else (0,2) if abs(p.normal.y)>.5 else (1,2)
        for li in p.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[a[0]]*.25,co[a[1]]*.25)
    return ob

def mesh(name,verts,faces,coll,mats,indices=None):
    me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);coll.objects.link(ob)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    finish(ob,coll,mats)
    if indices:
        for p,i in zip(me.polygons,indices):p.material_index=i
    return ob

def slab(name,poly,top,depth,coll,mats,bevel=0,slope=(0,0)):
    n=len(poly);cx=sum(x for x,y in poly)/n;cy=sum(y for x,y in poly)/n
    vs=[(x,y,top-depth+slope[0]*(x-cx)+slope[1]*(y-cy)) for x,y in poly]+[(x,y,top+slope[0]*(x-cx)+slope[1]*(y-cy)) for x,y in poly]
    fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    ob=mesh(name,vs,fs,coll,mats)
    if bevel:
        active(ob);mod=ob.modifiers.new('Stone edge wear','BEVEL');mod.width=bevel;mod.segments=1;mod.affect='EDGES';mod.angle_limit=.70
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob

def cut(bm,co,no):
    r=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.0001,plane_co=co,plane_no=no,clear_outer=True)
    edges=[e for e in r['geom_cut'] if isinstance(e,bmesh.types.BMEdge) and e.is_boundary]
    if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0)

def rock(name,center,scale,coll,mats,seed=0,rotation=0):
    """Sculptable low-frequency silhouette with specific fracture planes.
    Denser than a polygon prism, quiet enough for the target pixel scale.
    """
    r=random.Random(seed+144);bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=3,radius=1)
    for v in bm.verts:
        q=v.co.copy();a=r.uniform(-.035,.035)
        v.co.x=q.x*(1+.10*math.sin(q.z*4+seed))+.075*math.sin(q.y*4+seed*.7)
        v.co.y=q.y*(1+.11*math.sin(q.x*3-seed))+.06*math.sin(q.z*5+.7*seed)
        v.co.z=q.z+.065*math.sin(q.x*4+q.y*3+seed)+a
    cut(bm,Vector((0,0,.78)),Vector((.13*math.sin(seed),-.12,1)))
    cut(bm,Vector((.72,0,.0)),Vector((1,.16,-.15)))
    cut(bm,Vector((-.73,-.28,.1)),Vector((-.8,-.6,.15)))
    cut(bm,Vector((0,-.79,-.18)),Vector((-.12,-1,-.15)))
    rot=Matrix.Rotation(rotation,3,'Z');ctr=Vector(center)
    for v in bm.verts:v.co=rot@Vector((v.co.x*scale[0],v.co.y*scale[1],v.co.z*scale[2]))+ctr
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    me=bpy.data.meshes.new(name+'_mesh');bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);coll.objects.link(ob);finish(ob,coll,mats)
    # Broad face colors follow orientation; no random per-triangle patchwork.
    for p in me.polygons:
        p.material_index=1 if len(mats)>1 and p.normal.z>.65 else 0
        p.use_smooth=False
    # Dissolve only nearly coplanar facets, keeping the designed curved silhouette.
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.dissolve_limit(bm,angle_limit=.17,verts=list(bm.verts),edges=list(bm.edges));bm.to_mesh(me);bm.free()
    return ob

def tube(name,points,radius,coll,material,radii=None,sides=7):
    vs=[];fs=[];pts=[Vector(p) for p in points]
    for i,p in enumerate(pts):
        d=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized();u=d.cross(Vector((0,0,1)))
        if u.length<.05:u=d.cross(Vector((0,1,0)))
        u.normalize();v=d.cross(u);rad=radius if radii is None else radii[i]
        for j in range(sides):vs.append(tuple(p+(u*math.cos(j*math.tau/sides)+v*math.sin(j*math.tau/sides))*rad))
    for i in range(len(pts)-1):
        for j in range(sides):fs.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
    fs.extend([tuple(reversed(range(sides))),tuple(range((len(pts)-1)*sides,len(pts)*sides))])
    return mesh(name,vs,fs,coll,[material])

def leaf_group(name,origin,heading,length,coll,mats,seed=0,fullness=12):
    r=random.Random(seed+29);o=Vector(origin);vs=[];fs=[];ix=[];ns=[]
    for i in range(fullness):
        side=-1 if i%2 else 1;t=(i//2)/(fullness/2)
        axis=Vector((math.cos(heading),math.sin(heading),.1))
        root=o+axis*t*length*.62
        a=heading+side*(.45+t*.64)+r.uniform(-.12,.12)
        direction=Vector((math.cos(a),math.sin(a),-.23-t*.32))
        ln=length*(.40+.22*(1-t))*r.uniform(.88,1.08);w=ln*(.13+r.random()*.035)
        mid=root+direction*ln*.48+Vector((0,0,.05));tip=root+direction*ln
        cross=Vector((-direction.y,direction.x,.04));k=len(vs)
        vs.extend([tuple(root),tuple(mid-cross*w),tuple(tip),tuple(mid+cross*w)])
        fs.append((k,k+1,k+2,k+3));ix.append(1 if i%5==0 else 0)
    ob=mesh(name,vs,fs,coll,mats,ix)
    center=o+Vector((0,0,-.3))
    normals=[]
    for l in ob.data.loops:
        q=ob.data.vertices[l.vertex_index].co-center
        normals.append(tuple(Vector((q.x*.25,q.y*.25,.88+q.z*.12)).normalized()))
    ob.data.normals_split_custom_set(normals)
    return ob

def export_scene(revision):
    scene=bpy.data.scenes[SCENE];bpy.context.window.scene=scene;scene['revision']=revision
    OUT.mkdir(exist_ok=True,parents=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'pixel_cavern_coast.blend'))
    bpy.ops.object.select_all(action='DESELECT')
    objects=[o for o in scene.objects if o.type=='MESH' and o.get('pixel_cavern')]
    for ob in objects:ob.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.export_scene.gltf(filepath=str(OUT/'pixel_cavern_coast.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_normals=True,export_texcoords=True,export_materials='EXPORT')
    data={'revision':revision,'source':'empty Blender scene, user image composition','objects':len(objects),'imported_geometry':[],'hero_position_blender':[-4.7,-.3,4.48]}
    (OUT/'design.json').write_text(json.dumps(data,indent=2),encoding='utf-8');print(json.dumps(data))
