"""Second pass on this turn's NEW sample only, through Blender MCP."""
import bpy,bmesh,math,random,json
from mathutils import Vector
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Fresh_Pixel_Cape'];bpy.context.window.scene=scene
assert scene['revision']=='fresh-cape-color-study-1'
rng=random.Random(30022)
rockcol=bpy.data.collections['Fresh_02_Rock_Faces']
shore=bpy.data.collections['Fresh_06_Shore']
green=bpy.data.collections['Fresh_04_Grass']
steps=bpy.data.collections['Fresh_03_Stairway']
rockm=[bpy.data.materials['Fresh_'+s] for s in ['Rock_Base','Rock_Pale','Rock_Cool','Rock_Dark']]
grassm=[bpy.data.materials['Fresh_'+s] for s in ['Grass_Main','Grass_Light','Grass_Shade']]

def active(ob):
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
def newmesh(name,vs,fs,col,mats):
    data=bpy.data.meshes.new(name+'_mesh');data.from_pydata(vs,[],fs);data.update()
    ob=bpy.data.objects.new(name,data);col.objects.link(ob)
    for mat in mats:data.materials.append(mat)
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    uv=data.uv_layers.new(name='UVMap')
    for li,loop in enumerate(data.loops):
        v=data.vertices[loop.vertex_index].co;uv.data[li].uv=(v.x*.25,v.y*.25+v.z*.15)
    ob['fresh_sample']=True;ob['authored_from']='fresh sample revision, no imported geometry'
    return ob
def fractured_slab(name,foot,low,high,lean,phase):
    n=len(foot);cx=sum(x for x,y in foot)/n;cy=sum(y for x,y in foot)/n
    vs=[]
    for ring in range(3):
        t=ring/2
        for i,(x,y) in enumerate(foot):
            f=[1,.99,.85][ring]+.06*math.sin(i*2.13+phase+ring)
            z=low+(high-low)*t+.15*math.sin(i*1.7+phase)*(0.5+t)
            vs.append((cx+(x-cx)*f+lean[0]*t,cy+(y-cy)*f+lean[1]*t,z))
    vs.append((cx+lean[0]-.13,cy+lean[1]+.12,high+.06))
    fs=[tuple(reversed(range(n)))]
    for ring in range(2):
        for i in range(n):fs.append((ring*n+i,ring*n+(i+1)%n,(ring+1)*n+(i+1)%n,(ring+1)*n+i))
    for i in range(n):fs.append((n*2+i,n*2+(i+1)%n,n*3))
    ob=newmesh(name,vs,fs,rockcol,rockm)
    # Sculpt modifiers introduce medium-scale broken planes, not fine sand.
    active(ob)
    subdiv=ob.modifiers.new('Editable fracture density','SUBSURF');subdiv.subdivision_type='SIMPLE';subdiv.levels=2
    texture=bpy.data.textures.new(name+'_broad_displace',type='CLOUDS');texture.noise_scale=.62;texture.noise_depth=1
    disp=ob.modifiers.new('Broad stone break','DISPLACE');disp.texture=texture;disp.strength=.095;disp.mid_level=.5
    dec=ob.modifiers.new('Remove subpixel facets','DECIMATE');dec.ratio=.30
    for p in ob.data.polygons:p.material_index=1 if p.normal.z>.65 else 0
    return ob

# Rework only newly authored slabs. The long vertical fronts are replaced by
# overlapping diagonal fractures of different depths, not equal-height pillars.
for ob in list(rockcol.objects):
    if ob.name in ['Upper_Terrace_Exposed_Slab','Back_Bamboo_Buried_Rock']:continue
    bpy.data.objects.remove(ob,do_unlink=True)
fractured_slab('Fresh_West_Sunk_Bed',[(-11.2,-3.2),(-9.3,-4.0),(-7.6,-3.6),(-7.0,-2.6),(-8.8,-1.95),(-10.8,-2.3)],-.8,1.9,(.30,.1),.1)
fractured_slab('Fresh_West_Oblique_Crown',[(-10.9,-2.6),(-9.1,-3.52),(-7.05,-3.26),(-6.50,-2.10),(-8,-1.8),(-10.7,-1.9)],1.05,3.15,(-.20,-.15),1.8)
fractured_slab('Fresh_Lower_Slanted_Plate',[(-8.7,-3.2),(-6.55,-4.2),(-4.6,-3.9),(-4.25,-2.75),(-5.9,-2.2),(-8.1,-2.5)],-.9,1.24,(.52,-.15),2.6)
fractured_slab('Fresh_Central_Overlapping_Plate',[(-7.4,-2.9),(-5.6,-3.8),(-3.7,-3.5),(-3.1,-2.2),(-4.8,-1.95),(-6.9,-2.1)],.8,2.95,(.10,.03),3.1)
fractured_slab('Fresh_Cleft_Lower_Large',[(-4.6,-2.8),(-3.1,-3.9),(-1.2,-3.25),(-.9,-1.8),(-2.6,-1.6),(-4.2,-1.8)],-.9,2.05,(.25,-.28),.5)
fractured_slab('Fresh_Entry_Shoulder',[(-3.4,-2.4),(-2.5,-3.05),(-1.05,-2.72),(-.50,-1.75),(-1.7,-1.12),(-3.5,-1.6)],1.65,3.04,(-.20,0),2.5)
fractured_slab('Fresh_Cape_Outer_Lean',[(3.5,-.5),(4.9,-.75),(5.75,.45),(5.2,2.3),(4.3,2.9),(3.5,1.4)],-.75,2.20,(-.2,.15),1.5)
fractured_slab('Fresh_Cape_Crown',[(2.9,-.45),(4.55,-.95),(5.1,.2),(4.9,1.7),(3.6,2.2),(2.8,1.2)],1.5,3.22,(-.05,-.18),.7)
fractured_slab('Fresh_Outer_Tide_Slab',[(4.8,-.6),(6.35,-.55),(6.75,.4),(5.75,1.5),(4.75,.85)],-.7,.85,(.15,-.04),2.0)

