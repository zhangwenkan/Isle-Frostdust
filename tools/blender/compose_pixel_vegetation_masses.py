"""Compose connected grass / bamboo masses. Execute inside Blender via MCP only."""
import bpy, math, random, json, bmesh
from pathlib import Path
from mathutils import Vector
from array import array
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
exec((ROOT/'tools/blender/pixel_cavern_lib.py').read_text(encoding='utf-8'),globals())
scene=bpy.data.scenes[SCENE];bpy.context.window.scene=scene
assert scene['revision']=='pixel-cavern-living-vegetation-8'
live=collection('15_Composed_Vegetation');P=palette();r=random.Random(7312)
archive=collection('Archive_Before_Harmony');archive.hide_render=True
counts={'grass_blades':0,'bamboo_leaves':0,'bamboo_clusters':0,'shadow_masses':0}

def retire(o):
    for c in list(o.users_collection):c.objects.unlink(o)
    archive.objects.link(o);o['pixel_cavern']=False;o.hide_render=True;o.hide_set(True)

def attrs(ob,pivots,weights,local,phase,normals):
    me=ob.data;uv=me.uv_layers[0];uv2=me.uv_layers.new(name='Wind')
    a=[];b=[]
    for l in me.loops:
        i=l.vertex_index;p=pivots[i]
        a.extend((p.x,1+p.y));b.extend((p.z,1-weights[i]))
    uv.data.foreach_set('uv',a);uv2.data.foreach_set('uv',b)
    col=me.color_attributes.new(name='WindPivot',type='FLOAT_COLOR',domain='POINT')
    col.data.foreach_set('color',[c for i in range(len(local)) for c in (local[i],phase[i],0,1)])
    me.color_attributes.active_color=col
    for p in me.polygons:p.use_smooth=True
    me.normals_split_custom_set_from_vertices(normals)
    ob['wind_data_layout']='uv_xz_uv2_y_weight_color_leaf_phase'

class Leaves:
    def __init__(self):self.v=[];self.f=[];self.p=[];self.w=[];self.l=[];self.ph=[];self.n=[]
    def leaf(self,p,d,length,width,weight,phase,normal):
        d=Vector(d).normalized();view=Vector((.12,-1,.58));side=d.cross(view).normalized();k=len(self.v)
        for t,spread in ((0,.07),(.22,.75),(.48,1),(.76,.60),(1,0)):
            center=p+d*length*t+Vector((0,0,-.13*length*t*t))
            for sign in (-1,1):
                self.v.append(tuple(center+side*width*spread*sign));self.p.append(p.copy());self.w.append(weight);self.l.append(t);self.ph.append(phase);self.n.append(tuple(normal))
        for j in range(4):
            a=k+j*2;self.f.extend(((a,a+1,a+3),(a,a+3,a+2)))
    def build(self,name):
        ob=mesh(name,self.v,self.f,live,[P['leaf']]);attrs(ob,self.p,self.w,self.l,self.ph,self.n);return ob

def shadow(name,center,scale,weight,phase):
    bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=2,radius=1)
    for v in bm.verts:
        q=v.co.copy();v.co=center+Vector((q.x*scale.x,q.y*scale.y,q.z*scale.z))
    me=bpy.data.meshes.new(name+'_mesh');bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);live.objects.link(ob);finish(ob,live,[P['leaf']])
    attrs(ob,[center]*len(me.vertices),[weight]*len(me.vertices),[0]*len(me.vertices),[phase]*len(me.vertices),[tuple(v.normal) for v in me.vertices]);counts['shadow_masses']+=1
    return ob

original=[o for o in scene.objects if o.get('pixel_cavern') and o.type=='MESH']
# Height envelopes form low quiet interiors and taller, coherent tuft shoulders.
# Positions stay fixed on the authored terrain; no generated ground geometry.
for ob in original:
    if not ob.name.startswith('LiveGrass_'):continue
    me=ob.data;newnorm=[]
    for k in range(0,len(me.vertices),10):
        root=(me.vertices[k].co+me.vertices[k+1].co)*.5
        field=.5+.27*math.sin(root.x*.76+root.y*.31)+.20*math.cos(root.y*1.04-root.x*.23)
        t=max(0,min(1,(field-.36)/.38));t=t*t*(3-2*t)
        scale=.24+.73*t
        for j in range(5):
            a=me.vertices[k+2*j];b=me.vertices[k+2*j+1];center=(a.co+b.co)*.5
            for v in (a,b):
                side=v.co-center;delta=center-root
                v.co=root+Vector((delta.x*.58,delta.y*.58,delta.z*scale))+side*(1.28 if t>.3 else 1.05)
        newnorm.extend([(0,0,1)]*10);counts['grass_blades']+=1
    for p in me.polygons:p.material_index=0;p.use_smooth=True
    me.update();me.normals_split_custom_set_from_vertices(newnorm)
    ob['harmony_grass_envelope']=True

