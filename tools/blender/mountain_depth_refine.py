"""Mountain composition authored inside the running Blender via blender-mcp.

Continuous folded slopes replace the detached shore and round pillar skyline.
All coordinates below are in the project's Godot space, converted at the mesh boundary.
"""
import bpy, bmesh, math, json
from pathlib import Path
from mathutils import Vector
from mathutils import noise

ROOT = Path('D:/自己做着玩的/孤屿霜尘')
OUT = ROOT / 'artifacts/mountain-depth-review'
scene = bpy.data.scenes['Island_Refined']
bpy.context.window.scene = scene
assert Path(bpy.data.filepath).resolve() == (ROOT/'assets/island_blender/nameless_island.blend').resolve()

def g(p): return (p[0], -p[2], p[1])
def linear(v): return v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4
def color(h): return tuple(linear(int(h[i:i+2],16)/255) for i in (0,2,4))
def mix(a,b,t): return tuple(x*(1-t)+y*t for x,y in zip(a,b))
def clamp(v): return max(0,min(1,v))

# Retire only the superseded backdrop; preserve the close groves and walking terrain.
archive = bpy.data.collections.get('90_Superseded_Backdrop') or bpy.data.collections.new('90_Superseded_Backdrop')
if archive.name not in scene.collection.children: scene.collection.children.link(archive)
retired = []
for ob in list(scene.objects):
    if any(c.name.startswith('90_') for c in ob.users_collection): continue
    if ob.name.startswith(('Depth_Bamboo_Back','Depth_Mountain_Shoulder')) or ob.name in ['Depth_Forest_Shore','Depth_Far_Ridge','Depth_Middle_Ridge']:
        for c in list(ob.users_collection): c.objects.unlink(ob)
        archive.objects.link(ob); ob.hide_set(True); retired.append(ob.name)

col = bpy.data.collections.get('20_Layered_Mountain_Massifs') or bpy.data.collections.new('20_Layered_Mountain_Massifs')
if col.name not in scene.collection.children: scene.collection.children.link(col)
for ob in list(col.objects): bpy.data.objects.remove(ob,do_unlink=True)
mat = bpy.data.materials['Depth_Mountain']

def profile_at(controls,x):
    for a,b in zip(controls,controls[1:]):
        if x<=b[0]:
            t=clamp((x-a[0])/(b[0]-a[0]))
            # Mostly angular, with a restrained easing on broad shoulders.
            t=.82*t+.18*t*t*(3-2*t)
            return a[1]*(1-t)+b[1]*t
    return controls[-1][1]

far=[(-220,2),(-184,10),(-173,16),(-162,14),(-156,18),(-146,13),(-139,14.2),(-122,7),(-103,12),(-91,16),(-84,13.2),(-78,17.5),(-66,11),(-49,7.5),(-40,12.4),(-31,15.4),(-25,13.8),(-19,17.2),(-7,11.2),(4,8.5),(17,14),(25,12.8),(34,18.2),(40,16.8),(49,11.3),(59,13.5),(72,8.4),(86,14.7),(96,17.6),(105,12),(121,9),(137,14),(146,12),(165,17),(185,8),(220,2)]
mid=[(-145,0),(-120,5),(-109,10),(-103,8.4),(-96,12.1),(-87,8),(-76,4.2),(-64,7),(-57,11.7),(-52,10.2),(-44,12.6),(-37,6.1),(-28,4.4),(-21,7.4),(-16,6.5),(-10,11.4),(-6,10.6),(0,5.5),(9,3.8),(19,7.8),(24,6.8),(30,12),(36,9.5),(45,4.8),(54,7.4),(60,10.9),(65,9.1),(74,5),(84,8.8),(90,7.7),(101,11),(114,4),(145,0)]
front=[(-105,-2),(-80,1),(-68,5.0),(-62,3.7),(-53,7.2),(-47,5.6),(-42,7.8),(-35,4.1),(-27,2.0),(-20,4.4),(-15,3.8),(-9,6.1),(-5,4.4),(3,1.1),(11,2.8),(17,6.0),(23,4.9),(30,7.0),(36,4.1),(43,2.3),(50,4.0),(57,6.9),(63,4.7),(69,5.9),(78,2.3),(90,1),(110,-2)]
layers=[(front,-47,39,48,4.1),(mid,-92,54,56,2.7),(far,-158,64,55,1.4)]
peaks_by_layer=[[p for k,p in enumerate(c[1:-1],1) if p[1]>c[k-1][1] and p[1]>c[k+1][1]] for c,_,_,_,_ in layers]
palettes=[[color(h) for h in colors] for colors in [['3d554d','7c886b','344f39'],['4d6866','8b9785','405c48'],['73898b','a2afa5','6b847a']]]

