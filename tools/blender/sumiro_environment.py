"""Blender MCP only: fit Sumiro's inspected assets to the existing playable coast."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'artifacts/sumiro-style-review';ASSET=ROOT/'assets/sumiro'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
STAGE='sample'
stagefile=OUT/'authoring-stage.txt'
if stagefile.exists():STAGE=stagefile.read_text().strip()
def G(p):return Vector((p[0],-p[2],p[1]))
def DG(p):return Vector((p.x,p.z,-p.y))
def collection(name):
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in scene.collection.children:scene.collection.children.link(c)
    return c
def archive(ob):
    for c in list(ob.users_collection):c.objects.unlink(ob)
    old.objects.link(ob);ob.hide_set(True);ob.hide_render=True
old=collection('90_Pre_Sumiro_Environment')
col=collection('28_Sumiro_Coast');trees=collection('29_Sumiro_Pines');hills=collection('30_Sumiro_Ink_Hills')
for c in [col,trees,hills]:
    for ob in list(c.objects):bpy.data.objects.remove(ob,do_unlink=True)
for ob in list(scene.objects):
    if any(c.name.startswith('90_') for c in ob.users_collection):continue
    if ob.name.startswith(('Cliff_Fractures_','Cliff_Fern_','Depth_Bamboo_Main_','Coast_Low_Grass_','Fish_Ground_Rock_','Mist_Ridge_')):archive(ob)
def src(name):return bpy.data.objects[name]
def dup(source,name,c):
    ob=source.copy();ob.data=source.data.copy();ob.name=name;c.objects.link(ob)
    ob.parent=None;ob.matrix_world=source.matrix_world.copy();ob.hide_set(False);ob.hide_render=False
    return ob
def image_mat(name,path=None,base=(1,1,1,1)):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    m.diffuse_color=base;m['source']='https://xikhar.github.io/sumiro/'
    nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=base;bs.inputs['Roughness'].default_value=1.0
    if path:
        tex=nt.nodes.get('SumiroSource') or nt.nodes.new('ShaderNodeTexImage');tex.name='SumiroSource';tex.image=bpy.data.images.load(str(path),check_existing=True)
        nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
        if 'tufts' in str(path):nt.links.new(tex.outputs['Alpha'],bs.inputs['Alpha'])
    return m
def source_material(ob,role):
    for i,m in enumerate(list(ob.data.materials)):
        n=m.copy();n.name='Sumiro_'+role+'_'+ob.name;n['sumiro_role']=role
        for tex in n.node_tree.nodes:
            if tex.type=='TEX_IMAGE' and tex.image:
                # Unpack exact embedded upstream look maps to an attributable asset path.
                im=tex.image;file=ASSET/'env_cliff'/(im.name.split('.')[0]+'.png')
                if not file.exists():im.filepath_raw=str(file);im.file_format='PNG';im.save()
                tex.image=bpy.data.images.load(str(file),check_existing=True)
        ob.data.materials[i]=n
def finish(ob):
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
    ob['sumiro_source']='https://xikhar.github.io/sumiro/';ob['authoring']='Adapted in Blender via Blender MCP'
def height(x,z):
    if x>10:return 1.15+math.sin(x*.37)*.18+max(0,-z)*.16
    return 1.65+(4.5-x)*.127+math.sin(x*.39)*.16+math.cos(z*1.3+x*.21)*.10+max(0,-z-.3)*.23
def pz(x):return .25 if 4.5<=x<=14 else .4+math.sin(x*.25)*.44
def lerp(a,b,t):return a+(b-a)*t
land={};edge={}
for name in ['Fish_West_Continuous_Land','Fish_East_Continuous_Land']:
    ob=src(name);east='East' in name;n=52 if east else 100
    baseline=bpy.data.meshes.get(name+'_Before_Sumiro')
    if baseline is None:baseline=ob.data.copy();baseline.name=name+'_Before_Sumiro';baseline.use_fake_user=True
    ob.data=baseline.copy()
    edge[east]=[DG(ob.matrix_world@ob.data.vertices[i*26+25].co) for i in range(n+1)]
    top=image_mat('Sumiro_Path_Ground',ASSET/'env_cliff/look_path.png')
    rock=image_mat('Sumiro_Cliff_Base',ASSET/'env_cliff/look_cliff.png')
    oldm=[m.name for m in ob.data.materials]
    indices={i:('Ground' in m or 'Grass' in m or 'Path' in m) for i,m in enumerate(oldm)}
    ob.data.materials.clear();ob.data.materials.append(top);ob.data.materials.append(rock)
    for poly in ob.data.polygons:poly.material_index=0 if indices.get(poly.material_index,False) else 1
    land[east]=ob
def edge_at(x,east):
    a=edge[east]
    for p,q in zip(a,a[1:]):
        if p.x<=x<=q.x:return p.lerp(q,(x-p.x)/max(q.x-p.x,1e-6))
    return a[0] if x<a[0].x else a[-1]

# Continuous authored outer face: use the actual source silhouette, normals, UV and RGB look map.
source=src('SRC_env_cliff_path__face_outer')
points=[source.matrix_world@v.co for v in source.data.vertices]
source_uv={}
for loop in source.data.loops:source_uv[loop.vertex_index]=source.data.uv_layers.active.data[loop.index].uv.copy()
rim={}
for i,p in enumerate(points):
    u,v=source_uv[i];key=round(v,5)
    if key not in rim or u<rim[key][0]:rim[key]=(u,p)
for east,label,x0,x1 in [(False,'West',-19.5,4.1),(True,'East',14.6,26.1)]:
    ob=dup(source,'Sumiro_Cliff_'+label,col);ob.matrix_world=Matrix.Identity(4)
    for v,p in zip(ob.data.vertices,points):
        t=source_uv[v.index].y;x=lerp(x0,x1,t);e=edge_at(x,east);r=rim[round(t,5)][1]
        depth=max(0,r.z-p.z);drop=depth*(.34 if not east else .24)
        z=e.z+.018+(r.x-p.x)*.24
        v.co=G((x,e.y+.008-drop,z))
    source_material(ob,'Face');finish(ob)

# The path stays at exactly the existing foot/bridge height. The original path paint provides the pale wash.
# The hinterland wall is the original wall mesh, proportioned for the side-view camera.
# Its source upper and end boundaries were outside the original camera. Fit them
# below the terrain, with the authored folds providing the visible bank shape.
# The original back wall is camera-cropped at its top and ends. It stays in the
# source archive; the continuous outer face supplies the coast's visible cliff.

# Original sculpted lobes and boulder forms seated on the coast, never bevelled tile slabs.
rockspec=[('lobe_d1',-16.3,-3.1,.22,.2),('lobe_m4',-9.5,-3.8,.25,-.4),('lobe_d0',.8,-2.4,.35,.1),('lobe_m5',18.4,-2.8,.30,.8),('lobe_d2',25.1,-1.5,.23,.5)]
for i,(key,x,z,scale,yaw) in enumerate(rockspec):
    source=src('SRC_env_cliff_lobes__'+key);ob=dup(source,'Sumiro_Lobe_%02d'%i,col)
    ps=[source.matrix_world@v.co for v in source.data.vertices];lo=Vector(tuple(min(p[k] for p in ps) for k in range(3)));hi=Vector(tuple(max(p[k] for p in ps) for k in range(3)))
    origin=Vector(((lo.x+hi.x)*.5,(lo.y+hi.y)*.5,lo.z));rot=Matrix.Rotation(yaw,4,'Z')
    for v,p in zip(ob.data.vertices,ps):v.co=rot@((p-origin)*scale)+G((x,height(x,z)-.06,z))
    ob.matrix_world=Matrix.Identity(4);source_material(ob,'Lobe');finish(ob)

placement=json.loads((OUT/'source/assets/env_pines/placement.json').read_text())
bark=image_mat('Sumiro_Pine_Bark',ASSET/'env_pines/bark.png');roots=image_mat('Sumiro_Pine_Root',ASSET/'env_pines/bark_root.png')
twig=image_mat('Sumiro_Pine_Twig',base=(.025,.027,.022,1));needle=image_mat('Sumiro_Pine_Needles',ASSET/'env_pines/tufts.png')
def pine(key,label,x,z,scale,yaw):
    spec=placement['trees'][key];base=G((9.3,8.35,-63.8)) if key=='hero' else Vector((0,0,0))
    rotation=Matrix.Rotation(yaw,4,'Z');target=G((x,height(x,z)-.08,z))
    group=[]
    for mname in spec['mesh']:
        source=src('SRC_env_pines_pines__'+mname);ob=dup(source,'Sumiro_Pine_'+label+'_'+mname,trees);ps=[source.matrix_world@v.co for v in source.data.vertices]
        for v,p in zip(ob.data.vertices,ps):v.co=rotation@((p-base)*scale)+target
        ob.matrix_world=Matrix.Identity(4);ob.data.materials.clear();ob.data.materials.append(roots if mname.endswith('roots') else twig if mname.endswith('twigs') else bark)
        # Source bark colours are actual diffuse colours, not the four-channel rock masks.
        ca=ob.data.color_attributes
        for a in list(ca):ca.remove(a)
        finish(ob);group.append(ob)
    verts=[];faces=[];uv=[];colors=[];weights=[]
    conv=Matrix(((1,0,0),(0,0,-1),(0,1,0)))
    for card,instances in spec['tufts'].items():
        source=src('SRC_env_pines_pines__card_'+card);me=source.data
        for instance in instances:
            q=Quaternion((instance[6],instance[3],instance[4],instance[5])).to_matrix();q=conv@q@conv.inverted()
            offset=G(instance[:3]);factor=instance[7];start=len(verts)
            for v in me.vertices:
                p=q@(v.co*factor)+offset
                verts.append(rotation@((p-base)*scale)+target);weights.append(max(0,v.co.z)*2*factor*scale)
            for poly in me.polygons:
                faces.append(tuple(start+v for v in poly.vertices))
                for li in poly.loop_indices:
                    tu,tv=me.uv_layers.active.data[li].uv
                    # The served cards still reference a 2x2 atlas, while the served
                    # tufts image contains 3x3 fans. Fit each card to one actual fan.
                    oldcell={'hero':(0,0),'wide':(1,0),'near':(0,1),'dab':(1,1)}[card]
                    newcell={'hero':(0,0),'wide':(2,0),'near':(0,1),'dab':(1,1)}[card]
                    u=(tu-(oldcell[0]*.5+.004))/.492
                    v=(1-tv-(oldcell[1]*.5+.004))/.492
                    uv.append(((newcell[0]+.012+u*.976)/3,1-(newcell[1]+.012+v*.976)/3));colors.append((instance[8],)*3+(1,))
    me=bpy.data.meshes.new('Sumiro_Needles_'+label);me.from_pydata(verts,[],faces);me.materials.append(needle);me.update()
    layer=me.uv_layers.new(name='UVMap');wind=me.uv_layers.new(name='Wind')
    for loop,t,co in zip(me.loops,uv,colors):layer.data[loop.index].uv=t;wind.data[loop.index].uv=(weights[loop.vertex_index],0)
    ca=me.color_attributes.new(name='PineTone',type='FLOAT_COLOR',domain='CORNER');ca.data.foreach_set('color',[c for colr in colors for c in colr])
    ob=bpy.data.objects.new('Sumiro_Pine_'+label+'_Needles',me);trees.objects.link(ob);finish(ob)
    return {'label':label,'source':key,'root':[x,height(x,z)-.08,z],'scale':scale,'cards':sum(len(v) for v in spec['tufts'].values())}
specs=[('hero','West_01',-12.9,-3.0,.66,.12),('behind_gate','West_02',-3.0,-3.2,.78,-.12)]
if STAGE=='full':specs += [('hero','West_Entry',-20.1,-3.5,.72,-.28),('umbrella','West_Back',-3.9,-5.6,.65,-.20),('hero','East_01',18.5,-3.4,.65,-.20),('behind_gate','East_02',24.5,-3.6,.85,.38),('pale_behind','East_Back',22.4,-7.0,1.0,.0)]
tree_report=[pine(*s) for s in specs]

# Use the upstream relief meshes and their painted alpha images, placed in separate depth bands.
# The same source rows are used at their original proportions, with uniform scales only.
hill_specs=[('NF',-85,-245,24,.30),('NXM',32,-205,20,.32),('EM',125,-210,22,.34),('NXL',48,-140,12,.30),('NL',-72,-125,15,.32),('NA4',-6,-116,12,.34)]
if STAGE=='full':hill_specs += [('NXR',-12,-176,17,.28),('NA3',38,-100,11,.36),('WXA',88,-120,13,.36),('WA1',-120,-120,9,.38),('WR',-100,-184,16,.32),('ER',143,-150,16,.35),('NA0',-37,-91,7,.44),('NA2',10,-104,9,.40)]
hill_report=[]
for i,(key,x,z,top,scale) in enumerate(hill_specs):
    source=src('SRC_backdrop_hills__'+key);ob=dup(source,'Sumiro_Hill_%02d_%s'%(i,key),hills)
    ps=[source.matrix_world@v.co for v in source.data.vertices];lo=Vector(tuple(min(p[k] for p in ps) for k in range(3)));hi=Vector(tuple(max(p[k] for p in ps) for k in range(3)))
    origin=Vector(((lo.x+hi.x)*.5,(lo.y+hi.y)*.5,hi.z));target=G((x,top,z))
    for v,p in zip(ob.data.vertices,ps):v.co=(p-origin)*scale+target
    ob.matrix_world=Matrix.Identity(4);ob.data.materials.clear();ob.data.materials.append(image_mat('Sumiro_Hill_'+key,ASSET/'backdrop/hills'/(key+'.webp')));finish(ob)
    hill_report.append({'source':key,'position':[x,top,z],'scale':scale})

# Existing bridge is already fitted to the playable route. Sumiro's wood role changes its paint, not its joints.
wood=image_mat('Sumiro_Bridge_Wood',base=(.25,.23,.19,1));rope=image_mat('Sumiro_Bridge_Rope',base=(.12,.11,.09,1))
for ob in scene.objects:
    if ob.type=='MESH' and ob.name.startswith('Bridge_'):
        ob.data.materials.clear();ob.data.materials.append(rope if 'Rope' in ob.name else wood)
        for a in list(ob.data.color_attributes):ob.data.color_attributes.remove(a)

(OUT/'authoring.json').write_text(json.dumps({'stage':STAGE,'pine_placement':tree_report,'hill_placement':hill_report,'source':'Sumiro served GLBs; adapted through Blender MCP','road':'Existing route vertices unchanged'},indent=2),encoding='utf8')
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf8'),'fish_export.py','exec'))
print('SUMIRO_EXPORTED',STAGE,len(tree_report),'pines',len(hill_report),'hill layers')
