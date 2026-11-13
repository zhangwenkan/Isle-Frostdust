"""Blender MCP: sculpt interlocking coarse fracture faces into coastal bedrock."""
import bpy,bmesh,math,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
PROTOTYPE=False
col=bpy.data.collections.get('26_Cliff_Fracture_Faces') or bpy.data.collections.new('26_Cliff_Fracture_Faces')
if col.name not in scene.collection.children:scene.collection.children.link(col)
for ob in list(col.objects):bpy.data.objects.remove(ob,do_unlink=True)
mat=bpy.data.materials['Coast_Sculpted_Bedrock']

def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def color(h):return tuple(linear(int(h[i:i+2],16)/255) for i in (0,2,4))+(1,)
palette=[color(c) for c in ['929d8e','a4ab99','879787','9aa48f','aab19e']]
report=[]
for east in [False,True]:
    source=scene.objects['Fish_East_Continuous_Land' if east else 'Fish_West_Continuous_Land']
    baseline=bpy.data.meshes[source.name+'_Before_Cliff_Forms']
    n=52 if east else 100;rows=26
    boundary=[i*rows for i in range(n+1)]+[n*rows+j for j in range(1,rows)]+[i*rows+rows-1 for i in range(n-1,-1,-1)]+list(range(rows-2,0,-1))
    points=[baseline.vertices[i].co.copy() for i in boundary]
    tree=BVHTree.FromObject(source,bpy.context.evaluated_depsgraph_get())
    lengths=[0.]
    for j in range(len(points)):lengths.append(lengths[-1]+(points[(j+1)%len(points)]-points[j]).length)
    def sample(s):
        s=s%lengths[-1]
        j=next(j for j in range(len(points)) if lengths[j+1]>=s)
        f=(s-lengths[j])/(lengths[j+1]-lengths[j]);p=points[j].lerp(points[(j+1)%len(points)],f)
        tangent=(points[(j+1)%len(points)]-points[j]);tangent.z=0;tangent.normalize()
        outward=Vector((-tangent.y,tangent.x,0))
        if outward.dot(p-Vector((20.3 if east else -7.2,0,p.z)))<0:outward=-outward
        return p,tangent,outward
    verts=[];faces=[];cols=[];count=0
    # Alternate long vertical shoulders with staggered shorter slabs.
    for tier in range(3):
        s=.15+tier*.77
        while s<lengths[-1]:
            width=1.25+1.05*(.5+.5*math.sin(s*1.31+tier*2.2))
            p,tangent,outward=sample(s+width*.5)
            if p.y>1.8 or (PROTOTYPE and (east or p.x < -8.5 or p.x > -1.0)):
                s+=width*.87;continue
            # Bridge access is a continuous walking strip, not a rock ledge.
            if tier==0 and ((east and p.x<15.6) or (not east and p.x>3.1)) and abs(-p.y-.25)<1.65:
                s+=width*.87;continue
            height_total=p.z+3.2
            high=p.z-.15 if tier==0 else p.z-height_total*(.25 if tier==1 else .53)+.36*math.sin(s*.7+tier)
            low=p.z-height_total*(.42 if tier==0 else .77 if tier==1 else 1.06)+.20*math.sin(s*1.1)
            height=high-low
            center=p.copy();center.z=(high+low)*.5
            hit=tree.ray_cast(center+outward*4,-outward,8)[0]
            if hit is None:s+=width*.87;continue
            center=hit-outward*.36
            # Nonrectangular broken outline; unequal shoulders and leaning joints.
            outline=[(-.48,-.40),(-.52,.22),(-.29,.50),(.27,.46),(.51,.29),(.43,-.26),(.20,-.50),(-.24,-.48)]
            bm=bmesh.new();cloud=[]
            depth=.40+.21*(.5+.5*math.sin(s*1.2+tier))
            for layer in range(2):
                for k,(u,v) in enumerate(outline):
                    warp=.15*math.sin(s*.83+k*1.7+tier)
                    d=(-.42 if layer==0 else depth+warp)
                    point=center+tangent*(u*width+v*.38*math.sin(s*.9))+Vector((0,0,(v+u*.15*math.sin(s*1.1))*height))+outward*d
                    if tier==0:point.z=min(point.z,p.z-.06)
                    cloud.append(bm.verts.new(point))
            # A diagonal crest on the exposed face creates two large lit planes.
            cloud.append(bm.verts.new(center+tangent*(-.12*width)+Vector((0,0,.22*height))+outward*(depth+.14)))
            cloud.append(bm.verts.new(center+tangent*(.15*width)+Vector((0,0,-.22*height))+outward*(depth+.10)))
            hull=bmesh.ops.convex_hull(bm,input=cloud,use_existing_faces=False)
            unused=[v for v in bm.verts if not v.link_faces]
            if unused:bmesh.ops.delete(bm,geom=unused,context='VERTS')
            # Bevel only actual fracture boundaries. Coplanar hull triangulation
            # edges are construction lines and must not become surface stripes.
            bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
            fracture_edges=[e for e in bm.edges if e.is_manifold and e.calc_face_angle(0)>math.radians(24)]
            bmesh.ops.bevel(bm,geom=fracture_edges,offset=.065,segments=2,affect='EDGES',clamp_overlap=True)
            bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.verts.ensure_lookup_table();bm.verts.index_update()
            start=len(verts);verts.extend([v.co.copy() for v in bm.verts])
            c=palette[(count+tier*2)%len(palette)];cols.extend([c]*len(bm.verts))
            for face in bm.faces:faces.append(tuple(start+v.index for v in face.verts))
            bm.free();count+=1;s+=width*.87
    if verts:
        me=bpy.data.meshes.new('Cliff_Fractures');me.from_pydata(verts,[],faces);me.materials.append(mat);me.update()
        ca=me.color_attributes.new(name='LandscapeColor',type='FLOAT_COLOR',domain='POINT');ca.data.foreach_set('color',[v for c in cols for v in c])
        ob=bpy.data.objects.new('Cliff_Fractures_'+('East' if east else 'West'),me);col.objects.link(ob)
        ob['form']='Embedded interlocking fracture slabs on continuous bedrock shell'
    report.append({'island':source.name,'fracture_faces':count})
(ROOT/'artifacts/cliff-form-review/fracture-authoring.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
print('CLIFF_FRACTURES',json.dumps(report))
