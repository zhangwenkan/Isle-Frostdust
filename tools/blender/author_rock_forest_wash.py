"""Blender MCP: quieter colored stone washes and broken structural pigment.
Geometry, UVs and material face regions remain the measured Tripo reconstruction.
"""
import bpy,math,json,numpy as np,hashlib
from pathlib import Path
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/rock-forest-style-review';A=R/'assets/layered_island/tripo_replica'
SN='Rock_Forest_Wash_Author_20261119';assert not bpy.data.scenes.get(SN),'Inspect existing pass before restarting.'
base=bpy.data.scenes['Tripo_Stone_Grit_Review_20261119'];s=bpy.data.scenes.new(SN);bpy.context.window.scene=s
meshes=[];fingerprints={}
def fingerprint(me):
    vals={}
    for label,seq,prop,dtype,size in [('position',me.vertices,'co','float32',3),('loops',me.loops,'vertex_index','int32',1),('uv',me.uv_layers.active.data,'uv','float32',2)]:
        ar=np.empty(len(seq)*size,dtype=dtype);seq.foreach_get(prop,ar);vals[label]=hashlib.sha256(ar.tobytes()).hexdigest()
    return vals
for ob in base.objects:
    cp=ob.copy();cp.data=ob.data.copy();s.collection.objects.link(cp)
    if cp.type=='CAMERA':s.camera=cp
    if ob.name in ['Grit_Rocks','Grit_Stairs']:
        cp.name='Wash_Author_Rocks' if 'Rocks' in ob.name else 'Wash_Author_Stairs';meshes.append(cp)
        ids=np.empty(len(cp.data.polygons),np.int32);cp.data.polygons.foreach_get('material_index',ids)
        mats=list(cp.data.materials);cp.data.materials.clear()
        for m in mats:cp.data.materials.append(m.copy())
        cp.data.polygons.foreach_set('material_index',ids)
        fingerprints[cp.name]={'before':fingerprint(ob.data),'after':fingerprint(cp.data),'faces':np.bincount(ids,minlength=4).tolist()}
s.world=base.world.copy();s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=960;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look=base.view_settings.look
mat=meshes[0].data.materials[0];mat.name='Authored_Colored_Stone_Wash';mat.node_tree.nodes.clear();n=mat.node_tree.nodes;l=mat.node_tree.links
def node(t,label=''):
    q=n.new(t)
    if label:q.label=label;q.name=label
    return q
def setv(inp,v):
    if hasattr(v,'is_output'):l.new(v,inp)
    else:inp.default_value=v
def mathn(op,a,b=0):
    q=node('ShaderNodeMath');q.operation=op;setv(q.inputs[0],a);setv(q.inputs[1],b);return q.outputs[0]
def mix(f,a,b,op='MIX',label=''):
    q=node('ShaderNodeMixRGB',label);q.blend_type=op;setv(q.inputs[0],f);setv(q.inputs[1],a);setv(q.inputs[2],b);return q.outputs[0]
def ramp(v,stops,label=''):
    q=node('ShaderNodeValToRGB',label);r=q.color_ramp;r.interpolation='EASE';r.elements.remove(r.elements[1]);r.elements[0].position=stops[0][0];r.elements[0].color=stops[0][1]
    for p,c in stops[1:]:r.elements.new(p).color=c
    l.new(v,q.inputs[0]);return q.outputs[0]
def grey(v,stops,label=''):return ramp(v,[(p,(x,x,x,1)) for p,x in stops],label)
def noise(scale,detail=1,label='',vector=None):
    q=node('ShaderNodeTexNoise',label);q.inputs['Scale'].default_value=scale;q.inputs['Detail'].default_value=detail;q.inputs['Roughness'].default_value=.52;l.new(pos if vector is None else vector,q.inputs['Vector']);return q.outputs['Fac']
def attr(name):
    q=node('ShaderNodeAttribute',name);q.attribute_name=name;return q.outputs['Fac']
