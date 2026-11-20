"""Authored living vegetation. Run ONLY in Blender through blender-mcp.
Uses only the current independently authored Pixel_Cavern_Coast scene.
"""
import bpy, math, random, json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
exec((ROOT/'tools/blender/pixel_cavern_lib.py').read_text(encoding='utf-8'),globals())
scene=bpy.data.scenes[SCENE];bpy.context.window.scene=scene
assert scene['revision']=='pixel-cavern-review-7'
P=palette();live=collection('14_Living_Vegetation')
archive=bpy.data.collections.new('PCC_Archive_Static_Vegetation')
scene.collection.children.link(archive);archive.hide_render=True
r=random.Random(20261120)

def retire(ob):
    for c in list(ob.users_collection):c.objects.unlink(ob)
    archive.objects.link(ob);ob['pixel_cavern']=False;ob.hide_render=True;ob.hide_set(True)

def clamp(t):return max(0.,min(1.,t))
def gd(q):return Vector((q.x,q.z,-q.y))
def bounds(ob):
    pts=[ob.matrix_world@v.co for v in ob.data.vertices]
    return Vector(tuple(min(q[a] for q in pts) for a in range(3))),Vector(tuple(max(q[a] for q in pts) for a in range(3)))

def attributes(ob,weights,pivots,locals_,phases,normals=None):
    ob['wind_data_layout']='uv_xz_uv2_y_weight_color_leaf_phase'
    me=ob.data
    uv=me.uv_layers.get('Wind') or me.uv_layers.new(name='Wind')
    rootuv=me.uv_layers[0]
    colors=me.color_attributes.get('WindPivot') or me.color_attributes.new(name='WindPivot',type='FLOAT_COLOR',domain='POINT')
    me.color_attributes.active_color=colors
    for i,v in enumerate(me.vertices):
        colors.data[i].color=(locals_[i],phases[i],0,1)
    for loop in me.loops:
        i=loop.vertex_index;p=gd(pivots[i])
        rootuv.data[loop.index].uv=(p.x,1-p.z)
        uv.data[loop.index].uv=(p.y,1-weights[i])
    if normals:
        for p in me.polygons:p.use_smooth=True
        me.normals_split_custom_set([normals[l.vertex_index] for l in me.loops])

class Builder:
    def __init__(self):self.v=[];self.f=[];self.mat=[];self.w=[];self.p=[];self.local=[];self.phase=[];self.n=[]
    def vertex(self,q,weight,pivot,local,phase,normal):
        self.v.append(tuple(q));self.w.append(weight);self.p.append(pivot.copy());self.local.append(local);self.phase.append(phase);self.n.append(tuple(normal))
    def leaf(self,root,direction,length,width,weight,phase,normal,material=0,grass=False):
        d=Vector(direction).normalized();side=d.cross(Vector((0,0,1)))
        if side.length<.1:side=Vector((1,0,0))
        side.normalize();fold=side.cross(d).normalized();k=len(self.v)
        # Five cross-sections: narrow attached root, broad shoulders, pointed tip.
        for t,spread in [(0,.10),(.24,.78),(.50,1),(.77,.62),(1,0)]:
            bend=Vector((d.x,d.y,-.28))*length*t*t if not grass else Vector((d.x*.22,d.y*.22,0))*length*t*t
            center=root+d*length*t+bend
            for sign in [-1,1]:
                q=center+side*width*spread*sign+fold*(.045*length*math.sin(t*math.pi))
                w=t*t if grass else weight
                n=(normal*.92+fold*.08).normalized()
                self.vertex(q,w,root,t,phase,n)
        for j in range(4):
            a=k+j*2;self.f.extend([(a,a+1,a+3),(a,a+3,a+2)]);self.mat.extend([material,material])
    def build(self,name,mats):
        if not self.v:return None
        ob=mesh(name,self.v,self.f,live,mats,self.mat)
        attributes(ob,self.w,self.p,self.local,self.phase,self.n)
        ob['living_vegetation']=True
        return ob

def combined(objects):
    verts=[];faces=[]
    for ob in objects:
        start=len(verts);verts.extend(ob.matrix_world@v.co for v in ob.data.vertices)
        faces.extend(tuple(start+i for i in p.vertices) for p in ob.data.polygons)
    return BVHTree.FromPolygons(verts,faces) if verts else None

original=list(scene.objects)
floors=combined([o for o in original if o.name.startswith('Grass_')])
roads=combined([o for o in original if o.name.startswith(('Path_','Step_'))])
rocks=combined([o for o in original if o.name.startswith(('Rock_Cliff_','Rock_Cave_','Wood_Tree_','Bamboo_Stem_')) and 'Buried' not in o.name])
for ob in original:
    if ob.name.startswith(('Plant_Grass_Patch_','Plant_Forest_Cover_')):retire(ob)

