"""Sculpt continuous coastal cliffs inside Blender through Blender MCP.

Preserve the original walking surface and its UVs exactly. Replace only the
plain perimeter shell with angular buttresses, oblique clefts and broken ledges.
"""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
OUT=ROOT/'artifacts/cliff-form-review'

def clamp(v):return max(0.,min(1.,v))
def smooth(a,b,v):
    t=clamp((v-a)/(b-a));return t*t*(3-2*t)
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def color(h):return tuple(linear(int(h[i:i+2],16)/255) for i in (0,2,4))+(1.,)
def mix(a,b,t):return tuple(x*(1-t)+y*t for x,y in zip(a,b))
def G(p):return Vector((p[0],-p[2],p[1]))
def coll(name):
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in scene.collection.children:scene.collection.children.link(c)
    return c
plants=coll('25_Cliff_Ledge_Plants')
for ob in list(plants.objects):bpy.data.objects.remove(ob,do_unlink=True)
def painted_mat(name,attr):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    nodes=m.node_tree.nodes;nodes.clear()
    p=nodes.new('ShaderNodeBsdfPrincipled');o=nodes.new('ShaderNodeOutputMaterial')
    v=nodes.new('ShaderNodeVertexColor');v.layer_name=attr
    m.node_tree.links.new(v.outputs['Color'],p.inputs['Base Color']);m.node_tree.links.new(p.outputs['BSDF'],o.inputs['Surface'])
    p.inputs['Roughness'].default_value=.96
    return m
rock_mat=painted_mat('Coast_Sculpted_Bedrock','LandscapeColor')
plant_mat=painted_mat('Coast_Cliff_Fern','PlantColor')
stone=color('a3aa98');light=color('b3b9a6');dark=color('76867a');moss=color('5f773f')

# Unequal angular sections define geological ribs, with narrow shaded recesses
# between them. These are connected surfaces, not separate spheres on a wall.
WEST=[(-18.3,1.1,.55),(-15.5,1.6,.90),(-12.2,1.15,.62),(-9.2,1.9,1.10),(-5.9,1.25,.68),(-3.1,1.35,.95),(.2,1.55,.80),(3.6,.85,.40)]
EAST=[(15.1,.8,.42),(17.4,1.25,.76),(20.0,1.7,.90),(23.2,1.3,.72),(25.5,.85,.48)]
fractions=[.018,.055,.105,.16,.23,.29,.34,.40,.46,.52,.59,.65,.71,.78,.85,.92,1.0,1.14]
reports=[];samples={}
for east in [False,True]:
    name='Fish_East_Continuous_Land' if east else 'Fish_West_Continuous_Land'
    ob=scene.objects[name]
    base_name=name+'_Before_Cliff_Forms'
    baseline=bpy.data.meshes.get(base_name)
    if baseline is None:
        baseline=ob.data.copy();baseline.name=base_name;baseline.use_fake_user=True
    n=52 if east else 100;rows=26;count=(n+1)*rows
    boundary=[i*rows for i in range(n+1)]+[n*rows+j for j in range(1,rows)]+[i*rows+rows-1 for i in range(n-1,-1,-1)]+list(range(rows-2,0,-1))
    specs=EAST if east else WEST
    verts=[v.co.copy() for v in list(baseline.vertices)[:count]]
    top_faces=[p for p in baseline.polygons if p.material_index==0]
    faces=[tuple(p.vertices) for p in top_faces]
    colors=[tuple(c.color) for c in list(baseline.color_attributes['LandscapeColor'].data)[:count]]
    mats=[0]*len(faces)
    loop_uv=[]
    uv=baseline.uv_layers.active
    for face in top_faces:
        loop_uv.extend([tuple(uv.data[i].uv) for i in face.loop_indices])
    perimeter=[verts[i] for i in boundary]
    normals=[]
    for j,p in enumerate(perimeter):
        tangent=perimeter[(j+1)%len(perimeter)]-perimeter[(j-1)%len(perimeter)]
        normal=Vector((-tangent.y,tangent.x,0)).normalized()
        radial=p-Vector((20.3 if east else -7.2,0,p.z))
        if normal.dot(radial)<0:normal=-normal
        normals.append(normal)

    def sculpt(j,f):
        p=perimeter[j];x=p.x;z=-p.y;normal=normals[j]
        front=smooth(-1.5,1.0,z)
        side=abs(normal.x)**3
        weight=max(front,.72*side)
        # The rear shell is quieter; exposed front and bridge abutments carry form.
        warp=.30*math.sin(f*3.3+x*.21)+f*.30*math.sin(x*.33)
        rib=0.
        for cx,width,amp in specs:
            u=(x-cx-warp)/width
            # Unequal left/right planar shoulders produce broad broken faces.
            profile=max(0,1-abs(u))
            profile=min(profile*1.25, .95) if u<0 else profile
            rib=max(rib,amp*profile)
        side_rib=.52*(1-abs(math.sin(z*1.7+x*.3)))
        # Two bedding changes are tilted, staggered, and disappear between ribs.
        ledge_a=.30+.045*math.sin(x*.52)+.018*math.sin(x*1.27)
        ledge_b=.66+.055*math.sin(x*.43+1.7)
        shelf_a=.22*max(0,1-abs((f-ledge_a)/.095))*smooth(.12,.72,rib)
        shelf_b=.18*max(0,1-abs((f-ledge_b)/.11))*smooth(.15,.65,rib)
        notch=.06*math.exp(-((f-(ledge_a+.09))/.042)**2)*clamp(rib)
        body=(rib*1.25+side_rib)*smooth(0,.085,f)*(1-.28*smooth(.78,1.14,f))
        # Secondary clefts fork diagonally down the large buttresses.
        cleft_phase=x*1.6+z*.75-f*(.9+.5*math.sin(x*.3))
        cleft=.17*max(0,1-abs(math.sin(cleft_phase))/.18)
        body-=cleft*smooth(.035,.13,f)
        # Broad sea erosion gives a setback under each load-bearing shoulder.
        erosion=.16*math.exp(-((f-.83)/.12)**2)*(1-clamp(rib))
        offset=.035+.31*f+weight*(body+shelf_a+shelf_b-notch-erosion)
        offset*=smooth(0,.07,f)
        y=p.z*(1-f)+(-3.35)*f
        y+=weight*math.sin(min(f,1)*math.pi)*(.18*math.sin(x*.68)+.09*math.sin(x*1.31+f*2))
        out=p+normal*offset;out.z=y
        # Large face values, no fine random texture or tiled crack pattern.
        tone=.27+.48*clamp(rib)+.13*math.sin(x*.47+f*.8)
        c=mix(dark,stone,clamp(tone))
        c=mix(c,light,clamp(shelf_a*1.3+shelf_b)*.55)
        c=mix(c,dark,smooth(.66,1.12,f)*.22)
        fringe=.012+.013*(.5+.5*math.sin(x*.91+z*.6))
        c=mix(c,moss,(1-smooth(fringe,fringe+.022,f))*.65)
        return out,c

    prev=boundary
    for f in fractions:
        current=[]
        for j in range(len(boundary)):
            pos,c=sculpt(j,f);current.append(len(verts));verts.append(pos);colors.append(c)
        for j in range(len(boundary)):
            k=(j+1)%len(boundary)
            faces.append((prev[j],prev[k],current[k],current[j]));mats.append(1)
            loop_uv.extend([(0,0)]*4)
        prev=current
    faces.append(tuple(reversed(prev)));mats.append(1);loop_uv.extend([(0,0)]*len(prev))
    me=bpy.data.meshes.new(name+'_Sculpted_Cliff')
    me.from_pydata(verts,[],faces);me.materials.append(baseline.materials[0]);me.materials.append(rock_mat);me.update()
    ca=me.color_attributes.new(name='LandscapeColor',type='FLOAT_COLOR',domain='POINT')
    ca.data.foreach_set('color',[v for c in colors for v in c])
    uv=me.uv_layers.new(name='CoastUV');uv.data.foreach_set('uv',[v for pair in loop_uv for v in pair])
    for p,mat in zip(me.polygons,mats):p.material_index=mat;p.use_smooth=True
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    me.set_sharp_from_angle(angle=math.radians(34))
    ob.data=me
    ob['cliff_revision']='Connected buttress and bedding sculpt; top vertices and UVs preserved'
    max_top_delta=max((me.vertices[i].co-baseline.vertices[i].co).length for i in range(count))
    assert max_top_delta<1e-6
    reports.append({'name':name,'vertices':len(verts),'faces':len(faces),'preserved_top_vertices':count,'max_top_displacement':max_top_delta})
    # Record selected ledges for plants; roots sit on the modeled shoulder.
    wanted=[-16.0,-11.6,-7.3,-2.9,1.4] if not east else [16.9,20.7,24.3]
    anchors=[]
    for x0 in wanted:
        j=min(range(len(boundary)),key=lambda j:abs(perimeter[j].x-x0)+max(0,1.3+perimeter[j].y)*20)
        f=.27+.045*math.sin(perimeter[j].x*.52)
        p,c=sculpt(j,f)
        anchors.append((p,normals[j],x0))
    samples[name]=anchors

