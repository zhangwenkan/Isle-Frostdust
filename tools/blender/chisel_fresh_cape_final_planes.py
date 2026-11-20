"""Large oblique cuts instead of evenly bevelled columns; Blender MCP only."""
import bpy,bmesh,math,json
from mathutils import Vector
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Fresh_Pixel_Cape'];bpy.context.window.scene=scene
assert scene['revision']=='fresh-cape-stone-steps-clarity-2'
rockcol=bpy.data.collections['Fresh_02_Rock_Faces'];staircol=bpy.data.collections['Fresh_03_Stairway']
stone=bpy.data.materials['Fresh_Clean_Stone'];stone_lip=bpy.data.materials['Fresh_Clean_Stone_Lip'];side=bpy.data.materials['Fresh_Clean_Stone_Side']
source=(root/'tools/blender/refine_fresh_cape_stone_steps.py').read_text(encoding='utf-8')
exec(source[source.index('def mesh('):source.index('# The front has')],globals())

def clip(bm,point,normal):
    result=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=point,plane_no=normal,clear_outer=True,clear_inner=False)
    edges=[e for e in result['geom_cut'] if isinstance(e,bmesh.types.BMEdge) and e.is_boundary]
    if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0)

for index,ob in enumerate(list(rockcol.objects)):
    if not ob.name.startswith('Rock_') or ob.name in ['Rock_Terrace_Slab','Rock_Bamboo_Buried']:continue
    coords=[v.co for v in ob.data.vertices];lo=Vector(tuple(min(v[a] for v in coords) for a in range(3)));hi=Vector(tuple(max(v[a] for v in coords) for a in range(3)));c=(lo+hi)*.5;sz=hi-lo
    # Rebuild the same new stone's envelope as an oblique polyhedron, then cut
    # only selected corners. Broad final surfaces are exact planes.
    bm=bmesh.new();bmesh.ops.create_cube(bm,size=1)
    for v in bm.verts:v.co=Vector((v.co.x*sz.x,v.co.y*sz.y,v.co.z*sz.z))+c
    cuts=[
        (Vector((c.x,lo.y+sz.y*.18,hi.z-sz.z*.20)),Vector((.10 if index%2 else -.20,-.55,.82))),
        (Vector((hi.x-sz.x*.16,c.y,hi.z-sz.z*.12)),Vector((.72,.09,.62))),
        (Vector((lo.x+sz.x*.12,lo.y+sz.y*.15,c.z)),Vector((-.72,-.69,.12))),
        (Vector((hi.x-sz.x*.12,lo.y+sz.y*.13,c.z)),Vector((.78,-.62,-.04))),
        (Vector((c.x,lo.y+sz.y*.05,lo.z+sz.z*.15)),Vector((.08,-.77,-.63))),
        (Vector((c.x,c.y,hi.z-sz.z*.045)),Vector(((-.10 if index%2 else .075),.06,1)))
    ]
    for point,normal in cuts:clip(bm,point,normal)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    ob.data.materials.clear();ob.data.materials.append(stone)
    for p in ob.data.polygons:p.material_index=0
    uv=ob.data.uv_layers.get('UVMap') or ob.data.uv_layers.new(name='UVMap')
    for li,l in enumerate(ob.data.loops):q=ob.data.vertices[l.vertex_index].co;uv.data[li].uv=(q.x*.2,q.z*.2+q.y*.05)

# Replace the exposed monotonous staircase slope by two natural rock beds.
# These stay behind the tread front; the upper pieces carry each slab's underside.
for ob in list(staircol.objects):
    if 'Embedded_Rockbed' not in ob.name:continue
    # Break the smooth side face at different heights and setbacks without
    # adding upright per-tread seams.
    bm=bmesh.new();bm.from_mesh(ob.data)
    for v in bm.verts:
        if v.co.z>0:v.co.z-=.09
    bm.to_mesh(ob.data);bm.free()

# Interlocking stone masses along the near side, covering the sheer foundations.
def bed(name,poly,low,high,slope):
    n=len(poly);cx=sum(x for x,y in poly)/n
    vs=[(x,y,low) for x,y in poly]+[(x+.015,y+.04,high+slope*(x-cx)) for x,y in poly]
    fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,vs,fs,rockcol,[stone,stone_lip],bevel=.02)

bed('Stair_Bed_Low_Stratum',[(-.65,-2.72),(-.7,-3.15),(.23,-3.40),(1.54,-3.37),(2.20,-2.91),(2.02,-2.59)],-.49,1.02,-.19)
bed('Stair_Bed_Upper_Stratum',[(-.75,-2.55),(-.68,-2.95),(.16,-3.08),(.93,-3.04),(1.43,-2.73),(1.35,-2.43)],.92,1.97,-.25)
bed('Stair_Bed_Lower_Foot',[(3.25,-3.06),(3.40,-3.62),(4.37,-4.07),(5.20,-4.15),(5.52,-3.74),(4.65,-3.27)],-.44,.49,-.16)

# Visible changes in tread shape: chips large enough to read at the native grid,
# one worn corner per selected slab. Every stone remains a full solid.
for ob in staircol.objects:
    if '_Tread_' not in ob.name:continue
    i=int(ob.name.split('_Tread_')[1][:2]);lower=ob.name.startswith('Lower')
    coords=[v.co for v in ob.data.vertices];c=sum(coords,Vector())/len(coords)
    d=Vector((1,-.48 if lower else -.09,0)).normalized();p=Vector((-d.y,d.x,0));top=max(v.z for v in coords)
    maxu=max((q-c).dot(d) for q in coords);minw=min((q-c).dot(p) for q in coords)
    bm=bmesh.new();bm.from_mesh(ob.data)
    if i%3!=1:
        point=c+d*(maxu-.075)+p*(minw+.085);point.z=top-.025
        clip(bm,point,(d-p+Vector((0,0,.18))).normalized())
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()

scene['revision']='fresh-cape-stone-steps-clarity-3'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/fresh_pixel_cape/fresh_pixel_cape.blend'))
print(json.dumps({'revision':scene['revision']}))
