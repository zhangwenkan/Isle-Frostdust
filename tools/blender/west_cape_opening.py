"""Author a quiet western cape in Blender via MCP, retaining the rest of the coast."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/west-cape-opening-review'
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
archive=bpy.data.collections.get('90_Before_West_Cape') or bpy.data.collections.new('90_Before_West_Cape')
if archive.name not in scene.collection.children:scene.collection.children.link(archive)
def smooth(a,b,x):
    t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
def weight(x):return 1-smooth(-19.05,-15.0,x)
def path(x):return .4+math.sin(x*.25)*.44
def height(x,z):return 1.65+(4.5-x)*.127+math.sin(x*.39)*.16+math.cos(z*1.3+x*.21)*.1+max(0,-z-.3)*.23
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def col(s):return tuple(linear(int(s[i:i+2],16)/255) for i in (0,2,4))+(1.,)
def baseline(name):
    ob=scene.objects[name];saved=bpy.data.objects.get('CapeBaseline_'+name)
    if saved is None:
        saved=ob.copy();saved.data=ob.data.copy();saved.name='CapeBaseline_'+name
        archive.objects.link(saved);saved.hide_set(True);saved.hide_render=True
    return ob,saved
def deform(p):
    x,z,y=p.x,-p.y,p.z;w=weight(x)
    if w==0:return p.copy()
    nx=x-5.9*w;relative=z-path(x)
    # Keep the entire walking strip; broaden its foreground apron and flatten
    # the small rear shoulder into an open cape, with a rounded left lip.
    if relative<-.58:nz=path(nx)-.58+(relative+.58)*(1-.46*w)
    elif relative>.58:nz=path(nx)+.58+(relative-.58)*(1+.70*w)+.85*w*smooth(.58,1.15,relative)
    else:nz=path(nx)+relative
    nx+=.85*(1-smooth(-19.05,-18.15,x))*min(1,abs(relative)/1.8)**2
    rear=(1-math.exp(-max(0,path(x)-z-.7)*.75))*(1.65*math.exp(-((x+12.8)/5.3)**2))
    dy=height(nx,nz)-height(x,z)-rear*w*.88
    return Vector((nx,-nz,y+dy*smooth(-3.0,2.,y)))

land,saved=baseline('Fish_West_Continuous_Land');land.data=saved.data.copy();me=land.data
for v,old in zip(me.vertices,saved.data.vertices):v.co=deform(old.co)
# Shape only the cape's connected cliff shell into a receding, layered flank.
# The inherited eastern ribs remain exactly as authored.
n=100;rows=26;count=2626
boundary=[i*rows for i in range(n+1)]+[n*rows+j for j in range(1,rows)]+[i*rows+rows-1 for i in range(n-1,-1,-1)]+list(range(rows-2,0,-1))
fractions=[.018,.055,.105,.16,.23,.29,.34,.40,.46,.52,.59,.65,.71,.78,.85,.92,1.,1.14]
colors=me.color_attributes['LandscapeColor']
for ring,f in enumerate(fractions):
    for j,bid in enumerate(boundary):
        k=count+ring*len(boundary)+j;old=saved.data.vertices[bid].co;w=weight(old.x)
        if w==0:continue
        p=me.vertices[bid].co.copy()
        tangent=me.vertices[boundary[(j+1)%len(boundary)]].co-me.vertices[boundary[j-1]].co
        normal=Vector((-tangent.y,tangent.x,0)).normalized()
        if normal.dot(p-Vector((-7.2,0,p.z)))<0:normal=-normal
        a=.27+.04*math.sin(p.x*.8);b=.64+.035*math.sin(p.x*.53+1)
        shelf=.15*max(0,1-abs(f-a)/.09)+.12*max(0,1-abs(f-b)/.10)
        offset=.035-.48*smooth(.04,.80,f)+shelf+.045*math.sin(p.x*.93+f*5)*math.sin(min(f,1)*math.pi)
        target=p+normal*offset;target.z=p.z*(1-f)-3.35*f
        me.vertices[k].co=me.vertices[k].co.lerp(target,w)
        base=col('747467');low=col('424e4b');top=col('8c866c')
        t=smooth(.12,1.1,f)
        tint=tuple(base[q]*(1-t)+low[q]*t for q in range(4))
        if f<.10:tint=top
        oldc=colors.data[k].color
        colors.data[k].color=tuple(oldc[q]*(1-w)+tint[q]*w for q in range(4))
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()

# Retire just the detached cape slabs as connected components. Full old mesh
# remains archived. No caps or modeled surfaces are generated in Godot.
fractures,saved=baseline('Cliff_Fractures_West');fractures.data=saved.data.copy()
bm=bmesh.new();bm.from_mesh(fractures.data);unseen=set(bm.verts);removed=0
while unseen:
    seed=unseen.pop();component={seed};stack=[seed]
    while stack:
        v=stack.pop()
        for e in v.link_edges:
            other=e.other_vert(v)
            if other in unseen:unseen.remove(other);component.add(other);stack.append(other)
    if sum(v.co.x for v in component)/len(component)<-15.0:
        removed+=1;bmesh.ops.delete(bm,geom=list(component),context='VERTS')
bm.to_mesh(fractures.data);bm.free();fractures.data.update()
retired=[]
for name in ['Depth_Bamboo_Main_00','Depth_Bamboo_Main_01','Fish_Tidal_Reef_00_Body','Fish_Tidal_Reef_01_Body']:
    ob=bpy.data.objects.get(name)
    if ob is None:continue
    for c in list(ob.users_collection):c.objects.unlink(ob)
    archive.objects.link(ob);ob.hide_set(True);ob.hide_render=True;retired.append(name)

# Existing cape exposure is translated as one object. Its accepted mesh shape,
# normals, UV and proportions are not redesigned by this layout change.
placed=[]
for name in ['InkSample_Rock_00','Coast_Low_Grass_00.003','Coast_Low_Grass_01.003','Coast_Low_Grass_02.003']:
    ob,saved=baseline(name);ob.data=saved.data.copy();ob.matrix_world=saved.matrix_world.copy()
    pts=[saved.matrix_world@v.co for v in saved.data.vertices]
    center=sum(pts,Vector())/len(pts);center.z=min(p.z for p in pts)
    shift=deform(center)-center;ob.location+=shift
    placed.append({'name':name,'translation':list(shift)})
# Move the existing fern to the new continuous flank, using the actual surface.
ob,saved=baseline('Cliff_Fern_West_00');ob.data=saved.data.copy();ob.matrix_world=saved.matrix_world.copy()
uv=ob.data.uv_layers['WindWeight'];ids={l.vertex_index for l in ob.data.loops if uv.data[l.index].uv.x<.001}
root=sum((ob.matrix_world@ob.data.vertices[i].co for i in ids),Vector())/len(ids)
tree=BVHTree.FromPolygons([land.matrix_world@v.co for v in land.data.vertices],[tuple(p.vertices) for p in land.data.polygons])
target=deform(root);hit=tree.find_nearest(target)[0];assert hit is not None
ob.location+=hit-root
bed,saved=baseline('Fish_Seabed');bed.data=saved.data.copy()
for v,old in zip(bed.data.vertices,saved.data.vertices):
    w=(1-smooth(-21.,-10.,old.co.x))
    v.co.z=old.co.z-11.*w
bed.data.update()

exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
p=ROOT/'assets/island_blender/asset_manifest.json';manifest=json.loads(p.read_text(encoding='utf-8'))
manifest['revision']='Western opening cape: extended open turf lip, continuous shaded flank, deeper offshore basin and grove entrance to the right'
ref='../../artifacts/west-cape-opening-review/README.md'
if ref not in manifest['source_manifests']:manifest['source_manifests'].append(ref)
p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'blender-authoring.json').write_text(json.dumps({'retired':retired,'removed_cape_slab_components':removed,'rigid_placements':placed,'start_x':-20.7},indent=2),encoding='utf-8')
print('WEST_CAPE_EXPORTED')
