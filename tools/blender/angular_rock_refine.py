"""Build deliberately cut stone planes inside Blender, dispatched through MCP."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/angular-rock-review'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
def coll(name):
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in scene.collection.children:scene.collection.children.link(c)
    return c
archive=coll('90_Before_Angular_Rocks');active=coll('28_Colored_Ink_Sample')
land=scene.objects['Fish_West_Continuous_Land']
tree=BVHTree.FromPolygons([land.matrix_world@v.co for v in land.data.vertices],[tuple(p.vertices) for p in land.data.polygons])
def ground(x,y):
    hit=tree.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))[0]
    assert hit is not None,(x,y)
    return hit.z

mat=bpy.data.materials.get('InkSample_Rock_Angular') or bpy.data.materials.new('InkSample_Rock_Angular')
mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear()
bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=1
texture=nodes.new('ShaderNodeTexImage');texture.image=bpy.data.images.load(str(ROOT/'assets/colored_ink_sample/angular_rock_planes.png'),check_existing=True);texture.image.reload()
output=nodes.new('ShaderNodeOutputMaterial')
mat.node_tree.links.new(texture.outputs['Color'],bs.inputs['Base Color']);mat.node_tree.links.new(bs.outputs['BSDF'],output.inputs['Surface'])

# Each footprint is intentionally drawn, not a spherical mesh with noise.
# Main block: a broad inclined cap, three unequal front planes, clipped corners.
designs=[
 dict(name='InkSample_Rock_02',center=(-11.35,2.02),width=1.74,depth=1.32,rise=.40,dip=-.32,angle=-7,
      outline=[(-.50,-.24),(-.39,-.47),(-.08,-.50),(.28,-.43),(.48,-.23),(.43,.30),(.18,.48),(-.28,.45),(-.48,.24)],role='Small upright split bedrock, sloping top and hard vertical planes'),
 dict(name='InkSample_Rock_03',center=(-10.51,1.61),width=.76,depth=.81,rise=.17,dip=-.23,angle=-12,
      outline=[(-.48,-.29),(-.29,-.48),(.24,-.45),(.49,-.17),(.37,.40),(-.26,.46),(-.49,.18)],role='Attached chipped foot, smaller and lower'),
 dict(name='InkSample_Rock_04',center=(-6.45,1.95),width=1.35,depth=1.13,rise=.25,dip=-.26,angle=-9,
      outline=[(-.49,-.23),(-.27,-.47),(.18,-.49),(.47,-.20),(.40,.36),(.03,.47),(-.44,.31)],role='Low fractured shoulder with a readable top plane'),
 dict(name='InkSample_Rock_00',center=(-17.8,1.10),width=1.40,depth=.98,rise=.25,dip=.16,angle=6,
      outline=[(-.48,-.28),(-.27,-.47),(.22,-.46),(.48,-.16),(.37,.40),(-.31,.46),(-.49,.15)],role='Quiet entrance block, flat cut top and embedded foot')
]
reports=[]
for d in designs:
    old=scene.objects[d['name']]
    savedname='RoundBaseline_'+d['name']
    if bpy.data.objects.get(savedname) is None:
        saved=old.copy();saved.data=old.data.copy();saved.name=savedname
        archive.objects.link(saved);saved.hide_set(True);saved.hide_render=True
    cx,cy=d['center'];base=ground(cx,cy);a=math.radians(d['angle']);N=len(d['outline'])
    def xy(u,v,s=1):
        x=u*d['width']*s;y=v*d['depth']*s
        return cx+math.cos(a)*x-math.sin(a)*y,cy+math.sin(a)*x+math.cos(a)*y
    crease_a=xy(*d['outline'][2]);crease_b=xy(*d['outline'][N-3])
    ax,ay=crease_a;bx,by=crease_b
    crease_length=math.hypot(bx-ax,by-ay)
    def cap_z(x,y):
        signed=((x-ax)*(by-ay)-(y-ay)*(bx-ax))/crease_length
        return base+d['rise']+d['dip']*(x-cx)+.11*(y-cy)-max(0,signed)*.24
    pts=[]
    for ring in range(2):
        for i,(u,v) in enumerate(d['outline']):
            x,y=xy(u,v)
            z=cap_z(x,y)
            if ring==0:
                # Unequal fracture directions give the vertical edges a small
                # slant, with a broad buried foot and no continuous bevel band.
                slope=[(-.17,.03),(-.08,-.02),(.03,-.05),(.11,.01),(.06,.02),(.03,.03),(-.01,.06),(-.10,.03),(-.12,.01)][i]
                x+=slope[0]*d['width'];y+=slope[1]*d['depth']
                z=ground(x,y)-.34
            pts.append((x,y,z))
    faces=[tuple(reversed(range(N)))];tiles=[15]
    for i in range(N):
        j=(i+1)%N
        faces.append((i,j,N+j,N+i));tiles.append([1,2,3,4,5,7,8,0,4][i])
    # Two broad, genuinely planar top facets meet along an oblique fracture.
    # Neither spherical smoothing nor a regular bevel ring is used.
    faces.append(tuple(N+i for i in [0,1,2]+list(range(N-3,N))));tiles.append(10)
    faces.append(tuple(N+i for i in range(2,N-2)));tiles.append(11)
    me=bpy.data.meshes.new('CutPlanes_'+d['name']);me.from_pydata(pts,[],faces);me.materials.append(mat);me.update()
    old.data=me
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
    uv=me.uv_layers.new(name='AuthoredPlaneAtlas')
    for p,tile in zip(me.polygons,tiles):
        p.use_smooth=False
        # Quads use individual plane UVs: U follows its edge, V follows height.
        # Top/bottom use planar projection, so no repeated front-face cracks.
        for li in p.loop_indices:
            vi=me.loops[li].vertex_index
            if len(p.vertices)==4:
                local=list(p.vertices).index(vi)
                u,v=[(0,0),(1,0),(1,1),(0,1)][local]
            else:
                vtx=me.vertices[vi].co;u=(vtx.x-cx)/d['width']+.5;v=(vtx.y-cy)/d['depth']+.5
            u=.05+.90*u;v=.05+.90*v
            uv.data[li].uv=((tile%4+u)/4,1-(tile//4+1-v)/4)
    for modifier in list(old.modifiers):old.modifiers.remove(modifier)
    old['source_role']=d['role'];old['spatial_design']='Angular rock correction, 2026-11-08'
    old.hide_set(False);old.hide_render=False
    reports.append({**d,'vertices':len(me.vertices),'faces':len(me.polygons),'flat_normals':True,'ground_at_center':base})
(OUT/'blender-authoring.json').write_text(json.dumps({'designs':reports,'width_measurement':'See asset-verification.json for exported world extent comparison','no_smoothed_normals':True,'no_subdivision':True,'geometry_author':'Blender MCP'},ensure_ascii=False,indent=2),encoding='utf-8')
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
p=ROOT/'assets/island_blender/asset_manifest.json';m=json.loads(p.read_text(encoding='utf-8'))
m['revision']='Smaller angular western rocks: sloping caps, vertical fracture faces, hard normals and sparse painted edges'
ref='../../artifacts/angular-rock-review/README.md'
if ref not in m['source_manifests']:m['source_manifests'].append(ref)
p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
print('ANGULAR_ROCKS_EXPORTED',len(reports))
