"""Blender MCP: sparse karst peak groups rising through a cloud sea."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,noise
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/misty-peaks-review'
scene=bpy.data.scenes['Island_Refined']
for wm in bpy.data.window_managers:
    for win in wm.windows:win.scene=scene
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()

archive=bpy.data.collections.get('90_Rejected_Continuous_Mountains') or bpy.data.collections.new('90_Rejected_Continuous_Mountains')
if archive.name not in scene.collection.children:scene.collection.children.link(archive)
old=scene.objects.get('Depth_Mountain_Ranges')
if old and archive not in old.users_collection:
    for c in list(old.users_collection):c.objects.unlink(old)
    archive.objects.link(old);old.hide_set(True)
col=bpy.data.collections.get('21_Misty_Peak_Groups') or bpy.data.collections.new('21_Misty_Peak_Groups')
if col.name not in scene.collection.children:scene.collection.children.link(col)
for ob in list(col.objects):bpy.data.objects.remove(ob,do_unlink=True)

def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def color(h):return tuple(linear(int(h[i:i+2],16)/255) for i in (0,2,4))
def mix(a,b,t):return tuple(x*(1-t)+y*t for x,y in zip(a,b))
def clamp(x):return max(0,min(1,x))
def curve(points,t):
    for a,b in zip(points,points[1:]):
        if t<=b[0]:
            u=clamp((t-a[0])/(b[0]-a[0]));u=u*u*(3-2*u)
            return a[1]*(1-u)+b[1]*u
    return points[-1][1]

def peak(name,x,z,top,width,depth,lean,seed,profile):
    verts=[];faces=[];colors=[];around=72;rows=44;base=-10.0
    palette=[color(h) for h in ['53665f','8e9a84','4c6650']]
    for j in range(rows+1):
        t=j/rows;y=base+(top-base)*t
        r=curve(profile,t)
        cx=x+lean*t*t+math.sin(t*3.0+seed)*1.15*t
        cz=z+math.sin(t*2.0+seed)*1.6*t
        for i in range(around):
            a=i*math.tau/around
            # Broad buttresses continue vertically, ending in unequal crown shoulders.
            flute=.105*math.sin(a*4+seed+.28*t)+.045*math.cos(a*7-seed+.5*t)
            asym=1+.19*math.sin(a+seed)+.085*math.cos(3*a+seed)
            rr=r*asym+flute*math.sin(math.pi*t)**.65
            px=cx+math.cos(a)*width*rr;pz=cz+math.sin(a)*depth*rr
            n=noise.noise(Vector((px*.42,pz*.42,y*.62)),noise_basis='PERLIN_ORIGINAL')
            relief=(.07*n+.13*math.sin(y*.72+a*2.5))*math.sin(math.pi*t)
            px+=math.cos(a)*relief;pz+=math.sin(a)*relief
            py=y+(1.25*math.sin(a+seed)+.48*math.cos(a*3-seed))*math.sin(math.pi*t)
            verts.append((px,-pz,py))
            # Broken upper vegetation, mineral ribs and shaded clefts, kept broad.
            exposed=clamp(.50+.22*math.cos(a-seed)+.30*flute/.10+.08*n)
            c=mix(palette[0],palette[1],exposed)
            shelf=clamp(.25+.35*math.sin(y*.56+math.sin(a*3))+.2*n)
            c=mix(c,palette[2],shelf*.50+clamp((t-.86)*6)*.22)
            colors.append(c+(1,))
    for j in range(rows):
        for i in range(around):
            a=j*around+i;b=j*around+(i+1)%around;c=a+around;d=b+around
            faces.extend([(a,b,d),(a,d,c)])
    faces.append(tuple(reversed(range(around))))
    faces.append(tuple(rows*around+i for i in range(around)))
    me=bpy.data.meshes.new(name+'_Rock');me.from_pydata(verts,[],faces);me.materials.append(bpy.data.materials['Depth_Mountain']);me.update()
    ca=me.color_attributes.new(name='DepthColor',type='FLOAT_COLOR',domain='POINT');ca.data.foreach_set('color',[n for c in colors for n in c])
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    for p in me.polygons:p.use_smooth=len(p.vertices)==3
    ob=bpy.data.objects.new(name,me);col.objects.link(ob)
    ob['depth_role']='Distant peak; submerged base concealed by atmospheric cloud banks'
    ob['top_godot']=top;ob['spine_godot_z']=z
    return ob

round_profile=[(0,1.45),(.27,1.16),(.48,1.0),(.67,.82),(.80,.62),(.91,.35),(.97,.16),(1,.025)]
steep_profile=[(0,1.4),(.28,1.10),(.52,.88),(.72,.69),(.84,.46),(.92,.27),(.98,.10),(1,.018)]
shoulder_profile=[(0,1.5),(.30,1.13),(.55,.95),(.68,.84),(.77,.79),(.86,.43),(.94,.22),(1,.02)]

# Irregular groups and open intervals; no continuous land surface extends to shore.
specs=[
 ('Near_01',-64,-108,10.2,10.6,9.0,-3.5,1.4,shoulder_profile),
 ('Near_02',-30,-104,13.2,7.8,9.0,3.1,2.8,round_profile),
 ('Near_03',32,-119,17.0,9.8,10.5,-4.1,4.2,steep_profile),
 ('Near_04',77,-111,12.8,11.2,9.5,2.4,5.8,shoulder_profile),
 ('Far_01',-118,-180,15.8,14.0,12.0,-4.8,7.2,round_profile),
 ('Far_02',-63,-186,20.5,16.0,13.0,4.8,8.6,steep_profile),
 ('Far_03',-5,-190,9.6,15.0,13.0,-3.1,9.4,shoulder_profile),
 ('Far_04',66,-198,18.6,15.5,14.0,-4.8,10.5,round_profile),
 ('Far_05',122,-191,22.4,15.0,13.0,3.6,11.4,steep_profile),
]
for label,*args in specs:peak('Mist_Peak_'+label,*args)
report={'authoring':'Blender 5.1 via blender-mcp','peak_groups':len(specs),'main_peak_specs':[(s[0],s[1],s[2],s[3]) for s in specs],
        'nearest_geometry_godot_z':max(-v.co.y for o in col.objects for v in o.data.vertices),
        'retired':'Depth_Mountain_Ranges, dense continuous surface reaching foreground sea',
        'design':'Sparse uneven karst groups, open mist intervals, concealed feet; no continuous land apron'}
(OUT/'authoring.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
p=ROOT/'assets/island_blender/asset_manifest.json';d=json.loads(p.read_text())
d['revision']='Sparse distant peak groups with cloud-covered feet; continuous shore-reaching ranges retired'
d['source_manifests'].append('depth_layers/SOURCES.md');p.write_text(json.dumps(d,indent=2),encoding='utf-8')
print('MISTY_PEAKS_COMPLETE',json.dumps(report))