def fern(name,root,outward,seed):
    verts=[];faces=[];colors=[];weights=[]
    tangent=Vector((-outward.y,outward.x,0))
    # Four broad articulated fronds droop out of a sheltered bedding pocket.
    for k in range(5):
        a=(k-2)*.53
        forward=(outward*math.cos(a)+tangent*math.sin(a)).normalized()
        side=Vector((-forward.y,forward.x,0))
        length=.48+.20*(.5+.5*math.sin(seed+k*2.1))
        for j in range(7):
            t=j/6;center=root+forward*(t*length*.52)+Vector((0,0,.13*math.sin(t*math.pi)-t*t*length*.65))
            width=.085*math.sin(math.pi*t*.9)+.012
            base=len(verts)
            verts.extend([center-side*width,center+Vector((0,0,.025)),center+side*width])
            colors.extend([color('4b673a'),color('78904e'),color('607b40')]);weights.extend([t]*3)
            if j:
                faces.extend([(base-3,base,base+1,base-2),(base-2,base+1,base+2,base-1)])
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(plant_mat);me.update()
    ca=me.color_attributes.new(name='PlantColor',type='FLOAT_COLOR',domain='POINT');ca.data.foreach_set('color',[v for c in colors for v in c])
    me.uv_layers.new(name='SurfaceUV');uv=me.uv_layers.new(name='WindWeight')
    for loop in me.loops:uv.data[loop.index].uv=(weights[loop.vertex_index],.5)
    ob=bpy.data.objects.new(name,me);plants.objects.link(ob)
    return ob
for island,anchors in samples.items():
    for i,(p,n,x) in enumerate(anchors):fern('Cliff_Fern_'+('East' if 'East' in island else 'West')+'_%02d'%i,p+n*.025,n,i*1.7)

(OUT/'authoring.json').write_text(json.dumps({'cliffs':reports,'ledge_ferns':len(plants.objects),'method':'Blender MCP; preserved top surface with connected sculpted perimeter'},indent=2),encoding='utf-8')
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
print('CLIFF_FORMS_COMPLETE',json.dumps(reports))
