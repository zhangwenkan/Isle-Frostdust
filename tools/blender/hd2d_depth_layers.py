"""Blender MCP authoring: layered coastal ridges, bamboo groves and near cliff framing."""
import bpy,bmesh,math,random,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Island_Refined']
for wm in bpy.data.window_managers:
    for win in wm.windows:win.scene=scene
assert Path(bpy.data.filepath).name=='nameless_island.blend'
OUT=ROOT/'artifacts/depth-composition-review'

def G(p):return Vector((p[0],-p[2],p[1]))
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def color(h):return tuple(linear(int(h[i:i+2],16)/255) for i in (0,2,4))+(1,)
def blend(a,b,t):return tuple(x*(1-t)+y*t for x,y in zip(a,b))

def collection(name):
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in scene.collection.children:scene.collection.children.link(c)
    for ob in list(c.objects):bpy.data.objects.remove(ob,do_unlink=True)
    return c

far=collection('17_Distant_Coastal_Ridges')
forest=collection('18_Bamboo_Depth_Groves')
near=collection('19_Foreground_Cliffs')
archive=bpy.data.collections.get('90_Retired_Palms') or bpy.data.collections.new('90_Retired_Palms')
if archive.name not in scene.collection.children:scene.collection.children.link(archive)
for ob in list(scene.objects):
    if ob.name.startswith('Coast_Palm_'):
        for c in list(ob.users_collection):c.objects.unlink(ob)
        archive.objects.link(ob);ob.hide_set(True)

def material(name,h):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    m.node_tree.nodes.clear();n=m.node_tree.nodes
    bs=n.new('ShaderNodeBsdfPrincipled');out=n.new('ShaderNodeOutputMaterial')
    bs.inputs['Base Color'].default_value=color(h);bs.inputs['Roughness'].default_value=.94
    m.node_tree.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    vc=n.new('ShaderNodeVertexColor');vc.layer_name='DepthColor';m.node_tree.links.new(vc.outputs['Color'],bs.inputs['Base Color'])
    m.diffuse_color=color(h);return m

rockmat=material('Depth_Cliff','87958a')
mountmat=material('Depth_Mountain','879ca0')
stalkmat=material('Depth_Bamboo_Stem','667d43')
leafmat=material('Depth_Bamboo_Canopy','476f3c')

