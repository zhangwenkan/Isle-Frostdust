"""Blender MCP: enlarge seaward rock mass, preserve access scale, author solid stairs.
Works in a new scene. Reference-dependent rock reconstruction stays explicit.
"""
import bpy,bmesh,math,json,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/rock-cape-weight-review';A=R/'assets/layered_island/tripo_replica'
SN='Rock_Cape_Weight_Author_20261119';assert not bpy.data.scenes.get(SN),'Inspect existing author pass.'
source=bpy.data.scenes['Rock_Forest_Wash_Author_20261119'];s=bpy.data.scenes.new(SN);bpy.context.window.scene=s
fit=json.loads((A/'game_assembly.json').read_text());P=Matrix(fit['placement_matrix']);PI=P.inverted();objects={}
for ob in source.objects:
    cp=ob.copy();cp.data=ob.data.copy();s.collection.objects.link(cp)
    if cp.type=='CAMERA':s.camera=cp
    if ob.name in ['Wash_Author_Rocks','Wash_Author_Stairs']:
        cp.name='Weight_Author_Rocks' if 'Rocks' in ob.name else 'Weight_Previous_Stairs';objects[cp.name]=cp
        ids=np.empty(len(cp.data.polygons),np.int32);cp.data.polygons.foreach_get('material_index',ids);mats=list(cp.data.materials);cp.data.materials.clear()
        for mat in mats:cp.data.materials.append(mat.copy())
        cp.data.polygons.foreach_set('material_index',ids)
s.world=source.world.copy();s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=960;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look=source.view_settings.look
def smooth(a,b,v):
    t=max(0,min(1,(v-a)/(b-a)));return t*t*(3-2*t)
bot=Vector((-62.5,4));top=Vector((-63.140209,7.841249));axis=(top-bot).normalized();side=Vector((axis.y,-axis.x))
def expand(p):
    q=p.copy();rel=Vector((p.x,p.y))-bot;across=abs(rel.dot(side))
    preserve=(1-smooth(1.1,2.1,across))*(1-smooth(8.2,10.0,p.y))
    flank=1-preserve;offset=max(0,-59.8-p.x)
    q.x-=.30*offset*smooth(0,2.5,offset)*flank
    q.y+=(p.y-9.3)*.19*smooth(1.0,4.5,offset)*flank
    return q
rock=objects['Weight_Author_Rocks'];me=rock.data;before=[P@v.co for v in me.vertices]
prop_labels=np.zeros(len(me.vertices),np.int32)
for f in me.polygons:
    if f.material_index:
        for vi in f.vertices:prop_labels[vi]=f.material_index
# Translate the two wood pieces/fire as rigid local regions; avoid enlarging props.
centres={1:Vector((.145,0,.36)),4:Vector((-.16,-.01,.36)),2:Vector((0,0,.38)),3:Vector((0,0,.355))}
shifts={k:PI@(expand(P@v)) - v for k,v in centres.items()}
for v in me.vertices:
    label=int(prop_labels[v.index]);key=4 if label==1 and v.co.x<0 else label
    if key:v.co+=shifts[key]
    else:v.co=PI@expand(P@v.co)
me.update()
# Broader but still human-scale lower steps. The upper landing stays at its old level.
yb=[-.540,-.511,-.484,-.458,-.433,-.409,-.386,-.363,-.341,-.319,-.298,-.278,-.258,-.239,-.220,-.202,-.184]
zh=[.082,.096,.112,.128,.145,.161,.179,.197,.216,.234,.253,.272,.291,.309,.327,.343]
left=[.100,.097,.092,.087,.085,.083,.082,.080,.080,.081,.079,.081,.080,.081,.080,.083]
right=[.096,.092,.095,.090,.086,.086,.082,.084,.082,.080,.082,.080,.083,.081,.083,.082]
centeroff=[-.002,-.001,.001,.001,-.001,0,.001,-.001,0,.001,0,-.001,.001,0,0,0]
def xc(y):return -.070+(y+.449)*.287
# Make room only inside the new stone tread envelope; keep flank silhouettes.
bm=bmesh.new();bm.from_mesh(me);removed=[]
for f in bm.faces:
    if f.material_index!=0:continue
    p=f.calc_center_median()
    if yb[0]<p.y<yb[-1]:
        j=next((i for i in range(16) if yb[i]<=p.y<yb[i+1]),15)
        if xc(p.y)-left[j]+.003<p.x<xc(p.y)+right[j]-.003 and p.z<zh[j]+.006:removed.append(f)