def elevation(x,z):
    results=[]
    for layer,(controls,depth,fw,bw,seed) in enumerate(layers):
        bend=2*math.sin(x*.12+seed)+1.2*math.sin(x*.31-seed)
        t=abs(z-depth-bend)/(fw if z>depth+bend else bw)
        if t>=1:
            results.append((-9,0,0));continue
        warp=5.8*t*math.sin(x*.086+seed)+2.5*t*t*math.sin(x*.19)
        crest=profile_at(controls,x-warp)
        taper=clamp(min(x-controls[0][0],controls[-1][0]-x)/16)
        spur=0
        for px,py in peaks_by_layer[layer]:
            center=px+warp+math.sin(px*.23+seed)*t*9.5
            if abs(x-center)>14:continue
            for branch,start in [(0,0),(-1,.24),(1,.43)]:
                split=max(0,t-start);cx=center+branch*split*14
                ridge=max(0,1-abs(x-cx)/(1.1+2*t))**1.35
                onset=1 if branch==0 else clamp(split*12)
                spur=max(spur,ridge*onset*(1 if branch==0 else .65))
        y=-9+(crest+9)*((1-t)**1.22)*taper
        y+=(spur*2.5-.5)*math.sin(t*math.pi)*taper
        results.append((y,spur,t))
    index=max(range(3),key=lambda n:results[n][0])
    y,spur,t=results[index]
    # A single continuous apron joins all ranges, so no open layer ends can show.
    apron=1.0+1.6*math.sin(x*.075+z*.04)+.7*math.sin(x*.18-z*.06)
    coast=clamp((-z-6+math.sin(x*.11)*1.1)/20.0);back=clamp((z+217)/35);edge=clamp((220-abs(x))/25)
    apron=-9+(apron+9)*coast*back*edge
    y=max(y,apron)
    n=noise.noise(Vector((x*.22,z*.23,4.6)),noise_basis='PERLIN_ORIGINAL')
    n2=noise.noise(Vector((x*.56+12,z*.55,7.6)),noise_basis='PERLIN_ORIGINAL')
    n3=noise.noise(Vector((x*1.18,z*.94,11.6)),noise_basis='PERLIN_ORIGINAL')
    relief=n*1.05+n2*.40+n3*.13
    y+=relief*clamp((y+6)/6)
    # Blend the mineral and vegetation colors through actual distance.
    blend_layer=clamp((-z-52)/65)+clamp((-z-117)/65)
    lo=min(1,int(blend_layer));a=blend_layer-lo
    palette=[mix(palettes[lo][k],palettes[lo+1][k],a) for k in range(3)]
    exposed=clamp(.30+.40*spur+.23*(1-t)+relief*.12)
    c=mix(palette[0],palette[1],exposed)
    c=mix(c,palette[2],clamp(.62-spur+n*.4)*.45)
    return y,c

v=[];f=[];vc=[]
nx=677;nz=329
for j in range(nz):
    z=-218+j*214/(nz-1)
    for i in range(nx):
        x=-220+i*440/(nx-1);y,c=elevation(x,z)
        v.append(g((x,y,z)));vc.append(c+(1,))
for j in range(nz-1):
    for i in range(nx-1):
        a=j*nx+i;b=a+1;c=a+nx;d=c+1
        if (i+j)%2:f.extend([(a,c,b),(b,c,d)])
        else:f.extend([(a,d,b),(a,c,d)])
# A closed submerged skirt prevents the backdrop from ending in a visible sheet.
boundary=list(range(nx))+[j*nx+nx-1 for j in range(1,nz)]+[(nz-1)*nx+i for i in range(nx-2,-1,-1)]+[j*nx for j in range(nz-2,0,-1)]
bottom=[]
for i in boundary:
    bottom.append(len(v));p=v[i];v.append((p[0],p[1],-16));vc.append(vc[i])
for k,i in enumerate(boundary):
    q=(k+1)%len(boundary);f.append((i,boundary[q],bottom[q],bottom[k]))
f.append(tuple(reversed(bottom)))
me=bpy.data.meshes.new('Connected_Mountain_Ranges');me.from_pydata(v,[],f);me.materials.append(mat);me.update()
attr=me.color_attributes.new(name='DepthColor',type='FLOAT_COLOR',domain='POINT')
attr.data.foreach_set('color',[a for c in vc for a in c])
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
for p in me.polygons:p.use_smooth=len(p.vertices)==3
ob=bpy.data.objects.new('Depth_Mountain_Ranges',me);col.objects.link(ob)
ob['depth_role']='Three connected ranges with continuous valley floors and submerged footing'

report={'authoring':'Blender 5.1 via blender-mcp','removed_from_export':[o.name for o in archive.objects],
        'mountain_objects':[o.name for o in col.objects],
        'depth_spines_godot_z':[-47,-92,-158],
        'preserved_main_groves':[o.name for o in scene.objects if o.name.startswith('Depth_Bamboo_Main')],
        'geometry':'Connected shoulders, asymmetric silhouettes, branching rock ribs, broad ledges; no noise textures'}
(OUT/'authoring.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
p=ROOT/'assets/island_blender/asset_manifest.json';d=json.loads(p.read_text())
d['revision']='Three connected mountain ranges; removed distant shore grove; main bamboo behind character'
d['source_manifests'].append('depth_layers/SOURCES.md');p.write_text(json.dumps(d,indent=2),encoding='utf-8')
print('MOUNTAIN_DEPTH_COMPLETE',json.dumps(report))
