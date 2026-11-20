"""Author new stone/wood/moss colors from observation, not reference pixels.
Run via Blender MCP. The existing reference-fitted mesh is explicitly retained.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/tripo-replica-review';A=R/'assets/layered_island/tripo_replica'
s=bpy.data.scenes['Tripo_Authored_Material_Sample_20261119'];bpy.context.window.scene=s
assert s['revision']=='authored-material-prepared-1'
class Graph:
    def __init__(self,name):
        self.mat=bpy.data.materials.new(name);self.mat.use_nodes=True;self.n=self.mat.node_tree.nodes;self.l=self.mat.node_tree.links;self.n.clear()
        self.out=self.node('ShaderNodeOutputMaterial');self.bs=self.node('ShaderNodeBsdfPrincipled');self.link(self.bs.outputs[0],self.out.inputs['Surface'])
        self.geo=self.node('ShaderNodeNewGeometry');self.pos=self.geo.outputs['Position']
        self.bs.inputs['Roughness'].default_value=.88;self.bs.inputs['Specular IOR Level'].default_value=.22
    def node(self,t):return self.n.new(t)
    def link(self,a,b):self.l.new(a,b)
    def set(self,s,v):
        if hasattr(v,'is_output'):self.link(v,s)
        else:s.default_value=v
    def math(self,op,a,b=0):
        n=self.node('ShaderNodeMath');n.operation=op;self.set(n.inputs[0],a);self.set(n.inputs[1],b);return n.outputs[0]
    def noise(self,scale,detail=2,vector=None):
        n=self.node('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale;n.inputs['Detail'].default_value=detail;n.inputs['Roughness'].default_value=.58;self.link(vector or self.pos,n.inputs['Vector']);return n.outputs['Fac']
    def ramp(self,s,stops):
        n=self.node('ShaderNodeValToRGB');r=n.color_ramp
        r.elements.remove(r.elements[1]);r.elements[0].position=stops[0][0];r.elements[0].color=stops[0][1]
        for p,c in stops[1:]:r.elements.new(p).color=c
        self.link(s,n.inputs[0]);return n.outputs['Color']
    def mix(self,f,a,b,blend='MIX'):
        n=self.node('ShaderNodeMixRGB');n.blend_type=blend;self.set(n.inputs[0],f);self.set(n.inputs[1],a);self.set(n.inputs[2],b);return n.outputs[0]
    def color(self,c):self.set(self.bs.inputs['Base Color'],c)
    def layout(self):
        for i,n in enumerate(self.n):n.location=((i%6)*210,-(i//6)*200)
        self.mat['provenance']='New Blender material authored by observing palette and surface roles; no original texture sampled or projected.'
        return self.mat
g=Graph('Authored_Warm_Fractured_Stone')
broad=g.noise(9,1.4);pigment=g.noise(105,2)
base=g.ramp(broad,[(.18,(.125,.114,.093,1)),(.5,(.195,.175,.143,1)),(.82,(.25,.226,.188,1))])
# Keep broad planes readable. Fine pigment only modulates a narrow value range.
pig=g.ramp(pigment,[(.15,(.86,.86,.86,1)),(.82,(1,1,1,1))]);base=g.mix(.45,base,pig,'MULTIPLY')
sep=g.node('ShaderNodeSeparateXYZ');g.link(g.geo.outputs['Normal'],sep.inputs[0])
top=g.ramp(sep.outputs['Z'],[(.05,(0,0,0,1)),(.75,(.22,.22,.22,1))]);base=g.mix(top,base,(.29,.262,.218,1))
# Break convex edge pigment into intermittent stretches, without geometry bevels.
edge=g.ramp(g.geo.outputs['Pointiness'],[(.502,(0,0,0,1)),(.535,(1,1,1,1))])
breaks=g.ramp(g.noise(48,2),[(.39,(0,0,0,1)),(.61,(.65,.65,.65,1))]);wear=g.math('MULTIPLY',edge,breaks)
base=g.mix(wear,base,(.38,.345,.28,1))
cavity=g.ramp(g.geo.outputs['Pointiness'],[(.452,(.45,.45,.45,1)),(.495,(0,0,0,1))]);base=g.mix(cavity,base,(.07,.062,.048,1))
# Local moss is confined to the low flank, not scattered over every surface.
attr=g.node('ShaderNodeAttribute');attr.attribute_name='Authored_Moss_Region'
mb=g.ramp(g.noise(82,2),[(.42,(0,0,0,1)),(.62,(1,1,1,1))]);moss=g.math('MULTIPLY',attr.outputs['Fac'],mb)
mc=g.ramp(g.noise(46,2),[(.2,(.045,.057,.014,1)),(.8,(.14,.157,.045,1))]);base=g.mix(moss,base,mc)
g.color(base)
bump=g.node('ShaderNodeBump');bump.inputs['Strength'].default_value=.10;bump.inputs['Distance'].default_value=.0005;g.link(pigment,bump.inputs['Height']);g.link(bump.outputs[0],g.bs.inputs['Normal'])
stone=g.layout()
w=Graph('Authored_Weathered_Wood')
v=w.node('ShaderNodeVectorMath');v.operation='MULTIPLY';w.link(w.pos,v.inputs[0]);v.inputs[1].default_value=(12,1,4)
woodgrain=w.noise(80,1.5,v.outputs['Vector']);w.color(w.ramp(woodgrain,[(.2,(.075,.042,.018,1)),(.50,(.17,.103,.046,1)),(.8,(.27,.184,.089,1))]));wood=w.layout()
f=Graph('Authored_Static_Amber_Flame');z=f.node('ShaderNodeSeparateXYZ');f.link(f.pos,z.inputs[0]);fc=f.ramp(z.outputs['Z'],[(.365,(.65,.12,.008,1)),(.405,(1,.60,.08,1)),(.47,(1,.85,.35,1))]);f.color(fc);f.link(fc,f.bs.inputs['Emission Color']);f.bs.inputs['Emission Strength'].default_value=.35;flame=f.layout()
char=Graph('Authored_Hearth_Char');char.color(char.ramp(char.noise(85),[(.2,(.035,.023,.01,1)),(.8,(.15,.078,.02,1))]));hearth=char.layout()
materials=[stone,wood,flame,hearth]
counts={}
for name in ['Textured_Measured_Rocks','Textured_Authored_Stairs']:
    ob=s.objects[name];me=ob.data;me.materials.clear()
    for m in materials:me.materials.append(m)
    a=me.attributes.new('Authored_Moss_Region','FLOAT','POINT')
    weights=[]
    for vtx in me.vertices:
        x,y,zv=vtx.co
        p1=((x-.285)/.15)**2+((y+.365)/.11)**2+((zv-.09)/.12)**2
        p2=((x+.43)/.07)**2+((y-.07)/.10)**2+((zv-.17)/.18)**2
        weights.append(max(0,min(1,1-min(p1,p2)))*.9)
    a.data.foreach_set('value',weights)
    c=[0]*4
    for p in me.polygons:
        x,y,zv=p.center;mi=0
        if name=='Textured_Measured_Rocks':
            r=(x*x+y*y)**.5
            if r<.027 and zv>.37:mi=2
            elif r<.052 and zv>.352:mi=3
            elif -.185<x<-.115 and -.086<y<.052 and zv>.345:mi=1
            elif .102<x<.19 and -.068<y<.093 and zv>.345:mi=1
        p.material_index=mi;c[mi]+=1
    counts[name]=c
s['revision']='authored-material-lookdev-2'
cam=s.camera;target=Vector((0,0,.21));a=math.radians(35);cam.location=target+Vector((math.sin(a)*2.4,-math.cos(a)*2.4,1.05));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(O/'authored-material-draft-35.png');bpy.ops.render.render(write_still=True)
bpy.data.libraries.write(str(A/'tripo_material_authoring.blend'),{s},fake_user=True,compress=True)
(O/'material-lookdev.json').write_text(json.dumps({'scene':s.name,'material_faces':counts,'materials':[m.name for m in materials],'original_texture_reused':False,'geometry':'Previous reference-fitted reconstruction retained.'},indent=2),encoding='utf8')
print('Material lookdev saved and rendered.',counts)
