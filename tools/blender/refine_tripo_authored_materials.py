"""Refine authored material using multiscale geometry and semantic source labels.
Source albedo is consulted only to distinguish wood/fire/moss; RGB is not copied.
Executed inside Blender via MCP.
"""
import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/tripo-replica-review';A=R/'assets/layered_island/tripo_replica'
s=bpy.data.scenes['Tripo_Authored_Material_Sample_20261119'];bpy.context.window.scene=s
assert s['revision']=='authored-material-lookdev-2'
stone=bpy.data.materials['Authored_Warm_Fractured_Stone'];nt=stone.node_tree;n=nt.nodes;l=nt.links
bs=next(x for x in n if x.type=='BSDF_PRINCIPLED');geo=next(x for x in n if x.type=='NEW_GEOMETRY')
def setv(inp,value):
    if hasattr(value,'is_output'):l.new(value,inp)
    else:inp.default_value=value
def mathn(op,a,b=0):
    q=n.new('ShaderNodeMath');q.operation=op;setv(q.inputs[0],a);setv(q.inputs[1],b);return q.outputs[0]
def ramp(v,stops):
    q=n.new('ShaderNodeValToRGB');r=q.color_ramp;r.elements.remove(r.elements[1]);r.elements[0].position=stops[0][0];r.elements[0].color=stops[0][1]
    for p,c in stops[1:]:r.elements.new(p).color=c
    l.new(v,q.inputs[0]);return q.outputs[0]
def noise(scale,detail=2):
    q=n.new('ShaderNodeTexNoise');q.inputs['Scale'].default_value=scale;q.inputs['Detail'].default_value=detail;l.new(geo.outputs['Position'],q.inputs['Vector']);return q.outputs['Fac']
def mix(f,a,b,op='MIX'):
    q=n.new('ShaderNodeMixRGB');q.blend_type=op;setv(q.inputs[0],f);setv(q.inputs[1],a);setv(q.inputs[2],b);return q.outputs[0]
def attribute(name):
    q=n.new('ShaderNodeAttribute');q.attribute_name=name;return q.outputs['Fac']
reports=[]
for name in ['Textured_Measured_Rocks','Textured_Authored_Stairs']:
    ob=s.objects[name];me=ob.data;nv=len(me.vertices)
    co=np.empty(nv*3,dtype=np.float32);me.vertices.foreach_get('co',co);co=co.reshape(-1,3)
    normals=np.empty(nv*3,dtype=np.float32);me.vertices.foreach_get('normal',normals);normals=normals.reshape(-1,3)
    edges=np.empty(len(me.edges)*2,dtype=np.int32);me.edges.foreach_get('vertices',edges);edges=edges.reshape(-1,2)
    src=np.r_[edges[:,0],edges[:,1]];dst=np.r_[edges[:,1],edges[:,0]]
    degree=np.bincount(src,minlength=nv).clip(1).astype(np.float32)
    sm=co.copy()
    for _ in range(30):
        sums=np.stack([np.bincount(src,weights=sm[dst,k],minlength=nv) for k in range(3)],axis=1)
        sm=sm*.45+sums/degree[:,None]*.55
    curve=np.einsum('ij,ij->i',co-sm,normals)
    # Centered finite scale convexity; negative values darken recessed joints.
    weights=np.clip((curve+.0012)/.0024,0,1)
    att=me.attributes.new('Authored_Structural_Curvature','FLOAT','POINT');att.data.foreach_set('value',weights)
    reports.append({'name':name,'curvature_quantiles':np.quantile(curve,[0,.05,.25,.5,.75,.95,1]).tolist()})