class Mesh:
    def __init__(self):self.v=[];self.f=[];self.c=[];self.m=[]
    def face(self,points,c,mi=0):
        start=len(self.v);self.v.extend(points);self.c.extend([c]*len(points));self.f.append(tuple(range(start,start+len(points))));self.m.append(mi)
    def tube(self,points,radii,c,mi=0,sides=7):
        points=[Vector(p) for p in points];starts=[]
        for i,p in enumerate(points):
            tangent=(points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized()
            ref=Vector((0,1,0)) if abs(tangent.y)<.9 else Vector((1,0,0))
            u=tangent.cross(ref).normalized();v=tangent.cross(u).normalized();starts.append(len(self.v))
            for j in range(sides):
                self.v.append(tuple(p+(u*math.cos(j*math.tau/sides)+v*math.sin(j*math.tau/sides))*radii[i]))
                self.c.append(blend(c,color('94a66c'),.10*max(0,math.cos(j*math.tau/sides))))
        for i in range(len(points)-1):
            for j in range(sides):self.f.append((starts[i]+j,starts[i]+(j+1)%sides,starts[i+1]+(j+1)%sides,starts[i+1]+j));self.m.append(mi)
        self.f.extend([tuple(starts[0]+j for j in reversed(range(sides))),tuple(starts[-1]+j for j in range(sides))]);self.m.extend([mi,mi])
    def leaf(self,p,tip,width,c):
        p=Vector(p);tip=Vector(tip);d=tip-p
        flat=d.cross(Vector((0,1,0))).normalized()
        upright=d.normalized().cross(flat).normalized()
        tilt=.65+.55*(.5+.5*math.sin(p.x*3.2+p.y*1.8+p.z*2.1))
        side=(flat*math.cos(tilt)+upright*math.sin(tilt))*width
        mid=p+d*.43+Vector((0,.025,0));end=p+d*.76
        ids=len(self.v)
        self.v.extend([tuple(p),tuple(mid+side),tuple(mid+Vector((0,.025,0))),tuple(mid-side),tuple(end+side*.52),tuple(end-side*.52),tuple(tip)])
        self.c.extend([blend(c,color('7d9c56'),t) for t in [.0,.0,.18,.06,.1,.03,.16]])
        for f in [(0,1,2),(0,2,3),(1,4,2),(2,5,3),(2,4,6),(2,6,5)]:self.f.append(tuple(ids+j for j in f));self.m.append(1)
    def finish(self,name,col,mats,smooth=False):
        me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata([G(p) for p in self.v],[],self.f);me.update()
        ob=bpy.data.objects.new(name,me);col.objects.link(ob)
        for m in mats:me.materials.append(m)
        for p,mi in zip(me.polygons,self.m):p.material_index=mi;p.use_smooth=smooth
        colors=me.color_attributes.new(name='DepthColor',type='FLOAT_COLOR',domain='POINT')
        for item,c in zip(colors.data,self.c):item.color=c
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
        return ob

# Hand-composed silhouettes: paired shoulders and valleys, three real depth ranges.
def ridge(name,profile,cz,width,base,palette,col):
    mesh=Mesh();levels=[0,.12,.27,.43,.60,.76,.90,1.0]
    controls=profile;profile=[]
    for i in range(len(controls)-1):
        p0=controls[max(0,i-1)];p1=controls[i];p2=controls[i+1];p3=controls[min(len(controls)-1,i+2)]
        steps=max(3,int((p2[0]-p1[0])/2.4))
        for step in range(steps):
            t=step/steps;h=.5*((2*p1[1])+(-p0[1]+p2[1])*t+(2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t*t+(-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t*t*t)
            profile.append((p1[0]+(p2[0]-p1[0])*t,h))
    profile.append(controls[-1])
    for side in [-1,1]:
        rows=[]
        for j,t in enumerate(levels):
            row=[]
            for i,(x,h) in enumerate(profile):
                shoulder=.14*math.sin(x*.16)+.08*math.cos(x*.37)
                z=cz+side*width*((1-t)**.67)*(1+shoulder)+math.sin(x*.11)*width*.12
                x1=x+math.sin(x*.21+j*.6)*(1-t)*width*.07
                y=base+(h-base)*t+math.sin(x*.3+j*.8)*math.sin(t*math.pi)*.38
                row.append(len(mesh.v));mesh.v.append((x1,y,z))
                tone=.28+.35*t+.1*math.sin(x*.27)
                c=blend(color(palette[0]),color(palette[1]),tone)
                vegetation=(.5+.5*math.sin(x*.17+j*.6))*(.65 if t>.6 else .18)
                if name=='Depth_Forest_Shore':vegetation=.70 if t>.55 else .25
                mesh.c.append(blend(c,color(palette[2]),vegetation))
            rows.append(row)
        for j in range(len(rows)-1):
            for i in range(len(profile)-1):
                a,b=rows[j][i],rows[j][i+1];c1,d=rows[j+1][i+1],rows[j+1][i]
                mesh.f.extend([(a,b,c1),(a,c1,d)]);mesh.m.extend([0,0])
    ob=mesh.finish(name,col,[mountmat if col==far else rockmat],smooth=True);ob['depth_role']=name
    return ob

ridge('Depth_Far_Ridge',[(-160,7),(-145,11),(-125,17),(-110,14),(-96,20),(-82,16),(-65,10),(-48,16),(-35,21),(-24,17),(-12,12),(2,16),(18,22),(29,20),(40,13),(54,17),(71,21),(87,16),(104,20),(126,13),(150,8)],-142,22,-5,['9aaeb2','b6c9c8','9db6b0'],far)
ridge('Depth_Middle_Ridge',[(-92,3),(-78,6),(-67,11),(-58,7),(-46,14),(-40,12),(-30,5),(-20,8),(-13,12),(-4,7),(7,3),(18,7),(27,13),(34,15),(43,9),(53,6),(67,11),(80,7),(94,3)],-83,18,-4,['728b8a','99b0a6','66877b'],far)
bank_profile=[(-58,-1),(-48,.2),(-36,1),(-27,.2),(-20,1.2),(-13,.5),(-6,.2),(2,-.1),(10,.6),(18,1.0),(26,.7),(36,.2),(49,.7),(61,-1)]
bank=ridge('Depth_Forest_Shore',bank_profile,-36,7,-3,['5c766b','839582','4e7046'],far)

# Terrain queries are performed against the authored mesh, never guessed roots.
land=[scene.objects[n] for n in ['Fish_West_Continuous_Land','Fish_East_Continuous_Land']]
def bvh(ob):return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons])
grounds=[bvh(ob) for ob in land];bank_bvh=bvh(bank)
def height(x,z,trees=grounds):
    hits=[b.ray_cast(G((x,50,z)),Vector((0,0,-1))) for b in trees]
    return max((p.z for p,n,i,d in hits if p is not None),default=None)

# Four botanical clump variants: thin tapered culms, raised node collars,
# lateral twigs and drooping lanceolate leaves. Each clump is a single mesh.
def bamboo(name,cx,cz,scale,seed,count=8,front=False,base=None,support=None):
    rng=random.Random(seed);mesh=Mesh();used=[]
    for k in range(count):
        a=k*2.39996;rad=.22+math.sqrt((k+.3)/count)*1.00*scale
        x=cx+math.cos(a)*rad;z=cz+math.sin(a)*rad*.7
        y=base if base is not None else height(x,z,support if support is not None else grounds)
        if y is None:continue
        y-=.06;used.append((x,y,z))
        H=rng.uniform(3.8,5.8)*scale;R=rng.uniform(.045,.072)*scale
        lean=Vector((rng.uniform(-.9,.9),0,rng.uniform(-.6,.6)))*scale
        def center(t):return Vector((x,y+H*t,z))+lean*t*t
        segments=max(8,int(H/.48))
        for j in range(segments):
            lo=j/segments;hi=(j+1)/segments;r=R*(1-.66*lo)
            c=blend(color('516b37'),color('859450'),rng.uniform(.05,.45))
            mesh.tube([center(lo),center(hi)],[r,r*.97],c)
            cp=center(hi);tangent=(center(min(1,hi+.01))-center(max(0,hi-.01))).normalized()
            mesh.tube([cp-tangent*.022*scale,cp,cp+tangent*.016*scale],[r*1.10,r*1.16,r*1.04],color('a0a16a'))
        for j in range(7):
            t=.38+j*.085+rng.uniform(-.060,.060);angle=a+j*2.4+rng.uniform(-.65,.65)
            length=rng.uniform(.85,1.45)*scale*(1.1-abs(t-.70))
            direction=Vector((math.cos(angle),rng.uniform(.10,.42),math.sin(angle)))
            start=center(t);elbow=start+direction*length*.55;end=start+direction*length+Vector((0,-.28*scale,0))
            mesh.tube([start,elbow,end],[.017*scale,.011*scale,.003*scale],color('566a36'),sides=5)
            for spray in range(3):
                anchor=start+(end-start)*(.36+spray*.26)
                cross=Vector((-direction.z,0,direction.x))
                handed=-1 if spray%2==0 else 1
                twig=(direction*.65+cross*handed*.6).normalized()*rng.uniform(.55,.8)*scale
                twig_end=anchor+twig+Vector((0,-.22*scale,0))
                mesh.tube([anchor,anchor+twig*.45,twig_end],[.007*scale,.004*scale,.0015*scale],color('596d3b'),sides=4)
                for leaf in range(6):
                    v=.16+leaf*.14;sign=-1 if leaf%2==0 else 1
                    p=anchor+twig*v+Vector((0,-.22*v*v*scale,0))
                    ld=(twig.normalized()*(.30+.4*v)+cross*sign*rng.uniform(.5,.9)).normalized()
                    L=rng.uniform(.34,.55)*scale
                    tip=p+ld*L+Vector((0,(-.15-.15*v)*scale,0))
                    c=blend(color('335c35'),color('719749'),rng.uniform(.1,.65))
                    if front:c=blend(c,color('284b37'),.3)
                    mesh.leaf(p,tip,L*.095,c)
        # Small terminal spray breaks the culm tip without a palm-like crown.
        top=center(.97)
        for j in range(5):
            a1=a+j*2.4;tip=top+Vector((math.cos(a1)*.35,-.08,math.sin(a1)*.35))*scale
            mesh.leaf(top,tip,.032*scale,color('5c8243'))
    ob=mesh.finish(name,near if front else forest,[stalkmat,leafmat]);ob['depth_role']='foreground_bamboo' if front else 'bamboo_grove'
    ob['root_positions_godot']=json.dumps(used)
    return ob

placements=[(-17,-2.35,.92),(-14.5,-3.3,1),(-12.4,-4.1,1.03),(-10.2,-3.65,.90),(-7.4,-3.5,.87),(-4.6,-3.15,.94),(-1.4,-2.3,.79),(17,-2.3,.85),(19.3,-3.5,.92),(22.1,-3.1,.97),(24.3,-1.7,.83)]
for i,(x,z,s) in enumerate(placements):bamboo('Depth_Bamboo_Main_%02d'%i,x,z,s,810+i,count=7)
for i,x in enumerate(range(-42,49,3)):
    z=-35+math.sin(i*.9)*2.0;y=height(x,z,[bank_bvh])
    if y is not None:bamboo('Depth_Bamboo_Back_%02d'%i,x,z,1.02+math.sin(i*1.7)*.16,920+i,count=5,base=y-.10)
for i,x in enumerate(range(-40,49,6)):
    z=-39+math.sin(i*1.2);y=height(x,z,[bank_bvh])
    if y is not None:bamboo('Depth_Bamboo_Back_Upper_%02d'%i,x,z,1.3+math.sin(i*1.3)*.12,1920+i,count=3,base=y-.10)

# Foreground wall outcrops rise from below the sea, not floating screen cards.
# A few wide shoulders make a frame; the central traversal remains unobscured.
def h(x):
    if x>10:return 1.15+math.sin(x*.37)*.18
    return 1.65+(4.5-x)*.127+math.sin(x*.39)*.16+.1*math.cos(x*.21)

def crag(name,x,z,width,depth,top,seed):
    # Rework the established matched rock topology/UVs into a coastal buttress.
    # This keeps its natural shoulder and existing material instead of a radial cap.
    source=scene.objects['Fish_Ground_Rock_04_Body' if seed%2==0 else 'Fish_Ground_Rock_03_Body']
    me=source.data.copy();ob=bpy.data.objects.new(name,me);near.objects.link(ob)
    points=[source.matrix_world@v.co for v in source.data.vertices]
    lows=[min(p[a] for p in points) for a in range(3)];highs=[max(p[a] for p in points) for a in range(3)]
    for v,p in zip(me.vertices,points):
        u=(p.x-lows[0])/(highs[0]-lows[0]);w=(p.y-lows[1])/(highs[1]-lows[1]);t=(p.z-lows[2])/(highs[2]-lows[2])
        v.co=G((x+(u-.5)*width*2.0,-5+(t**.72)*(top+5),z-(w-.5)*depth*2.0))
    me.update();ob['depth_role']='foreground_cliff';ob['source']='Reworked existing Fish_Rock_C topology and UVs inside Blender MCP'
    return ob

def mountain_spur(name,x,z,width,top,lean):
    m=Mesh();N=13;rings=[]
    sections=[(-3.4,1.4,0),(top*.14,1.08,.04),(top*.40,.87,.19),(top*.65,.70,.35),(top*.84,.62,.60),(top,.28,1)]
    for j,(y,scale,shift) in enumerate(sections):
        ring=[]
        for i in range(N):
            a=i*math.tau/N
            radius=width*scale*(1+.10*math.cos(i*2.1+x))
            point=(x+math.cos(a)*radius+lean*shift,y+(.22*math.sin(i*1.9+x) if j>1 else 0),z+math.sin(a)*radius*.70)
            ring.append(len(m.v));m.v.append(point)
            base=blend(color('7d9792'),color('adc0b1'),.25+.28*max(0,math.cos(a)))
            moss=.24 if j in [2,4,5] and i%4<2 else .04
            m.c.append(blend(base,color('5b8372'),moss))
        rings.append(ring)
    for j in range(len(rings)-1):
        for i in range(N):m.f.append((rings[j][i],rings[j][(i+1)%N],rings[j+1][(i+1)%N],rings[j+1][i]));m.m.append(0)
    m.f.append(tuple(rings[-1]));m.m.append(0)
    ob=m.finish(name,far,[mountmat],smooth=True)
    ob['depth_role']='mountain_rock_shoulder'

for i,(x,z,w,h0,lean) in enumerate([(-41,-71,4.3,12.3,1.8),(-18,-72,3.1,11.8,-1.1),(-5,-78,3.7,10.2,.5),(26,-70,4.1,12.6,-1.7),(39,-76,5.2,15.0,2.0),(61,-76,3.7,11.6,-.8)]):
    mountain_spur('Depth_Mountain_Shoulder_%02d'%i,x,z,w,h0,lean)

fronts=[(-22,6.1,3.1,1.6,.75),(-15.9,6.4,2.4,1.4,.35),(-9.4,6.8,2.0,1.6,.55),(-2.8,6.1,2.5,1.4,.25),(4.1,6.7,1.9,1.2,-.6),(14.7,6.6,2.1,1.4,-.45),(21.8,6.2,2.4,1.6,.35),(28,6.3,2.8,1.6,.7)]
for i,(x,z,w,d,dy) in enumerate(fronts):crag('Depth_Foreground_Crag_%02d'%i,x,z,w,d,h(x)+dy,130+i)
# Sparse edge stems and leaves create faster parallax than the rocky lower edge.
front_bvhs=[bvh(ob) for ob in near.objects if ob.name.startswith('Depth_Foreground_Crag')]
for i,(x,z,s) in enumerate([(-20.5,6.1,.68),(-2.6,6.1,.65),(22.5,6.2,.68)]):
    bamboo('Depth_Bamboo_Fore_%02d'%i,x,z,s,150+i,count=2,front=True,support=front_bvhs)

report={'depth_ranges_godot_z':{'foreground':[5,8],'main_groves':[-4.5,-1.5],'forest_shore':[-43,-29],'middle_ridge':[-101,-65],'far_ridge':[-164,-120]},
    'new_collections':{c.name:len(c.objects) for c in [far,forest,near]},'retired_palms':len(archive.objects),'authoring':'Blender via blender-mcp'}
(OUT/'authoring.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
p=ROOT/'assets/island_blender/asset_manifest.json';d=json.loads(p.read_text());d['revision']='HD2D coastal depth: bamboo groves, two distant mountain ridges, foreground cliffs; close gameplay camera'
d['source_manifests'].append('depth_layers/SOURCES.md');p.write_text(json.dumps(d,indent=2),encoding='utf-8')
print('DEPTH_LAYERS_COMPLETE',json.dumps(report))
