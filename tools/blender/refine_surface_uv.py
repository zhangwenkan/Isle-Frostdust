"""Run inside the live Blender session via blender-mcp; edit materials + UV only."""
import bpy, json, math, hashlib, struct
from pathlib import Path
from mathutils import Vector

ROOT = Path('D:/自己做着玩的/孤屿霜尘')
OUT = ROOT/'assets/island_blender'
TEX = OUT/'pixel/surfaces'
DENSITY = 40.0
FILES = {'rock':'coastal_granite.png', 'rock_light':'weathered_granite.png',
         'wet_rock':'coastal_granite.png', 'grass':'coastal_turf.png',
         'moss':'rock_moss.png', 'bark':'pine_bark_scales.png', 'wood':'salt_worn_wood.png'}
SIZES = {}

def geometry_hash():
    h=hashlib.sha256()
    for ob in sorted(bpy.context.scene.objects,key=lambda x:x.name):
        if ob.type!='MESH':continue
        h.update(ob.name.encode())
        for row in ob.matrix_world:
            h.update(struct.pack('4d',*row))
        for v in ob.data.vertices:
            h.update(struct.pack('3d',*v.co))
        for p in ob.data.polygons:
            h.update(struct.pack('%di'%len(p.vertices),*p.vertices))
            h.update(struct.pack('i?',p.material_index,p.use_smooth))
    return h.hexdigest()

before = geometry_hash()
for key,file in FILES.items():
    m=bpy.data.materials[key]
    image=bpy.data.images.load(str(TEX/file),check_existing=True)
    image.reload(); image.colorspace_settings.name='sRGB'; image.pack()
    SIZES[key]=tuple(image.size)
    m.use_nodes=True
    for n in list(m.node_tree.nodes):
        if n.type=='TEX_IMAGE':m.node_tree.nodes.remove(n)
    node=m.node_tree.nodes.new('ShaderNodeTexImage')
    node.name='Surface_Pixel_Albedo';node.label='40 px/m · palette / no dither'
    node.image=image;node.interpolation='Closest';node.extension='REPEAT'
    bsdf=m.node_tree.nodes.get('Principled BSDF')
    m.node_tree.links.new(node.outputs['Color'],bsdf.inputs['Base Color'])
    m['surface_texels_per_meter']=DENSITY
    m['surface_pass']='2026-11-07'

def tube_uv(ob, uv, coords):
    """Unwrap existing ring topology along each trunk/branch; no mesh creation."""
    caps=sorted([p for p in ob.data.polygons if len(p.vertices)>4],key=lambda p:min(p.vertices))
    groups=[]
    for a,b in zip(caps[::2],caps[1::2]):
        n=len(a.vertices);start=min(a.vertices);end=max(b.vertices)+1
        if len(b.vertices)!=n or end<=start or (end-start)%n:continue
        if sorted(a.vertices)!=list(range(start,start+n)):continue
        if sorted(b.vertices)!=list(range(end-n,end)):continue
        rings=[coords[i:i+n] for i in range(start,end,n)]
        centers=[sum(r,Vector())/n for r in rings]
        distance=[0.0]
        for c0,c1 in zip(centers,centers[1:]):distance.append(distance[-1]+(c1-c0).length)
        arcs=[]
        for ring in rings:
            arc=[0.0]
            for j in range(n):arc.append(arc[-1]+(ring[(j+1)%n]-ring[j]).length)
            arcs.append(arc)
        groups.append((start,end,n,distance,arcs))
    done=set()
    for p in ob.data.polygons:
        key=ob.data.materials[p.material_index].name
        if key not in ('bark','wood') or len(p.vertices)!=4:continue
        for start,end,n,distance,arcs in groups:
            if not all(start<=v<end for v in p.vertices):continue
            angles=[(v-start)%n for v in p.vertices]
            seam=0 in angles and n-1 in angles
            w,h=SIZES[key]
            # Integral texel offsets introduce variation while retaining scale.
            offset=(start*13+len(ob.name)*7)%w
            for li in p.loop_indices:
                k=ob.data.loops[li].vertex_index-start
                ring,j=divmod(k,n)
                if seam and j==0:j=n
                uv.data[li].uv=((arcs[ring][j]*DENSITY+offset)/w,
                                (distance[ring]*DENSITY+(start*17)%h)/h)
            done.add(p.index)
            break
    return done,len(groups)

changes=[]
for ob in bpy.context.scene.objects:
    if ob.type!='MESH':continue
    if not any(m and m.name in FILES for m in ob.data.materials):continue
    uv=ob.data.uv_layers.active or ob.data.uv_layers.new(name='UVMap')
    coords=[ob.matrix_world@v.co for v in ob.data.vertices]
    mapped=set();groups=0
    if any(m and m.name in ('bark','wood') for m in ob.data.materials):
        mapped,groups=tube_uv(ob,uv,coords)
    offset=int.from_bytes(hashlib.sha256(ob.name.encode()).digest()[:4],'little')
    changed=len(mapped)
    for p in ob.data.polygons:
        if p.index in mapped:continue
        m=ob.data.materials[p.material_index]
        if not m or m.name not in FILES:continue
        key=m.name;w,h=SIZES[key]
        normal=ob.matrix_world.to_3x3().inverted().transposed()@p.normal
        axis=max(range(3),key=lambda i:abs(normal[i]))
        axes={0:(1,2),1:(0,2),2:(0,1)}[axis]
        if key=='grass':axes=(0,1)
        if key=='wood' and ob.name.startswith('Bridge_Plank_'):
            # Boards run across the bridge (Blender Y). Physical meters in
            # both directions replace one whole tile squeezed across a board.
            axes=(2,1) if axis==0 else (0,1) if axis==2 else (0,2)
        for li in p.loop_indices:
            co=coords[ob.data.loops[li].vertex_index]
            uv.data[li].uv=((co[axes[0]]*DENSITY+offset%w)/w,
                            (co[axes[1]]*DENSITY+(offset//w)%h)/h)
        changed+=1
    ob.data.update()
    changes.append({'object':ob.name,'faces':changed,'tube_components':groups})

after=geometry_hash()
assert before==after,'Geometry changed during a UV-only pass'
report={'authoring':'Blender MCP execute_blender_code', 'texels_per_meter':DENSITY,
        'geometry_sha256_before':before,'geometry_sha256_after':after,
        'geometry_unchanged':True,'materials':FILES,'objects':changes}
(ROOT/'artifacts/surface-review/surface-pass.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'nameless_island.blend'))
print('SURFACE_PASS',len(changes),'objects; geometry hash unchanged;',sum(x['tube_components'] for x in changes),'tube components')

# Export the same model collections, including the authored lens surface.
bpy.ops.object.select_all(action='DESELECT')
count=0
for ob in bpy.context.scene.objects:
    if ob.type=='MESH' and any(not c.name.startswith('90_') for c in ob.users_collection):
        ob.hide_set(False);ob.select_set(True);count+=1
bpy.ops.export_scene.gltf(filepath=str(OUT/'nameless_island.glb'),export_format='GLB',use_selection=True,
    export_yup=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',
    export_cameras=False,export_lights=False,export_extras=True)
manifest=json.loads((OUT/'asset_manifest.json').read_text(encoding='utf-8'))
manifest['surface_pass']={'date':'2026-11-07','texels_per_meter':DENSITY,'objects_updated':len(changes),'geometry_unchanged':True,'provenance':'pixel/surfaces/SOURCES.md'}
(OUT/'asset_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('SURFACE_EXPORT',count,'meshes')