out=node('ShaderNodeOutputMaterial');bs=node('ShaderNodeBsdfPrincipled');l.new(bs.outputs[0],out.inputs['Surface']);bs.inputs['Specular IOR Level'].default_value=.16
geo=node('ShaderNodeNewGeometry');pos=geo.outputs['Position'];sep=node('ShaderNodeSeparateXYZ');l.new(geo.outputs['Normal'],sep.inputs[0])
wash=noise(8.5,.7,'Broad pooled pigment')
color=ramp(wash,[(.23,(.105,.125,.120,1)),(.43,(.175,.190,.162,1)),(.57,(.218,.222,.185,1)),(.78,(.285,.268,.215,1))],'Cool recess to warm mineral wash')
top=grey(sep.outputs['Z'],[(.20,0),(.85,.10)],'Restrained warm top wash');color=mix(top,color,(.32,.293,.229,1))
layer=grey(noise(24,1.1,'Uneven pigment pools'),[(.28,.86),(.51,1),(.74,1.09)])
color=mix(.42,color,layer,'MULTIPLY','Quiet middle scale wash')
mapping=node('ShaderNodeVectorMath','Short directional dry brush');mapping.operation='MULTIPLY';l.new(pos,mapping.inputs[0]);mapping.inputs[1].default_value=(1.3,.8,4.2)
strokes=noise(29,1.2,'Interrupted brush coverage',mapping.outputs[0])
broken=grey(strokes,[(.35,0),(.47,.1),(.62,.85)],'Uneven brush pressure')
curve=attr('Authored_Structural_Curvature')
cavity=mathn('MULTIPLY',grey(curve,[(.12,.48),(.36,0)]),broken)
color=mix(cavity,color,(.050,.068,.065,1),'MIX','Selective dark fracture strokes')
wear=mathn('MULTIPLY',grey(curve,[(.74,0),(.98,.30)]),broken)
color=mix(wear,color,(.36,.337,.275,1),'MIX','Broken light on exposed fractures')
patch=grey(noise(17,.8,'Local peeled zones'),[(.47,0),(.62,.12),(.76,1)])
fleck=noise(170,1,'Sparse stone tooth')
color=mix(mathn('MULTIPLY',patch,.17),color,grey(fleck,[(.3,.78),(.7,1.12)]),'MULTIPLY','Local dry stone grain')
moss=attr('Authored_Moss_Region');moss_color=ramp(noise(26,1),[(.26,(.040,.063,.027,1)),(.73,(.091,.119,.047,1))],'Olive moss wash');color=mix(moss,color,moss_color)
l.new(color,bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.94
relief=noise(43,1.3,'Broad shallow cleavage')
b1=node('ShaderNodeBump','Shallow broken planes');b1.inputs['Distance'].default_value=.0014;b1.inputs['Strength'].default_value=.34;l.new(relief,b1.inputs['Height'])
b2=node('ShaderNodeBump','Localized dry tooth');b2.inputs['Distance'].default_value=.00045;l.new(mathn('MULTIPLY',patch,.22),b2.inputs['Strength']);l.new(fleck,b2.inputs['Height']);l.new(b1.outputs[0],b2.inputs['Normal']);l.new(b2.outputs[0],bs.inputs['Normal'])
meshes[1].data.materials[0]=mat
for i,q in enumerate(n):q.location=((i%8)*210,-(i//8)*200)
s['revision']='colored-stone-wash-author-1'
bpy.data.libraries.write(str(A/'rock_forest_wash_authoring.blend'),{s},fake_user=True,compress=True)
(O/'material-author.json').write_text(json.dumps({'scene':SN,'revision':s['revision'],'mesh_uv_fingerprints':fingerprints,'description':'Broad colored washes, broken curvature-guided pigment, local dry tooth; no geometry changes.'},indent=2),encoding='utf8')
print('Colored stone wash author saved; geometry and UV hashes retained.')
