"""Hand-hewn timber and quiet rope forms, authored only through Blender MCP."""
import bpy,bmesh,math,json,hashlib,bisect
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/ink-bridge-review'
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
def active():return [o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
def signature(o):
    m=o.data
    return hashlib.sha256(json.dumps({'v':[list(v.co) for v in m.vertices],'p':[list(p.vertices) for p in m.polygons],
      'n':[list(n.vector) for n in m.corner_normals],'uv':[[list(d.uv) for d in u.data] for u in m.uv_layers],
      'matrix':[list(r) for r in o.matrix_world]},separators=(',',':')).encode()).hexdigest()
before={o.name:signature(o) for o in active() if not o.name.startswith('Bridge_')}
arc=bpy.data.collections.get('90_Before_Ink_Bridge')
if arc is None:arc=bpy.data.collections.new('90_Before_Ink_Bridge');scene.collection.children.link(arc)
arc.hide_render=True
bridge=bpy.data.collections['07_Bridge']
def baseline(o):
    s=bpy.data.objects.get('InkBridgeBaseline_'+o.name)
    if s is None:
        s=o.copy();s.data=o.data.copy();s.name='InkBridgeBaseline_'+o.name;arc.objects.link(s);s.hide_set(True);s.hide_render=True
    return s
def stash(o):
    for c in list(o.users_collection):c.objects.unlink(o)
    arc.objects.link(o);o.hide_set(True);o.hide_render=True
def material(name,image):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    nodes=m.node_tree.nodes;nodes.clear();bs=nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=1
    bs.inputs['Specular IOR Level'].default_value=0
    tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/image),check_existing=True);tex.image.reload()
    tex.interpolation='Closest';out=nodes.new('ShaderNodeOutputMaterial')
    m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);m.node_tree.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    return m
wood=material('InkBridge_Wood','assets/ink_bridge/wood-brush.png')
end=material('InkBridge_End','assets/ink_bridge/wood-brush.png')
rope=material('InkBridge_Rope','assets/ink_bridge/rope-brush.png')
binding=material('InkBridge_Binding','assets/ink_bridge/rope-brush.png')
def atlas(u,v,k):return ((k%4*40+4+max(0,min(1,u))*32)/160,1-(k//4*136+4+max(0,min(1,v))*128)/272)
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def hit(t,x,y):
    h=t.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))[0]
    return h.z if h else None