# Recess the underlying continuous face behind the authored slabs.
core=bpy.data.objects['Cape_Continuous_Core']
for v in core.data.vertices:
    if v.co.y<-1.6 and v.co.z<2.85:v.co.y+=.25

# Form a continuous rock shoulder alongside the stairs, hiding the triangular
# construction backing while keeping every tread and the landing visible.
fractured_slab('Fresh_Stair_Upper_Embedded_Side',[(-.65,-2.85),(.7,-3.2),(1.6,-2.95),(1.6,-2.3),(.5,-2.2),(-.65,-2.3)],-.4,1.75,(-.1,.05),.1)
fractured_slab('Fresh_Landing_Side_Stone',[(1.4,-3.0),(2.8,-3.45),(3.5,-3.13),(3.45,-2.5),(2.5,-2.4),(1.45,-2.5)],-.5,1.35,(.15,.05),3.1)
fractured_slab('Fresh_Lower_Stair_Side',[(3.1,-3.5),(4.2,-4.0),(5.2,-4.1),(5.3,-3.5),(4.6,-3.05),(3.5,-3.0)],-.5,.70,(.05,0),2.4)
for ob in steps.objects:
    if '_Buried_Support' in ob.name:
        # Pull supporting side face inward to expose stone lips, keeping solid core.
        coords=[v.co for v in ob.data.vertices]
        cx=sum(v.x for v in coords)/len(coords);cy=sum(v.y for v in coords)/len(coords)
        for v in ob.data.vertices:
            v.co.y=cy+(v.co.y-cy)*.86
    if '_Tread_' in ob.name:
        # Independent worn crowns with shallow off-axis dips, no repetitive bevel rings.
        ztop=max(v.co.z for v in ob.data.vertices)
        for i,v in enumerate(ob.data.vertices):
            if v.co.z>ztop-.03:v.co.z+=.014*math.sin(i*1.9+ztop*2.1)

# Grass no longer reads as a planted rail along the full front edge.
for ob in list(green.objects):
    if ob.name.startswith('Grass_Clump_'):
        idx=int(ob.name.rsplit('_',1)[1])
        if idx<84 and (idx%14 in [3,4,5,6,7] or idx>65):
            bpy.data.objects.remove(ob,do_unlink=True)
        elif idx<84:
            ob.location.y+=rng.uniform(-.12,.3)
            ob.scale*=1.3
        else:
            ob.scale*=.85

# Short broken turf tongues cover a few rock/soil transitions.
for i,(x,y,w) in enumerate([(-9.4,-3.35,.8),(-7.5,-3.26,.7),(-5.6,-3.1,.9),(-3.1,-2.85,.55),(3.6,-.92,.5)]):
    vs=[(x-w,y+.3,3.15),(x+w,y+.3,3.15),(x+w*.7,y-.08,3.08),(x+w*.25,y-.22,2.94),(x-w*.35,y-.13,3.0),(x-w,y,3.10)]
    newmesh('Fresh_Turf_Tongue_%02d'%i,vs,[(0,1,2),(0,2,4),(2,3,4),(0,4,5)],green,[grassm[0]])

# Broader leaf groups plus irregular upper termination; avoid bare antenna tips.
for ob in bpy.data.collections['Fresh_05_Bamboo'].objects:
    if 'Fan' in ob.name:
        vs=ob.data.vertices
        centroid=sum((v.co for v in vs),Vector())/len(vs)
        for v in vs:
            v.co=centroid+(v.co-centroid)*1.25
        if 'Counter' in ob.name:
            ob.location.z+=.15
    elif '_Stem' in ob.name:
        zmax=max(v.co.z for v in ob.data.vertices)
        for v in ob.data.vertices:
            if v.co.z>zmax-.1:v.co.z-=.40

# Full-screen projection surface authored here, used only for Godot edge shading.
quad=newmesh('Fresh_Render_Overlay',[(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)],[(0,1,2,3)],shore,[rockm[0]])
scene['revision']='fresh-cape-color-study-2'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/fresh_pixel_cape/fresh_pixel_cape.blend'))
print(json.dumps({'revision':scene['revision'],'fresh_objects':sum(bool(o.get('fresh_sample')) for o in scene.objects)}))
