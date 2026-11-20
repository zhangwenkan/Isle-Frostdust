"""Second reference pass: break masonry rhythm and build bamboo leaf volumes."""
import bpy,bmesh,math,random,json
from mathutils import Vector
from pathlib import Path
root=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Fresh_Pixel_Cape'];bpy.context.window.scene=scene
assert scene['revision']=='fresh-cape-reference-polish-1'
rng=random.Random(40311)
rockcol=bpy.data.collections['Fresh_02_Rock_Faces'];green=bpy.data.collections['Fresh_04_Grass'];bamboo=bpy.data.collections['Fresh_05_Bamboo']

def active(ob):
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
def recolor(name,h):
    m=bpy.data.materials['Fresh_'+name];rgb=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    c=[v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    m.diffuse_color=(*c,1);m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1);m['srgb']='#'+h
for name,h in [('Rock_Base','899b99'),('Rock_Pale','a6b0a2'),('Rock_Cool','7b8e95'),('Rock_Dark','45616c'),
 ('Grass_Main','62864c'),('Grass_Light','7a9654'),('Grass_Shade','4f7553'),
 ('Bamboo_Leaf','42755b'),('Bamboo_Leaf_Light','64875b'),('Bamboo_Leaf_Dark','315e52'),
 ('Step','a6ad9c'),('Step_Variant','98a69b'),('Path','a19a83')]:recolor(name,h)

# Smooth medium scale wear into the clipped volumes, then preserve broad
# planar normals. Edges become irregular arcs, not geometric triangle motifs.
for i,ob in enumerate(rockcol.objects):
    if ob.type!='MESH':continue
    active(ob)
    for v in ob.data.vertices:
        p=v.co
        p.y+=.11*math.sin(p.x*1.3+p.z*2.4+i*.7)
        p.x+=.06*math.sin(p.y*1.7+p.z*2.1+i)
        p.z+=.06*math.sin(p.x*.9+p.y*1.4+i*.8)
    bevel=ob.modifiers.new('Secondary worn edge','BEVEL');bevel.width=.11;bevel.segments=2;bevel.angle_limit=.25
    bevel.affect='EDGES';bpy.ops.object.modifier_apply(modifier=bevel.name)
    # Split selected large planes into a shallow ridge, with coherent normals.
    # Weighted normals keep the wide planes readable instead of faceting all triangles.
    for p in ob.data.polygons:p.use_smooth=True
    wn=ob.modifiers.new('Large stone plane normals','WEIGHTED_NORMAL');wn.keep_sharp=True;wn.weight=25
    if 'Crown' in ob.name or 'Shoulder' in ob.name:
        # Most crown sits just below turf; a few exposed corners remain.
        for v in ob.data.vertices:
            if v.co.z>3.10:v.co.z=3.10+(v.co.z-3.10)*.18

# Stagger primary seams and shorten the exposed horizontal shelf lines.
for name,delta in {
 'Rock_West_Undercut':(.38,.20,.08),
 'Rock_Center_Deep_Plane':(-.25,.13,-.10),
 'Rock_Center_Low_Bed':(.35,.25,-.13),
 'Rock_Entry_Split_Front':(-.12,.12,-.12),
 'Rock_Cape_Lower_Wall':(.12,.04,0),
}.items():
    ob=bpy.data.objects[name]
    for v in ob.data.vertices:v.co+=Vector(delta)

def mesh(name,vs,fs,col,mat):
    me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(vs,[],fs);me.update()
    ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(mat)
    uv=me.uv_layers.new(name='UVMap')
    for li,l in enumerate(me.loops):
        p=me.vertices[l.vertex_index].co;uv.data[li].uv=(p.x*.25,p.y*.25+p.z*.1)
    ob['fresh_sample']=True;ob['authored_from']='new sample leaf/grass cluster refinement'
    return ob

# Replace comb-like fans with layered bunches of lanceolate bamboo leaves.
# Each bunch has a quiet core, articulated tips, and proxy-volume normals.
leafm=[bpy.data.materials['Fresh_'+n] for n in ['Bamboo_Leaf','Bamboo_Leaf_Light','Bamboo_Leaf_Dark']]
for ob in list(bamboo.objects):
    if 'Bamboo_Leaves' in ob.name:bpy.data.objects.remove(ob,do_unlink=True)
