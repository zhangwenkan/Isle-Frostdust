"""Blender MCP pass: layered mist ridges and sparse underwater life."""
import bpy, bmesh, json, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path('D:/自己做着玩的/孤屿霜尘')
OUT = ROOT / 'artifacts/cinematic-coast-review'
scene = bpy.data.scenes['Island_Refined']
for wm in bpy.data.window_managers:
    for win in wm.windows:
        win.scene = scene
assert Path(bpy.data.filepath).resolve() == (ROOT/'assets/island_blender/nameless_island.blend').resolve()

def collection(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in scene.collection.children:
        scene.collection.children.link(c)
    return c

archive = collection('90_Superseded_Sparse_Peaks')
for old_name in ['21_Misty_Peak_Groups', '22_Mist_Peak_Shoulders']:
    old = bpy.data.collections.get(old_name)
    if old:
        for ob in list(old.objects):
            old.objects.unlink(ob); archive.objects.link(ob); ob.hide_set(True)
ridge_col = collection('23_Layered_Mist_Ridges')
life_col = collection('24_Underwater_Life')
for c in (ridge_col, life_col):
    for ob in list(c.objects):
        bpy.data.objects.remove(ob, do_unlink=True)

def srgb(hex_color):
    return tuple((int(hex_color[i:i+2], 16) / 255.0) ** 2.2 for i in (0, 2, 4)) + (1.0,)

def material(name, color, roughness=0.92):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = srgb(color)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = m.diffuse_color
    p.inputs['Roughness'].default_value = roughness
    return m

mountain_mat = bpy.data.materials.get('Depth_Mountain')
if mountain_mat is None:
    mountain_mat = material('Depth_Mountain', '546b67')
shell_mat = material('Fish_Underwater_Shell', 'c7b79b', 0.88)
shell_shadow = material('Fish_Underwater_Shell_Shadow', '877b6b', 0.95)
fish_mat = material('Fish_Underwater_Swimmer', '426d72', 0.82)
fish_belly = material('Fish_Underwater_Belly', '91aaa0', 0.90)
plant_mat = material('Fish_Underwater_Kelp', '4f8374', 0.95)

def G(p):
    # Godot (x, y, z) -> Blender (x, -z, y).
    return Vector((p[0], -p[2], p[1]))

def mesh_obj(name, verts, faces, mat, col):
    me = bpy.data.meshes.new(name + '_Mesh')
    me.from_pydata([G(v) for v in verts], [], faces)
    me.materials.append(mat)
    me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); col.objects.link(ob)
    return ob

def ridge(name, x, z, top, width, depth, phase, rotation):
    # A connected ridge has unequal crowns, offset saddles and a branching foot.
    # Its outline is sculpted at several scales; no repeating cone or noise texture.
    verts, faces, colors = [], [], []
    nx, nz, base = 92, 30, -8.0
    crowns = [(-.62,.12,.57,.22),(-.20,-.16,.86,.20),(.13,.05,1.0,.18),(.51,.20,.66,.22)]
    for j in range(nz+1):
        v = -1.0 + 2*j/nz
        for i in range(nx+1):
            u = -1.0 + 2*i/nx
            spine = .14*math.sin(u*4.1+phase)
            height = 0.0
            for k,(cx,cz,h,w) in enumerate(crowns):
                cx += .055*math.sin(phase+k*1.7)
                h *= 1+.10*math.sin(phase+k*1.1)
                height += h*math.exp(-((u-cx)/w)**2.0-((v-cz-spine)/(.44+.06*k))**2)
            height = min(height/1.18,1.08)
            # Broken shoulders and oblique rock ribs give each crown a distinct side.
            height = height ** .80
            seam = abs(math.sin(u*24+v*5.0+phase*2.0))
            height *= 1.0-.075*(seam**7.0)*min(1.0,height*3.0)
            ledge = .020*math.sin(v*23+u*9+phase)*height
            height += ledge
            taper = min(1.0,(1-abs(u))*9,(1-abs(v))*5)
            # Long rock buttresses and broken shelves follow the ridge, not fine noise.
            fold = .10*math.sin(u*27+v*5+phase)+.045*math.cos(u*59-v*7+phase)
            h = base+(top-base)*(height+fold*height*.42)*max(0,taper)
            px=u*width; pz=v*depth
            co=math.cos(rotation);si=math.sin(rotation)
            verts.append((x+px*co-pz*si,h,z+px*si+pz*co))
            tone=.50+.29*math.cos(u*24+v*5+phase*2)+.08*math.sin(v*10+phase)
            colors.append((.105+tone*.065,.16+tone*.07,.145+tone*.06,1))
    for j in range(nz):
        for i in range(nx):
            a=j*(nx+1)+i; b=a+1; c=a+nx+1; d=c+1
            faces.extend([(a,c,b),(b,c,d)])
    ob=mesh_obj(name,verts,faces,mountain_mat,ridge_col)
    ca=ob.data.color_attributes.new(name='DepthColor',type='FLOAT_COLOR',domain='POINT')
    ca.data.foreach_set('color',[v for c in colors for v in c])
    for poly in ob.data.polygons: poly.use_smooth=True
    ob['depth_role']='Connected multi-crown ridge; separate cloud valleys between groups'
    return ob