# Unequal grass tufts cover the ground itself, leaving stone and travelled edges.
tiles={};grass_blades=0
for ix in range(155):
    x=-17.4+ix*.232
    for iy in range(65):
        y=-3.6+iy*.232
        xx=x+r.uniform(-.095,.095);yy=y+r.uniform(-.095,.095)
        p,n,_,_=floors.ray_cast(Vector((xx,yy,18)),Vector((0,0,-1)),22)
        if p is None or n.z<.7:continue
        road,_,_,_=roads.ray_cast(Vector((xx,yy,18)),Vector((0,0,-1)),22)
        if road is not None and road.z>=p.z-.08:continue
        block,_,_,_=rocks.ray_cast(Vector((xx,yy,18)),Vector((0,0,-1)),22)
        if block is not None and block.z>p.z+.12:continue
        # Large connected patches with smaller clearings, rather than uniform fuzz.
        patch=.5+.27*math.sin(xx*.68+yy*.22)+.19*math.cos(yy*.87-xx*.29)
        if r.random()>(.94 if patch>.35 else .56):continue
        key=(int((xx+18)/3),int((yy+4)/3));b=tiles.setdefault(key,Builder())
        h=r.uniform(.18,.34)*(1.22 if patch>.65 else .86)
        count=4 if yy<4 else 3
        for j in range(count):
            a=r.random()*math.tau;root=p+Vector((r.uniform(-.035,.035),r.uniform(-.035,.035),-.018))
            d=Vector((math.cos(a)*.23,math.sin(a)*.23,1))
            normal=Vector((math.cos(a)*.12,math.sin(a)*.12,1)).normalized()
            b.leaf(root,d,h*r.uniform(.76,1.2),r.uniform(.025,.041),1,r.random(),normal,1 if patch>.7 and j==0 else 0,True)
            grass_blades+=1
for key,b in tiles.items():b.build('LiveGrass_%02d_%02d'%key,[P['grass'],P['grass_light']])

