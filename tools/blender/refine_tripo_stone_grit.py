"""Revise the smooth stone material through Blender MCP; preserve mesh/UV.
Uses the existing reference-dependent mesh. No new Tripo RGB transfer.
"""
import bpy,math,json,numpy as np,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/tripo-replica-review';A=R/'assets/layered_island/tripo_replica'
SN='Tripo_Stone_Grit_Review_20261119';assert not bpy.data.scenes.get(SN),'Inspect existing grit pass.'
base=bpy.data.scenes['Tripo_Textured_Delivery_20261119'];author=bpy.data.scenes['Tripo_Authored_Material_Sample_20261119']
s=bpy.data.scenes.new(SN);bpy.context.window.scene=s;meshmap={}
for ob in base.objects:
    cp=ob.copy();cp.data=ob.data.copy();s.collection.objects.link(cp)
    if cp.type=='CAMERA':s.camera=cp
    if ob.name in ['Delivery_Rocks','Delivery_Stairs']:
        cp.name='Grit_Rocks' if ob.name=='Delivery_Rocks' else 'Grit_Stairs';meshmap[cp.name]=cp
        src=author.objects['Textured_Measured_Rocks' if cp.name=='Grit_Rocks' else 'Textured_Authored_Stairs']
        ids=np.empty(len(cp.data.polygons),np.int32);cp.data.polygons.foreach_get('material_index',ids)
        cp.data.materials.clear()
        for m in src.data.materials:cp.data.materials.append(m.copy())
        cp.data.polygons.foreach_set('material_index',ids)
        cp['expected_material_faces']=np.bincount(ids,minlength=4).tolist()
s.world=base.world.copy();s.render.engine='CYCLES';s.cycles.samples=96;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=960;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.view_settings.view_transform='AgX';s.view_settings.look=base.view_settings.look
mat=meshmap['Grit_Rocks'].data.materials[0];mat.name='Authored_Grit_Stone_v2';mat.node_tree.nodes.clear();n=mat.node_tree.nodes;l=mat.node_tree.links
def node(t,label=''):
    q=n.new(t)
    if label:q.label=label;q.name=label
    return q
def setv(inp,v):
    if hasattr(v,'is_output'):l.new(v,inp)
    else:inp.default_value=v
def mathn(op,a,b=0,label=''):
    q=node('ShaderNodeMath',label);q.operation=op;setv(q.inputs[0],a);setv(q.inputs[1],b);return q.outputs[0]
def mix(f,a,b,op='MIX',label=''):
    q=node('ShaderNodeMixRGB',label);q.blend_type=op;setv(q.inputs[0],f);setv(q.inputs[1],a);setv(q.inputs[2],b);return q.outputs[0]
def ramp(v,stops,label=''):
    q=node('ShaderNodeValToRGB',label);r=q.color_ramp;r.elements.remove(r.elements[1]);r.elements[0].position=stops[0][0];r.elements[0].color=stops[0][1]
    for p,c in stops[1:]:r.elements.new(p).color=c
    l.new(v,q.inputs[0]);return q.outputs[0]
def grey(v,stops,label=''):return ramp(v,[(p,(x,x,x,1)) for p,x in stops],label)
def noise(scale,detail=2,rough=.65,label=''):
    q=node('ShaderNodeTexNoise',label);q.inputs['Scale'].default_value=scale;q.inputs['Detail'].default_value=detail;q.inputs['Roughness'].default_value=rough;l.new(pos,q.inputs['Vector']);return q.outputs['Fac']
def attr(name):
    q=node('ShaderNodeAttribute',name);q.attribute_name=name;return q.outputs['Fac']