samples=[];plank_reports=[]
for i in range(39):
    ob=scene.objects['Bridge_Plank_%02d'%i];saved=baseline(ob);oldtree=tree(saved)
    ob.data=saved.data.copy();me=ob.data
    pts=[v.co.copy() for v in me.vertices];lo=Vector([min(p[k] for p in pts) for k in range(3)]);hi=Vector([max(p[k] for p in pts) for k in range(3)])
    cx=(lo.x+hi.x)*.5;cy=(lo.y+hi.y)*.5;top=hit(oldtree,cx,cy);samples.append((cx,top-.045))
    # Keep every upper bevel and walking face, giving only the underside more
    # timber thickness. No board is lowered, rotated or widened into its gap.
    changed=0
    for v in me.vertices:
        top_here=hit(oldtree,v.co.x*.999+cx*.001,v.co.y*.999+cy*.001)
        if top_here is None:top_here=top
        d=top_here-v.co.z;t=max(0,min(1,(d-.035)/.075));t=t*t*(3-2*t)
        if t>0:v.co.z-=t*(.055+.012*math.sin(i*1.7));changed+=1
    me.materials.clear();me.materials.append(wood);me.materials.append(end)
    uv=me.uv_layers[0];uv.name='BridgeBrushAtlas'
    for p in me.polygons:
        p.material_index=1 if abs(p.normal.y)>.75 else 0
        for li in p.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co
            if abs(p.normal.y)>.75:u=(v.x-lo.x)/(hi.x-lo.x);vcoord=(v.z-lo.z+.08)/(hi.z-lo.z+.08)
            else:u=(v.x-lo.x)/(hi.x-lo.x);vcoord=(v.y-lo.y)/(hi.y-lo.y)
            uv.data[li].uv=atlas(u,vcoord,(i*5+i//4)%8)
    me.update();newtree=tree(ob);errors=[]
    for fx in [.18,.5,.82]:
        for fy in [.12,.28,.5,.72,.88]:
            x=lo.x+(hi.x-lo.x)*fx;y=lo.y+(hi.y-lo.y)*fy
            a=hit(oldtree,x,y);b=hit(newtree,x,y)
            assert a is not None and b is not None
            errors.append(abs(a-b))
    assert max(errors)<1e-5
    plank_reports.append({'object':ob.name,'changed_lower_vertices':changed,'walk_top_delta_m':max(errors)})

def ground(x):
    j=max(0,min(len(samples)-2,bisect.bisect_left([s[0] for s in samples],x)-1))
    a,ya=samples[j];b,yb=samples[j+1];t=max(0,min(1,(x-a)/(b-a)));return ya+(yb-ya)*t
def G(p):return Vector((p[0],-p[2],p[1]))

class Batch:
    def __init__(self):self.v=[];self.faces=[];self.uv=[]
    def tube(self,points,radii,sides=6,kind='rope',variant=0,hewn=False):
        pts=[Vector(p) for p in points];offset=len(self.v);dist=[0.]
        for a,b in zip(pts,pts[1:]):dist.append(dist[-1]+(b-a).length)
        profile=[(-.50,-.34),(-.30,-.50),(.40,-.46),(.50,-.26),(.45,.41),(.25,.50),(-.43,.45),(-.51,.18)]
        for i,p in enumerate(pts):
            axis=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized()
            ref=Vector((0,0,1)) if abs(axis.z)<.9 else Vector((1,0,0))
            u=axis.cross(ref).normalized();v=axis.cross(u).normalized()
            for j in range(sides):
                if hewn:
                    a,b=profile[j];a*=1+.04*math.sin(i*2.1+variant);b*=1+.04*math.cos(i+variant)
                    q=p+(u*a+v*b)*radii[i]*2
                else:
                    a=j*math.tau/sides;q=p+(u*math.cos(a)+v*math.sin(a))*radii[i]
                self.v.append(tuple(G(q)))
        for i in range(len(pts)-1):
            for j in range(sides):
                a=offset+i*sides+j;b=offset+i*sides+(j+1)%sides
                self.faces.append((a,b,b+sides,a+sides))
                if kind=='wood':
                    # Each broad hewn face gets long-axis brush coordinates.
                    self.uv.append([atlas(0,dist[i]/max(dist[-1],.001),variant),atlas(1,dist[i]/max(dist[-1],.001),variant),atlas(1,dist[i+1]/max(dist[-1],.001),variant),atlas(0,dist[i+1]/max(dist[-1],.001),variant)])
                else:
                    self.uv.append([(j/sides,dist[i]/.75),((j+1)/sides,dist[i]/.75),((j+1)/sides,dist[i+1]/.75),(j/sides,dist[i+1]/.75)])
        for ring,reverse in [(0,True),(len(pts)-1,False)]:
            ids=list(range(sides));ids=ids[::-1] if reverse else ids
            self.faces.append(tuple(offset+ring*sides+j for j in ids))
            self.uv.append([atlas(.5+math.cos(j*math.tau/sides)*.4,.5+math.sin(j*math.tau/sides)*.4,variant) if kind=='wood' else (.5+math.cos(j*math.tau/sides)*.4,.5+math.sin(j*math.tau/sides)*.4) for j in ids])
    def finish(self,name,mat,smooth):
        ob=scene.objects[name];baseline(ob)
        me=bpy.data.meshes.new(name+'_InkMesh');me.from_pydata(self.v,[],self.faces);me.materials.append(mat);me.update();ob.data=me
        uv=me.uv_layers.new(name='LongAxisBrush')
        for p,coords in zip(me.polygons,self.uv):
            p.use_smooth=smooth and len(p.vertices)==4
            for li,coord in zip(p.loop_indices,coords):uv.data[li].uv=coord
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
        return ob

supports=Batch();rails=Batch();knots=Batch();post_positions=[]
for side in [-1,1]:
    z=.25+side*.93
    for i in range(8):
        x=4.2+i*10.3/7;y=ground(x);tilt=.025*side+.012*math.sin(i*2.0)
        top=1.05+.035*math.sin(i*2.3+side)
        supports.tube([(x,y-.27,z),(x+tilt*.45,y+.44,z+.009*math.sin(i)),(x+tilt,y+top,z+.016*math.sin(i))],[.085,.080,.070],8,'wood',(i+3)%8,True)
        post_positions.append((x,y,z))
        for band in [.46,.96]:
            # Two broad turns sit on the actual post. Fewer larger bands read
            # as binding at the game camera instead of a stack of bright rings.
            points=[]
            for j in range(25):
                a=j*math.tau/12;h=band-.028+j*.0026
                points.append((x+tilt*h/top+.092*math.cos(a),y+h,z+.092*math.sin(a)))
            knots.tube(points,[.017]*len(points),5)
        if i in [0,3,7]:
            knots.tube([(x+.04,y+.50,z),(x+.10,y+.36,z+.025),(x+.095,y+.28,z+.03)],[.018,.017,.014],5)
    for h,radius in [(.46,.030),(.96,.037),(-.13,.050)]:
        points=[]
        for span in range(7):
            for j in range(8):
                t=j/8;x=4.2+(span+t)*10.3/7
                sag=math.sin(t*math.pi)*(.09+.012*math.sin(span*1.9+side)) if h>0 else 0
                points.append((x,ground(x)+h-sag,z))
        points.append((14.5,ground(14.5)+h,z))
        rails.tube(points,[radius]*len(points),6)
for i,x in enumerate([4.4,14.2]):
    for z in [-.55,1.05]:supports.tube([(x,-2.4,z),(x,ground(x)+.10,z)],[.14,.115],8,'wood',4+i,True)
    for a,b in [(-.55,1.05),(1.05,-.55)]:supports.tube([(x,-1.8,a),(x,ground(x)-.2,b)],[.068,.060],8,'wood',2+i,True)
supports.finish('Bridge_Weathered_Posts_Cross_Braces',wood,False)
rails.finish('Bridge_Sagging_Rope_Rails',rope,True)
knots.finish('Bridge_Hand_Tied_Bindings_and_Twisted_Fibres',binding,True)
removed=[]
for name in ['Bridge_Plank_Grain_Grooves','Bridge_Wooden_Pegs']:
    ob=scene.objects.get(name)
    if ob and not any(c.name.startswith('90_') for c in ob.users_collection):stash(ob)
    removed.append(name)
after={o.name:signature(o) for o in active() if not o.name.startswith('Bridge_')}
assert before==after,'Unrelated scene mesh changed'
triangles=0
for o in active():
    if o.name.startswith('Bridge_'):o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
report={'planks':plank_reports,'walking_surface_samples':39*15,'max_walking_surface_delta_m':max(p['walk_top_delta_m'] for p in plank_reports),
 'archived':removed,'bridge_triangles':triangles,'baseline_triangles':55912,'unrelated_meshes_identical':len(before),
 'geometry_author':'Blender MCP live scene; no external model generation', 'post_count':16,'rail_strands':6,'bindings':32}
(O/'blender-authoring.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
p=R/'assets/island_blender/asset_manifest.json';m=json.loads(p.read_text(encoding='utf-8'))
m['revision']='Colored ink bridge: quiet wood washes, hand-hewn posts and simple thick rope; walking tops preserved'
ref='../../artifacts/ink-bridge-review/README.md'
if ref not in m['source_manifests']:m['source_manifests'].append(ref)
p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
print('INK_BRIDGE_EXPORTED',triangles,'triangles; walking delta',report['max_walking_surface_delta_m'],'unrelated',len(before))