ridge_specs = [
 ('Mist_Ridge_Front_00',-68,-86,8.8,23,10,.2,.18),
 ('Mist_Ridge_Front_01',-28,-94,10.0,22,11,1.4,-.23),
 ('Mist_Ridge_Front_02',15,-83,6.8,20,10,2.7,.19),
 ('Mist_Ridge_Front_03',58,-96,10.8,25,12,4.1,-.17),
 ('Mist_Ridge_Mid_00',-94,-133,14.0,29,13,1.0,-.12),
 ('Mist_Ridge_Mid_01',-44,-143,16.7,31,14,2.0,.21),
 ('Mist_Ridge_Mid_02',7,-132,14.2,28,14,3.2,-.24),
 ('Mist_Ridge_Mid_03',57,-148,18.8,30,13,4.7,.12),
 ('Mist_Ridge_Mid_04',105,-138,13.0,26,12,5.7,-.2),
 ('Mist_Ridge_Far_00',-135,-207,24.0,43,17,1.5,.12),
 ('Mist_Ridge_Far_01',-61,-218,23.5,46,18,2.6,-.15),
 ('Mist_Ridge_Far_02',18,-206,23.3,42,17,3.8,.19),
 ('Mist_Ridge_Far_03',93,-222,25.0,48,18,5.2,-.11),
 ('Mist_Ridge_Far_04',165,-213,22.0,40,17,6.1,.15),
]
for spec in ridge_specs: ridge(*spec)

seabed=bpy.data.objects['Fish_Seabed']
tree=BVHTree.FromObject(seabed,bpy.context.evaluated_depsgraph_get())
def bed_y(x,z):
    hit=tree.ray_cast(Vector((x,-z,10)),Vector((0,0,-1)))[0]
    return hit.z if hit is not None else -5.0

def uv_sphere(name, loc, scale, mat, col, segments=12, rings=7):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings, radius=1.0)
    for v in bm.verts:
        v.co = G((loc[0] + v.co.x * scale[0], loc[1] + v.co.z * scale[1], loc[2] + v.co.y * scale[2]))
    me = bpy.data.meshes.new(name + '_Mesh'); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); col.objects.link(ob)
    for p in me.polygons: p.use_smooth = True
    return ob

def shell(name,x,y,z,scale=1.0,rot=0.0):
    # A fan shell with a convex roof, nine radial ribs and a scalloped lip.
    y=bed_y(x,z)+.018
    verts=[];faces=[]
    rings,arcs=9,40
    for j in range(rings+1):
        r=j/rings
        for k in range(arcs+1):
            a=-1.14+2.28*k/arcs
            rib=.018*math.cos(a*27)*r
            px=math.sin(a)*(.36*r+rib)*scale
            pz=(math.cos(a)*.43*r-.16)*scale
            py=.13*math.sin(math.pi*r*.88)*scale+.009*math.cos(a*27)*r
            co=math.cos(rot);si=math.sin(rot)
            verts.append((x+px*co-pz*si,y+py,z+px*si+pz*co))
    for j in range(rings):
        for k in range(arcs):
            a=j*(arcs+1)+k;b=a+1;c=a+arcs+1;d=c+1
            faces.append((a,c,d,b))
    ob=mesh_obj(name,verts,faces,shell_mat,life_col)
    solid=ob.modifiers.new('Shell thickness','SOLIDIFY');solid.thickness=.016*scale
    bpy.context.view_layer.objects.active=ob;ob.select_set(True)
    bpy.ops.object.modifier_apply(modifier=solid.name);ob.select_set(False)
    return ob