out=node('ShaderNodeOutputMaterial');bs=node('ShaderNodeBsdfPrincipled');l.new(bs.outputs[0],out.inputs['Surface']);bs.inputs['Specular IOR Level'].default_value=.25
geo=node('ShaderNodeNewGeometry');pos=geo.outputs['Position'];sep=node('ShaderNodeSeparateXYZ');l.new(geo.outputs['Normal'],sep.inputs[0])
coarse=noise(12,1.2,.55,'Broad stone color');meso=noise(82,2.7,.65,'Visible shallow fracture relief');grain=noise(245,2,.67,'Mineral aggregate');fine=noise(680,1.5,.6,'Fine mineral glints')
patch=grey(noise(23,1.7,.65,'Weathered patch density'),[(.25,.18),(.48,.55),(.72,1)],'Uneven rough patch coverage')
relief=grey(meso,[(.25,.10),(.43,.29),(.56,.72),(.74,.92)],'Irregular shallow cleavage')
# Only a small lightening of upward-facing stone, keeping its mineral color.
basecolor=ramp(coarse,[(.22,(.10,.083,.062,1)),(.50,(.17,.143,.108,1)),(.79,(.247,.214,.164,1))],'Warm grey stone palette')
top=grey(sep.outputs['Z'],[(.15,0),(.86,.065)],'Restrained top plane lift');basecolor=mix(top,basecolor,(.29,.254,.197,1))
aggregate=grey(grain,[(.27,.48),(.44,.74),(.58,1.06),(.75,1.34)],'Visible mineral tonal variation')
colorstrength=mathn('ADD',mathn('MULTIPLY',patch,.35),.35)
basecolor=mix(colorstrength,basecolor,aggregate,'MULTIPLY','Regional mineral pigment')
basecolor=mix(.20,basecolor,grey(relief,[(.1,.68),(.8,1.12)]),'MULTIPLY','Shallow surface pigment')
curv=attr('Authored_Structural_Curvature');wear=grey(curv,[(.70,0),(.98,.48)])
wear=mathn('MULTIPLY',wear,grey(noise(76,1.5),[(.40,0),(.64,.8)]))
basecolor=mix(wear,basecolor,(.30,.269,.207,1),'MIX','Discontinuous exposed edges')
recess=grey(curv,[(.1,.25),(.46,0)]);basecolor=mix(recess,basecolor,(.065,.05,.032,1))
moss=attr('Authored_Moss_Region');mc=ramp(noise(140,2),[(.24,(.023,.029,.009,1)),(.75,(.075,.091,.023,1))]);basecolor=mix(moss,basecolor,mc)
l.new(basecolor,bs.inputs['Base Color'])
rough=grey(grain,[(.25,.66),(.74,.94)],'Mineral roughness variation');l.new(rough,bs.inputs['Roughness'])
# The original pass had a very weak, subpixel bump. These bands remain readable
# at the actual review scale and modulate light, not just diffuse color.
b1=node('ShaderNodeBump','Meso shallow broken surface');b1.inputs['Distance'].default_value=.0030;b1.inputs['Strength'].default_value=.55;l.new(relief,b1.inputs['Height'])
b2=node('ShaderNodeBump','Uneven mineral aggregate normal');b2.inputs['Distance'].default_value=.00115;l.new(mathn('ADD',mathn('MULTIPLY',patch,.42),.28),b2.inputs['Strength']);l.new(grain,b2.inputs['Height']);l.new(b1.outputs[0],b2.inputs['Normal'])
b3=node('ShaderNodeBump','Fine grain normal');b3.inputs['Distance'].default_value=.00022;b3.inputs['Strength'].default_value=.25;l.new(fine,b3.inputs['Height']);l.new(b2.outputs[0],b3.inputs['Normal']);l.new(b3.outputs[0],bs.inputs['Normal'])
for i,q in enumerate(n):q.location=((i%8)*210,-(i//8)*200)
mat['provenance']='Authored multi-scale mineral material on existing measured geometry; no original RGB transferred.'
meshmap['Grit_Stairs'].data.materials[0]=mat
for ob in meshmap.values():ob.data.update()
s['revision']='grit-material-lookdev-1'
cam=s.camera;target=Vector((0,0,.21));a=math.radians(35);cam.location=target+Vector((math.sin(a)*2.4,-math.cos(a)*2.4,1.05));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(O/'roughness-draft-three-quarter.png');bpy.ops.render.render(write_still=True)
bpy.data.libraries.write(str(A/'tripo_grit_material_authoring.blend'),{s},fake_user=True,compress=True)
report={'scene':s.name,'revision':s['revision'],'geometry_and_uv':'copied unchanged from prior textured delivery','source':'new authored material with three bump scales, regional grain pigment and variable roughness','render':s.render.filepath,'pending':'visual inspection and baked readback'}
(O/'roughness-lookdev.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
