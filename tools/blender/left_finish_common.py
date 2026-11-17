"""Shared authoring helpers. Execute only within the real Blender MCP session."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'assets/layered_island';TEX=OUT/'left_finish_textures';REVIEW=ROOT/'artifacts/left-finish-review'
SCENE=bpy.data.scenes['Layered_Island_20261116'];bpy.context.window.scene=SCENE
LAYOUT=json.loads((OUT/'layout.json').read_text(encoding='utf-8'))
A={k:Vector((v[0],-v[2],v[1])) for k,v in LAYOUT['anchors'].items()}
COL=bpy.data.collections.get('41_Left_Finish')
MATS={}
def mat(name,color=(1,1,1,1)):
    key='LF_'+name
    if bpy.data.materials.get(key):MATS[name]=bpy.data.materials[key];return MATS[name]
    m=bpy.data.materials.new(key);m.use_nodes=True;m.diffuse_color=color
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color;p.inputs['Roughness'].default_value=.92
    image_path=TEX/(name+'.png')
    if image_path.exists():
        im=bpy.data.images.load(str(image_path),check_existing=True);im.reload();im.pack()
        node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;m.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
    MATS[name]=m;return m
for n in ['rock_a','rock_b','rock_c','rock_d','rock_top','soil','grass','sand','paving','tread','culm','leaf']:mat(n)
mat('node',(0.21,.28,.11,1));mat('branch',(.16,.22,.075,1));mat('grass_blade',(.22,.32,.10,1))
def tri(points):
    pts=[Vector(p) for p in points];result=tessellate_polygon([pts])
    return [tuple(int(v) if isinstance(v,int) else min(range(len(pts)),key=lambda i:(pts[i]-v).length_squared) for v in t) for t in result]
def route_at(x,y):
    best=(1e6,0,None,0)
    for i,(ka,kb) in enumerate(LAYOUT['edges']):
        if ka in ['bridge_left','bridge_right','cave_mouth']:continue
        a=A[ka];b=A[kb];v=Vector((b.x-a.x,b.y-a.y));q=Vector((x-a.x,y-a.y));t=max(0,min(1,q.dot(v)/v.length_squared));dist=(q-v*t).length
        if dist<best[0]:best=(dist,a.z+(b.z-a.z)*t,i,t)
    return best
def sm(a,b,v):
    t=max(0,min(1,(v-a)/(b-a)));return t*t*(3-2*t)
def height(x,y):
    h=2.85+.72*sm(2.85,3.75,y)+1.26*sm(6.35,7.12,y)+1.08*sm(10.35,11.08,y)
    h+=.08*math.sin(x*.40+y*.19)+.06*math.sin(y*.6-x*.17)
    dist,rh,index,t=route_at(x,y)
    if index in [8,10,12]:
        ka,kb=LAYOUT['edges'][index];n={8:4,10:7,12:6}[index]
        rh=A[ka].z+(A[kb].z-A[ka].z)*min(n,math.floor(t*n)+1)/n-.065
    if index in [2,3,7,8,9,10,11,12]:h=h*(sm(.62,1.48,dist))+rh*(1-sm(.62,1.48,dist))
    return h
class Mesh:
    def __init__(self,name):self.name=name;self.v=[];self.f=[];self.mi=[];self.uv=[];self.w=[];self.colors=[];self.materials=[]
    def material(self,m):
        if isinstance(m,str):m=MATS[m]
        if m not in self.materials:self.materials.append(m)
        return self.materials.index(m)
    def part(self,vs,fs,material,uv=None,weights=None,colors=None,indices=None):
        n=len(self.v);self.v.extend([tuple(p) for p in vs]);self.f.extend([tuple(n+i for i in face) for face in fs])
        base=self.material(material)
        self.mi.extend(indices if indices is not None else [base]*len(fs))
        self.uv.extend(uv or [None]*len(vs));self.w.extend(weights or [0]*len(vs));self.colors.extend(colors or [(1,1,1,1)]*len(vs))
    def build(self,smooth=False):
        me=bpy.data.meshes.new(self.name);me.from_pydata(self.v,[],self.f);me.update()
        # Recalculate closed solids without averaging their deliberately cut faces.
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
        ob=bpy.data.objects.new(self.name,me);COL.objects.link(ob)
        for m in self.materials:me.materials.append(m)
        uv=me.uv_layers.new(name='UVMap');wind=me.uv_layers.new(name='Wind')
        color=me.color_attributes.new(name='SurfaceTint',type='FLOAT_COLOR',domain='CORNER')
        for p in me.polygons:
            p.material_index=self.mi[p.index];p.use_smooth=smooth
            for li in p.loop_indices:
                vi=me.loops[li].vertex_index;co=me.vertices[vi].co;n=p.normal
                coord=self.uv[vi]
                if coord is None:
                    if abs(n.z)>.65:coord=(co.x*.37,co.y*.37)
                    elif abs(n.x)>abs(n.y):coord=(co.y*.30,co.z*.34)
                    else:coord=(co.x*.30,co.z*.34)
                uv.data[li].uv=coord;wind.data[li].uv=(self.w[vi],0);color.data[li].color=self.colors[vi]
        return ob
def tube(builder,points,radii,material,sides=8,weights=None):
    pts=[Vector(p) for p in points];vs=[];uv=[];w=[];fs=[]
    for j,p in enumerate(pts):
        d=pts[min(j+1,len(pts)-1)]-pts[max(j-1,0)];d.normalize();side=d.cross(Vector((0,1,0)))
        if side.length<.01:side=d.cross(Vector((1,0,0)))
        side.normalize();up=side.cross(d).normalized()
        for k in range(sides):
            a=k*math.tau/sides;vs.append(p+radii[j]*(side*math.cos(a)+up*math.sin(a)));uv.append((k/sides,j/max(1,len(pts)-1)));w.append(weights[j] if weights else 0)
    for j in range(len(pts)-1):
        for k in range(sides):z=j*sides+k;n=j*sides+(k+1)%sides;fs.append((z,n,n+sides,z+sides))
    fs.extend([tuple(reversed(range(sides))),tuple((len(pts)-1)*sides+i for i in range(sides))])
    builder.part(vs,fs,material,uv,w)
def export(label):
    live=[o for o in SCENE.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
    LAYOUT['revision']='left-finish-'+label;LAYOUT['objects']=[{'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons)} for o in live]
    (OUT/'layout.json').write_text(json.dumps(LAYOUT,ensure_ascii=False,indent=2),encoding='utf-8')
    bpy.data.libraries.write(str(OUT/'layered_island.blend'),{SCENE},fake_user=True,compress=True)
    bpy.ops.object.select_all(action='DESELECT')
    for o in live:o.hide_set(False);o.select_set(True)
    bpy.context.view_layer.objects.active=live[0]
    bpy.ops.export_scene.gltf(filepath=str(OUT/'layered_island.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_texcoords=True,export_normals=True,export_vertex_color='ACTIVE',export_all_vertex_colors=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
    print(json.dumps({'pass':label,'live_meshes':len(live),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in live)}))