for ob in list(bamboo.objects):
    if 'Bough' not in ob.name:continue
    stem=int(ob.name.split('_')[1]);branch=int(ob.name.split('_')[3])
    if (stem+branch)%5==0:continue
    # Rod's last seven vertices are the tip ring (five-sided branches).
    center=sum((v.co for v in list(ob.data.vertices)[-5:]),Vector())/5
    front=center.y<2.5
    pr=random.Random(stem*151+branch*131)
    rx=.68+.16*pr.random();rz=.32+.10*pr.random();ry=.34
    vs=[];fs=[];normals=[]
    for i in range(78):
        a=pr.uniform(0,math.tau);r=math.sqrt(pr.random())
        base=center+Vector((rx*r*math.cos(a),ry*pr.uniform(-1,1),rz*r*math.sin(a)))
        # Down/outward direction with varied attachment avoids a repeated feather.
        direction=Vector((.68*math.cos(a)+pr.uniform(-.4,.4),pr.uniform(-.30,.18),-.50+pr.uniform(-.25,.3))).normalized()
        ll=pr.uniform(.27,.53);width=pr.uniform(.045,.08)
        tangent=Vector((direction.z,0,-direction.x)).normalized()
        tip=base+direction*ll;mid=base.lerp(tip,.42)+Vector((0,-.035,.02))
        k=len(vs);vs.extend([tuple(base),tuple(mid-tangent*width),tuple(tip),tuple(mid+tangent*width)])
        fs.append((k,k+1,k+2,k+3))
    mi=0 if front else 2
    if branch==4 and stem%3==0:mi=1
    leaf=mesh('Bamboo_Leaf_Cluster_%02d_%02d'%(stem,branch),vs,fs,bamboo,leafm[mi])
    for p in leaf.data.polygons:
        for li in p.loop_indices:
            q=leaf.data.vertices[leaf.data.loops[li].vertex_index].co-center
            n=Vector((q.x*.8,q.y*1.8-.20,q.z*2.4+.32)).normalized()
            normals.append(tuple(n))
    leaf.data.normals_split_custom_set(normals)

# Grass is a continuous edge treatment, not sparse isolated dark flecks.
for ob in list(green.objects):
    if 'Grass_Patch_Blades' in ob.name:bpy.data.objects.remove(ob,do_unlink=True)
grassm=[bpy.data.materials['Fresh_'+n] for n in ['Grass_Main','Grass_Light','Grass_Shade']]
groups=[(-9.25,-2.35,1.35,.57,1),(-7.0,-2.45,1.25,.55,0),(-4.8,-2.15,1.3,.50,1),(-2.55,-1.97,.7,.35,0),
 (-9.2,1.6,1.35,.85,2),(-7.0,2.0,1.6,1.0,2),(-4.7,2.15,1.3,.80,2),(-2.4,2.1,1.3,.85,0),
 (.05,2.3,1.45,.75,1),(2.0,1.15,1.10,.75,0),(-8.1,.35,.9,.24,0),(-5.8,.13,.8,.26,1),(-3.6,-.24,.5,.2,0)]
for j,(x,y,rx,ry,mi) in enumerate(groups):
    vs=[];fs=[];pr=random.Random(540+j)
    for i in range(int(170*(rx+ry))):
        a=pr.uniform(0,math.tau);r=math.sqrt(pr.random());base=Vector((x+rx*r*math.cos(a),y+ry*r*math.sin(a),3.145))
        h=pr.uniform(.12,.31);w=pr.uniform(.025,.055)
        # Front-facing grass planes have clean broad silhouettes; all share turf normal.
        s=Vector((1,0,0));lean=Vector((pr.uniform(-.11,.11),pr.uniform(-.06,.06),0))
        k=len(vs);vs.extend([tuple(base-s*w),tuple(base+s*w),tuple(base+lean+s*w*.55+Vector((0,0,h*.48))),tuple(base+lean+Vector((0,0,h))),tuple(base+lean-s*w*.45+Vector((0,0,h*.6)))])
        fs.append(tuple(range(k,k+5)))
    tuft=mesh('Grass_Patch_Blades_%02d'%j,vs,fs,green,grassm[mi])
    tuft.data.normals_split_custom_set([(0,0,1)]*len(tuft.data.loops))

scene['revision']='fresh-cape-reference-polish-2'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/fresh_pixel_cape/fresh_pixel_cape.blend'))
print(json.dumps({'revision':scene['revision'],'fresh_meshes':sum(o.type=='MESH' for o in scene.objects)}))