# Vine stems and leaves share hanging distance weights, anchored at the roof.
vine_count=0
for ob in [o for o in original if o.name.startswith('Root_Vine_')]:
    tag=ob.name.rsplit('_',1)[1];pts=[]
    for i in range(len(ob.data.vertices)//5):pts.append(sum((ob.matrix_world@ob.data.vertices[i*5+j].co for j in range(5)),Vector())/5)
    if not pts:continue
    root=pts[0];length=(pts[-1]-root).length
    weights=[clamp((root.z-v.co.z)/max(length,.1))**1.4 for v in ob.data.vertices]
    attributes(ob,weights,[root]*len(weights),[0]*len(weights),[int(tag)*.079%1]*len(weights))
    ob.name='LiveVineStem_'+tag
    old=scene.objects.get('Plant_Vine_Leaves_'+tag)
    if old:retire(old)
    b=Builder()
    for j in range(max(14,int(length/.115))):
        t=(j+.5)/max(14,int(length/.115));q=t*(len(pts)-1);i=min(len(pts)-2,int(q));rootleaf=pts[i].lerp(pts[i+1],q-i)
        sign=1 if j%2 else -1
        d=Vector((sign*r.uniform(.65,.95),r.uniform(-.6,-.15),r.uniform(-.7,-.25)))
        b.leaf(rootleaf,d,r.uniform(.23,.38),r.uniform(.065,.105),t**1.4,(int(tag)*.079+j*.061)%1,Vector((sign*.25,-.65,.7)).normalized(),j%7==0)
        vine_count+=1
    b.build('LiveVineLeaf_'+tag,[P['leaf'],P['leaf_lit']])

# The new tree canopy uses pointed folded leaves in branch-centred layered sprays.
tree_roots={}
for ob in original:
    if ob.name.startswith('Wood_Tree_') and not ob.name.startswith('Wood_Tree_Branch_'):
        i=int(ob.name.rsplit('_',1)[1]);lo,hi=bounds(ob);tree_roots[i]=(Vector(((lo.x+hi.x)*.5,(lo.y+hi.y)*.5,lo.z)),hi.z-lo.z)
tree_leaf_count=0
for ob in [o for o in original if o.name.startswith('Foliage_Tree_')]:
    _,_,ti,ci=ob.name.split('_');ti=int(ti);ci=int(ci);lo,hi=bounds(ob);center=(lo+hi)*.5;radius=(hi-lo)*.5
    retire(ob);shadow=scene.objects.get('Shadow_'+ob.name)
    if shadow:retire(shadow)
    root,height=tree_roots[ti];b=Builder()
    for layer in range(3):
        layercenter=center+Vector((.19*math.sin(ci+layer*1.7),.16*math.cos(ti+layer),(-.40+layer*.46)*radius.z))
        scale=1.0-layer*.15
        for j in range(145 if layer==0 else 115):
            a=r.random()*math.tau;u=r.uniform(-.46,1);rad=math.sqrt(1-u*u)
            q=layercenter+Vector((math.cos(a)*rad*radius.x*scale,math.sin(a)*rad*radius.y*scale,u*radius.z*.45))
            normal=Vector((math.cos(a)*rad,math.sin(a)*rad,u*.75+.25)).normalized()
            # Three-leaf tips form an irregular twig silhouette, not a solid disc.
            for leafid in range(3):
                turn=a+(leafid-1)*.9;d=Vector((math.cos(turn),math.sin(turn),r.uniform(-.3,.4)))
                p=q+Vector((math.cos(turn),math.sin(turn),0))*.07*leafid
                b.leaf(p,d,r.uniform(.24,.39),r.uniform(.055,.09),clamp((p.z-root.z)/max(height,1)),r.random(),normal,1 if u>.65 and j%7==0 else 0)
                tree_leaf_count+=1
    b.build('LiveCanopy_%d_%d'%(ti,ci),[P['leaf'],P['leaf_lit']])
for ob in original:
    if ob.name.startswith('Wood_Tree_'):
        ti=int(ob.name.split('_')[3] if ob.name.startswith('Wood_Tree_Branch_') else ob.name.rsplit('_',1)[1]);root,height=tree_roots[ti]
        weights=[clamp((v.co.z-root.z)/max(height,1)) for v in ob.data.vertices]
        attributes(ob,weights,[root]*len(weights),[0]*len(weights),[ti*.17]*len(weights));ob.name='LiveTreeBranch_'+ob.name.removeprefix('Wood_')

# Keep bamboo stems but replace their wide four-corner blades with tapered leaves.
bamboo_roots={}
for ob in original:
    if ob.name.startswith('Bamboo_Stem_'):
        i=int(ob.name.rsplit('_',1)[1]);lo,hi=bounds(ob);bamboo_roots[i]=(Vector(((lo.x+hi.x)*.5,(lo.y+hi.y)*.5,lo.z)),hi.z-lo.z)
bamboo_leaf_count=0
for ob in original:
    if ob.name.startswith(('Bamboo_Leaves_','Bamboo_Spray_')):
        ti=int(ob.name.split('_')[2]);root,height=bamboo_roots[ti];b=Builder();lo,hi=bounds(ob);center=(lo+hi)*.5
        for p in ob.data.polygons:
            if len(p.vertices)!=4:continue
            q=[ob.data.vertices[i].co.copy() for i in p.vertices]
            # First and third vertex remain attachment and pointed leaf tip.
            d=q[2]-q[0];normal=Vector(((q[0].x-center.x)*.20,(q[0].y-center.y)*.20,.8+(q[0].z-center.z)*.35)).normalized()
            ln=min(.88,d.length*.92)
            b.leaf(q[0],d,ln,ln*.075,clamp((q[0].z-root.z)/height),r.random(),normal,p.material_index%2)
            bamboo_leaf_count+=1
        retire(ob);b.build('LiveBambooLeaf_'+ob.name.removeprefix('Bamboo_'),[P['leaf'],P['leaf_lit']])
    elif ob.name.startswith(('Bamboo_Stem_','Bamboo_Branches_')):
        ti=int(ob.name.rsplit('_',1)[1]);root,height=bamboo_roots[ti];weights=[clamp((v.co.z-root.z)/height) for v in ob.data.vertices]
        attributes(ob,weights,[root]*len(weights),[0]*len(weights),[ti*.113%1]*len(weights))
    elif ob.name.startswith(('Plant_Fern_','Plant_Edge_Shrub_','Plant_Foreground_','Plant_Cliff_Creeper_')):
        lo,hi=bounds(ob);root=Vector(((lo.x+hi.x)*.5,(lo.y+hi.y)*.5,lo.z));height=max(.3,hi.z-lo.z)
        weights=[clamp((v.co.z-lo.z)/height) for v in ob.data.vertices]
        attributes(ob,weights,[root]*len(weights),weights,[r.random()]*len(weights))

scene['revision']='pixel-cavern-living-vegetation-8'
counts={'grass_blades':grass_blades,'grass_tiles':len(tiles),'vine_leaves':vine_count,'tree_leaves':tree_leaf_count,'bamboo_leaves':bamboo_leaf_count,'geometry_source':'Blender MCP, current sample only','revision':scene['revision']}
(ROOT/'artifacts/pixel-vegetation-review/authoring.json').write_text(json.dumps(counts,indent=2),encoding='utf-8')
bpy.data.libraries.write(str(OUT/'pixel_cavern_coast.blend'),{scene},fake_user=True,compress=True)
print(json.dumps(counts))