# Read the reference only for bounded discrete region identification.
ref=bpy.data.objects['Material_Reference_Original'];rm=ref.data;rm.calc_loop_triangles()
tree=BVHTree.FromPolygons([v.co for v in rm.vertices],[list(p.vertices) for p in rm.polygons],all_triangles=True)
im=next(nd.image for nd in rm.materials[0].node_tree.nodes if nd.type=='TEX_IMAGE');iw,ih=im.size
pixels=np.empty(iw*ih*4,dtype=np.float32);im.pixels.foreach_get(pixels);pixels=pixels.reshape(ih,iw,4)
uv=rm.uv_layers.active.data
classes=np.zeros(len(rm.polygons),dtype=np.int32)
for p in rm.polygons:
    x,y,z=p.center
    # Finite region bounds prevent shadow colors elsewhere becoming wood/moss.
    if not ((abs(x)<.22 and abs(y)<.12 and z>.32) or (abs(x)>.20 and z<.30)):continue
    u=sum(uv[i].uv.x for i in p.loop_indices)/len(p.loop_indices);v=sum(uv[i].uv.y for i in p.loop_indices)/len(p.loop_indices)
    rr,gg,bb=pixels[min(ih-1,max(0,int(v*ih))),min(iw-1,max(0,int(u*iw))),:3]
    rad=(x*x+y*y)**.5
    if rad<.03 and z>.37:classes[p.index]=2
    elif rad<.05 and z>.35:classes[p.index]=3
    elif .10<abs(x)<.20 and abs(y)<.10 and z>.33 and rr>gg*1.19 and gg>bb*1.24:classes[p.index]=1
    elif abs(x)>.20 and z<.30 and gg>rr*.97 and gg>bb*1.38:classes[p.index]=4
ob=s.objects['Textured_Measured_Rocks'];me=ob.data;counts=[0]*5
moss_sum=np.zeros(len(me.vertices));moss_count=np.zeros(len(me.vertices))
for p in me.polygons:
    pos,normal,index,dist=tree.find_nearest(p.center)
    label=int(classes[index]) if index is not None and dist<.022 else 0
    p.material_index=label if label<4 else 0;counts[label]+=1
    if label==4:
        for vi in p.vertices:moss_sum[vi]+=1
    for vi in p.vertices:moss_count[vi]+=1
me.attributes['Authored_Moss_Region'].data.foreach_set('value',np.clip(moss_sum/np.maximum(1,moss_count)*1.6,0,1))
# Stronger but controlled mineral planes, with broken structural wear.
broad=noise(11,1.6)
base=ramp(broad,[(.18,(.083,.073,.055,1)),(.50,(.16,.138,.106,1)),(.82,(.25,.219,.172,1))])
grain=noise(430,2.4);minerals=ramp(grain,[(.25,(.57,.57,.57,1)),(.54,(.9,.9,.9,1)),(.76,(1.12,1.12,1.12,1))]);base=mix(.62,base,minerals,'MULTIPLY')
sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Normal'],sep.inputs[0]);top=ramp(sep.outputs['Z'],[(.2,(0,0,0,1)),(.85,(.20,.20,.20,1))]);base=mix(top,base,(.30,.266,.215,1))
curve=attribute('Authored_Structural_Curvature');wear=ramp(curve,[(.59,(0,0,0,1)),(.86,(1,1,1,1))]);fragment=ramp(noise(73,2),[(.32,(.1,.1,.1,1)),(.60,(.9,.9,.9,1))]);wear=mathn('MULTIPLY',wear,fragment)
base=mix(wear,base,(.37,.334,.274,1));cavity=ramp(curve,[(.1,(.55,.55,.55,1)),(.45,(0,0,0,1))]);base=mix(cavity,base,(.055,.046,.031,1))
mc=ramp(noise(140,2),[(.24,(.028,.043,.009,1)),(.75,(.16,.19,.04,1))]);base=mix(attribute('Authored_Moss_Region'),base,mc)
l.new(base,bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.91
bp=next(x for x in n if x.type=='BUMP');l.new(grain,bp.inputs['Height']);bp.inputs['Strength'].default_value=.13;bp.inputs['Distance'].default_value=.00065
s['revision']='authored-material-refined-3'
s.render.filepath=str(O/'authored-material-refined-35.png');bpy.ops.render.render(write_still=True)
bpy.data.libraries.write(str(A/'tripo_material_authoring.blend'),{s},fake_user=True,compress=True)
(O/'material-refined.json').write_text(json.dumps({'curvature':reports,'semantic_faces':counts,'source_texture_usage':'Discrete wood/fire/moss region identification only; source RGB/UV not used as output color.'},indent=2),encoding='utf8')
print('Refined material rendered.',counts)