for args in [
 ('Fish_Underwater_Shell_00',6.0,0,2.2,1.0,-.4),
 ('Fish_Underwater_Shell_01',7.1,0,3.0,.75,.3),
 ('Fish_Underwater_Shell_02',10.1,0,2.0,.95,-.1),
 ('Fish_Underwater_Shell_03',12.3,0,2.6,.72,.5),
 ('Fish_Underwater_Shell_04',8.8,0,-1.4,.8,-.8),
 ('Fish_Underwater_Shell_05',13.0,0,-2.5,.62,1.2),
]: shell(*args)

def fish(name, x, y, z, scale=1.0):
    root = bpy.data.objects.new(name, None); life_col.objects.link(root)
    root.location = G((x, y, z))
    body = uv_sphere(name + '_Body', (0, 0, 0), (0.34 * scale, 0.10 * scale, 0.12 * scale), fish_mat, life_col)
    body.parent = root; body.location = (0, 0, 0)
    tail = mesh_obj(name + '_Tail', [(0.22, 0.0, 0.0), (0.42, 0.0, 0.16), (0.42, 0.0, -0.16), (0.42, 0.08, 0.0)], [(0, 1, 3), (0, 3, 2), (0, 2, 1)], fish_belly, life_col)
    tail.parent = root; tail.location = (0, 0, 0)
    root['depth_role'] = 'Sparse shallow-water swimmer visible below bridge'
    return root

for args in [
    ('Fish_Underwater_Swimmer_00', 5.5, -3.22, -0.85, 0.70),
    ('Fish_Underwater_Swimmer_01', 8.4, -3.68, 1.42, 0.54),
    ('Fish_Underwater_Swimmer_02', 11.0, -3.42, -1.72, 0.62),
    ('Fish_Underwater_Swimmer_03', 13.0, -3.85, 0.55, 0.48),
]: fish(*args)

def kelp(name, x, y, z, scale=1.0, phase=0.0):
    # Three broad curved blades, deliberately sparse and readable at bridge distance.
    verts=[]; faces=[]
    for blade in range(3):
        a = math.tau * blade / 3.0 + phase
        side = Vector((math.cos(a), 0, math.sin(a)))
        for j in range(5):
            t = j / 4.0; yy = t * 0.72 * scale
            center = Vector((x, y + yy, z)) + side * (0.06 * scale * t) + Vector((math.sin(t * 2.3 + phase) * 0.09 * scale, 0, math.cos(t * 2.0 + phase) * 0.08 * scale))
            w = 0.035 * scale * (1.0 - t * 0.45)
            verts.extend([(center.x - side.x*w, center.y, center.z - side.z*w), (center.x + side.x*w, center.y, center.z + side.z*w)])
        base = blade * 10
        for j in range(4): faces.append((base+j*2, base+j*2+1, base+j*2+3, base+j*2+2))
    mesh_obj(name, verts, faces, plant_mat, life_col)

kelp('Fish_Underwater_Kelp_00', 6.8, bed_y(6.8,2.6), 2.6, 0.90, 0.2)
kelp('Fish_Underwater_Kelp_01', 10.8, bed_y(10.8,3.0), 3.0, 0.82, 1.7)
kelp('Fish_Underwater_Kelp_02', 12.4, bed_y(12.4,-1.1), -1.1, 0.76, 2.4)

# Export the editable source and the same GLB used by Godot.
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'), 'fish_export.py', 'exec'))
manifest = json.loads((ROOT/'assets/island_blender/asset_manifest.json').read_text(encoding='utf-8'))
manifest['revision'] = 'Cinematic layered mist ridges, sparse bridge-underwater shells, swimmers and kelp'
review_ref = '../../artifacts/cinematic-coast-review/README.md'
if review_ref not in manifest.setdefault('source_manifests', []):
    manifest['source_manifests'].append(review_ref)
(ROOT/'assets/island_blender/asset_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
report = {
    'blender_mcp': True,
    'layered_ridges': len(ridge_specs),
    'underwater_shells': 6,
    'underwater_swimmers': 4,
    'underwater_kelp': 3,
    'source_blend': str(ROOT/'assets/island_blender/nameless_island.blend'),
    'export_glb': str(ROOT/'assets/island_blender/nameless_island.glb'),
}
(ROOT/'artifacts/cinematic-coast-review/authoring.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('CINEMATIC_COAST_ASSETS_COMPLETE', json.dumps(report))