# Recompose each existing branch fan into short leaves on a coherent twig.
# Keep attachment and stem placement; old leaves are archived, never reexported.
for ob in original:
    if not ob.name.startswith('LiveBambooLeaf_'):continue
    me=ob.data;nv=len(me.vertices)//10;groups=[]
    if '_Spray_' in ob.name:groups=[(0,nv)]
    else:
        start=0
        while start<nv:
            size=14 if start%24==0 else 10;groups.append((start,min(nv-start,size)));start+=size
    weights=[0]*len(me.vertices)
    for l in me.loops:weights[l.vertex_index]=1-me.uv_layers[1].data[l.index].uv.y
    b=Leaves()
    for gi,(start,n) in enumerate(groups):
        roots=[(me.vertices[(start+j)*10].co+me.vertices[(start+j)*10+1].co)*.5 for j in range(n)]
        origin=roots[0];axis=(roots[-1]-origin);axis.z=0
        if axis.length<.03:axis=Vector((1,0,0))
        length=axis.length*.83;axis.normalize();length=max(.35,min(1.05,length))
        lateral=Vector((-axis.y,axis.x,0));pairs=6 if n>=14 else 4
        weight=weights[start*10];phase=(gi*.193+origin.x*.117)%1
        cluster_center=origin+axis*length*.50+Vector((0,0,-.07))
        for j in range(pairs):
            t=(j+.2)/pairs;attach=origin+axis*length*t+Vector((0,0,-.09*t*t))
            for sign in (-1,1):
                d=axis*(.35+.38*t)+lateral*sign*(.80-.17*t)+Vector((0,0,-.13-.18*t))
                ln=(.44-.15*t)*(.92+.08*math.sin(gi+j*.8))
                normal=Vector((lateral.x*sign*.18,lateral.y*sign*.18,.95-.16*t)).normalized()
                b.leaf(attach,d,ln,ln*.105,weight,phase,normal);counts['bamboo_leaves']+=1
        b.leaf(origin+axis*length,axis+Vector((0,0,-.30)),.33,.032,weight,phase,Vector((0,0,1)))
        counts['bamboo_leaves']+=1;counts['bamboo_clusters']+=1
        # A smaller solid interior casts one mass, leaving openings at the edges.
        # Each proxy follows the same spatial main wind, with no leaf flutter.
        ext=Vector((abs(axis.x)*length*.36+abs(lateral.x)*.20,abs(axis.y)*length*.36+abs(lateral.y)*.20,.13))
        shadow('Shadow_BambooMass_%s_%02d'%(ob.name.removeprefix('LiveBambooLeaf_'),gi),cluster_center,ext,weight,phase)
    name=ob.name;retire(ob);ob.name='Archived_Harmony_'+name;b.build(name)

# Tree leaves retain the actual shape, but use one volume normal per crown layer.
for ob in original:
    if not ob.name.startswith('LiveCanopy_'):continue
    me=ob.data;coords=[v.co for v in me.vertices];lo=Vector(tuple(min(p[i] for p in coords) for i in range(3)));hi=Vector(tuple(max(p[i] for p in coords) for i in range(3)));center=(lo+hi)*.5;rad=(hi-lo)*.5
    normals=[]
    for k in range(0,len(me.vertices),10):
        p=(me.vertices[k].co+me.vertices[k+1].co)*.5;q=p-center
        n=Vector((q.x/max(rad.x,1)*.52,q.y/max(rad.y,1)*.52,.62+q.z/max(rad.z,.2)*.32)).normalized();normals.extend([tuple(n)]*10)
    me.normals_split_custom_set_from_vertices(normals)
    for p in me.polygons:p.material_index=0
    # Two overlapping unequal lobes avoid the old regular round shadow disks.
    weight=1-me.uv_layers[1].data[0].uv.y
    for j in range(2):
        ctr=center+Vector(((-.22 if j==0 else .28)*rad.x,(-.10 if j==0 else .16)*rad.y,(.06 if j==0 else -.09)*rad.z))
        shadow('Shadow_CanopyMass_'+ob.name.removeprefix('LiveCanopy_')+'_'+str(j),ctr,Vector((rad.x*.60,rad.y*.70,rad.z*.55)),weight,0)

scene['revision']='pixel-cavern-vegetation-harmony-9'
bpy.data.libraries.write(str(OUT/'pixel_cavern_coast.blend'),{scene},fake_user=True,compress=True)
(ROOT/'artifacts/pixel-vegetation-harmony-review/authoring.json').write_text(json.dumps(counts,indent=2),encoding='utf-8')
print(json.dumps(counts))