bmesh.ops.delete(bm,geom=removed,context='FACES');bm.to_mesh(me);bm.free();me.update()
# Each tread is a closed volume with an authored front contour. Hidden overlap
# and a buried continuous core carry its weight; no all-edge bevel operation.
verts=[];faces=[];curves=[];us=[-1,-.74,-.38,0,.37,.72,1]
contours=[[-.001,0,.001,.0002,-.0006,0,.0012],[.001,0,-.0005,-.001,0,.0007,0],[0,-.0003,-.001,0,.001,.0014,.0001],[-.0005,.0004,.001,0,-.0005,0,.001],[.001,0,.0004,-.0006,-.001,0,.0005],[0,.0006,0,-.0008,.0002,.001,0],[.0008,0,-.0005,.0002,.001,0,-.0005],[0,-.0005,.0005,.001,0,-.0007,.0003]]
def add(co,curve=.5):verts.append(co);curves.append(curve);return len(verts)-1
def width(u,j):return (left[j] if u<0 else right[j])*u
step_stats=[]
for j in range(16):
    front=[];rear=[];basefront=[];baserear=[];y0=yb[j];y1=yb[j+1]+.006;z=zh[j]
    bottom=.059 if j<2 else max(.059,zh[j-2]-.006)
    for k,u in enumerate(us):
        loss=.0015 if (j,k) in [(1,0),(4,6),(9,0),(12,6)] else 0
        x=xc(y0)+width(u,j)+centeroff[j];yf=y0+contours[j%8][k]-u*.0015
        zf=z+u*.00055-loss
        front.append(add((x,yf,zf),.79 if (j+k)%5==0 else .53))
        rear.append(add((xc(y1)+width(u,j)+centeroff[j],y1,z+.0007+u*.0003),.5))
        # Slightly tucked upper face, heavy lower face; selected chips stay local.
        basefront.append(add((x+u*.0011,yf+.0017,bottom),.38))
        baserear.append(add((xc(y1)+width(u,j)+centeroff[j],y1,bottom),.5))
    for k in range(6):
        faces.extend([(front[k],front[k+1],rear[k+1],rear[k]),(basefront[k],basefront[k+1],front[k+1],front[k]),(rear[k],rear[k+1],baserear[k+1],baserear[k]),(basefront[k+1],basefront[k],baserear[k],baserear[k+1])])
    faces.extend([(front[0],rear[0],baserear[0],basefront[0]),(front[-1],basefront[-1],baserear[-1],rear[-1])])
    step_stats.append({'step_from_bottom':j+1,'width_m':(left[j]+right[j])*14.125,'tread_depth_m':(yb[j+1]-yb[j])*14.125,'stone_thickness_m':(z-bottom)*14.125})
new=bpy.data.meshes.new('Weighted_Authored_Stone_Steps');new.from_pydata(verts,[],faces);new.update()
bm=bmesh.new();bm.from_mesh(new);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(new);bm.free()
st=bpy.data.objects.new('Weight_Author_Stairs',new);s.collection.objects.link(st)
for mat in objects['Weight_Previous_Stairs'].data.materials:new.materials.append(mat)
for p in new.polygons:p.use_smooth=False
att=new.attributes.new('Authored_Structural_Curvature','FLOAT','POINT');att.data.foreach_set('value',np.array(curves,np.float32))
att=new.attributes.new('Authored_Moss_Region','FLOAT','POINT');att.data.foreach_set('value',np.zeros(len(verts),np.float32))
for ob in s.objects:ob.select_set(False)
st.select_set(True);bpy.context.view_layer.objects.active=st;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.012,area_weight=.4);bpy.ops.object.mode_set(mode='OBJECT')
old=objects['Weight_Previous_Stairs'];s.collection.objects.unlink(old);old.hide_render=True
# Clean broad mineral color; limit soft pooling and retain selective fracture marks.
mat=rock.data.materials[0];mat.name='Authored_Clean_Weight_Stone';n=mat.node_tree.nodes
palette=n['Cool recess to warm mineral wash'].color_ramp
for elem,col in zip(palette.elements,[(.157,.167,.145,1),(.185,.193,.164,1),(.216,.219,.184,1),(.247,.240,.201,1)]):elem.color=col
n['Quiet middle scale wash'].inputs[0].default_value=.16
n['Shallow broken planes'].inputs['Strength'].default_value=.24
n['Selective dark fracture strokes'].inputs[2].default_value=(.085,.098,.081,1)
n['Broken light on exposed fractures'].inputs[2].default_value=(.29,.28,.237,1)
st.data.materials[0]=mat
s['revision']='rock-cape-weight-author-1'
bpy.data.libraries.write(str(A/'rock_cape_weight_authoring.blend'),{s},fake_user=True,compress=True)
def bounds(vs):return [[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]]
def gd(v):return [v.x,v.z,-v.y]
anchors={}
for key,vals in fit['sample_anchors'].items():
    p=Vector((vals[0],-vals[2],vals[1]));anchors[key]=gd(expand(p)) if key in ['cape_center','fire_center'] else vals
anchors['cape_stair_bottom']=gd(P@Vector((xc(yb[0]+.005),yb[0]+.005,zh[0])))
report={'scene':SN,'revision':s['revision'],'bounds_before':bounds(before),'bounds_after':bounds([P@v.co for v in me.vertices]),'source_rock_dependency':'Existing measured Tripo surface, expanded in controlled regions; not an independent sculpting demonstration.','stair_steps':step_stats,'cleared_covered_rock_faces':len(removed),'sample_anchors':anchors,'placement_matrix':fit['placement_matrix']}
(O/'author.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps({'scene':SN,'stairs':len(step_stats),'rock_bounds':report['bounds_after'],'removed_covered_faces':len(removed)}))
