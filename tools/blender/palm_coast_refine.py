"""Live Blender MCP authoring pass: palms, low broad grass and coastal land forms."""
import bpy,bmesh,math,json,random
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');OUT=ROOT/'assets/island_blender'
MAPS=OUT/'palm_study'
REF=Path('D:/steam/steamapps/common/I Just Wanted to Fish Demo/analysis/exported_all')
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
assert Path(bpy.data.filepath).name=='nameless_island.blend'
lod_metadata=json.loads((ROOT/'artifacts/palm-style-review/reference-lod-metadata.json').read_text())
cleaned=ROOT/'artifacts/palm-style-review/lod0';cleaned.mkdir(exist_ok=True)
def lod0_obj(file):
    # Unity 6 stores all mesh LOD index ranges in a submesh; the supplied OBJ
    # exporter concatenated every level. Filter the faces INSIDE Blender.
    mesh_name=file.rsplit('_',1)[0]
    submeshes=lod_metadata[mesh_name]['lod_info']['m_SubMeshes']
    lines=[];face_index=0;start=0;end=0;active=False
    for line in (REF/'meshes'/file).read_text().splitlines():
        if line.startswith('g '):
            group=line[2:];active=group.startswith(mesh_name+'_') and group.rsplit('_',1)[-1].isdigit()
            if active:
                part=int(group.rsplit('_',1)[-1]);level=submeshes[part]['m_Levels'][0]
                start=level['m_IndexStart']//3;count=level['m_IndexCount']
                if not count:count=lod_metadata[mesh_name]['original_index_counts'][part]
                end=start+count//3;face_index=0
        if line.startswith('f '):
            keep=active and start<=face_index<end;face_index+=1
            if not keep:continue
        lines.append(line)
    destination=cleaned/file;destination.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return destination
collection=bpy.data.collections.get('15_Palm_Coast') or bpy.data.collections.new('15_Palm_Coast')
if collection.name not in scene.collection.children:scene.collection.children.link(collection)
for ob in list(collection.objects):bpy.data.objects.remove(ob,do_unlink=True)
retired=[]
for ob in list(scene.objects):
    if ob.name.startswith(('Fish_Tree_','Fish_Tuft_')):
        retired.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
def linear(s):return s/12.92 if s<=.04045 else ((s+.055)/1.055)**2.4
def color(s):return tuple(linear(int(s[i:i+2],16)/255) for i in [0,2,4])+(1,)
def mat(name,albedo=None,normal=None,tint=(1,1,1,1),vertex=False):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes.clear()
    n=m.node_tree.nodes;p=n.new('ShaderNodeBsdfPrincipled');out=n.new('ShaderNodeOutputMaterial')
    m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface']);p.inputs['Base Color'].default_value=tint
    p.inputs['Roughness'].default_value=.88;p.inputs['Specular IOR Level'].default_value=.20
    m.diffuse_color=tint
    if albedo:
        t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(albedo),check_existing=True);t.image.pack();t.extension='EXTEND'
        m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
    if normal:
        t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(normal),check_existing=True);t.image.colorspace_settings.name='Non-Color';t.image.pack()
        nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.55
        m.node_tree.links.new(t.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],p.inputs['Normal'])
    if vertex:
        c=n.new('ShaderNodeVertexColor');c.layer_name='CoastColor';m.node_tree.links.new(c.outputs['Color'],p.inputs['Base Color'])
    return m
ground=mat('Coast_Ground',MAPS/'Island_Ground_Study.png',MAPS/'Island_Ground_Normal.png')
palm=mat('Coast_Palm',MAPS/'T_Palm_Albedo_399.png',MAPS/'T_Palm_Normal_501_OpenGL.png')
ripe=mat('Coast_Coconut_Ripe',tint=color('88704b'))
young=mat('Coast_Coconut_Young',tint=color('77814c'))
grass=mat('Coast_Grass',vertex=True)

land=[]
for name in ['Fish_West_Continuous_Land','Fish_East_Continuous_Land']:
    ob=bpy.data.objects[name];me=ob.data
    # Restore this pass's own baseline on reruns so shape edits never accumulate.
    baseline_name=name+'_Before_Palm'
    baseline=bpy.data.meshes.get(baseline_name)
    if baseline is None:
        baseline=me.copy();baseline.name=baseline_name;baseline.use_fake_user=True
    else:
        old=ob.data;ob.data=baseline.copy();me=ob.data
    east='East' in name;n=52 if east else 100;rows=26;top_count=(n+1)*rows
    boundary=[i*rows for i in range(n+1)]+[n*rows+j for j in range(1,rows)]+[i*rows+rows-1 for i in range(n-1,-1,-1)]+list(range(rows-2,0,-1))
    # Shallow contour-shaped undulations; preserve the exact walking corridor.
    for v in list(me.vertices)[:top_count]:
        x,z=v.co.x,-v.co.y;pz=.25 if 4.5<=x<=14 else .4+math.sin(x*.25)*.44
        w=max(0,min(1,(abs(z-pz)-.75)/.8))
        v.co.z+=w*(.060*math.sin(x*1.22+z*.65)+.035*math.sin(x*.73-z*1.45))
    # Form readable rock courses in the existing continuous cliff shell.
    # Their shoulders follow the coast; they are not separately scattered cubes.
    center_x=20.3 if east else -7.2
    colors=me.color_attributes.get('LandscapeColor')
    for ring in range(6):
        for j,bid in enumerate(boundary):
            v=me.vertices[top_count+ring*len(boundary)+j];original=baseline.vertices[v.index].co
            root=me.vertices[bid].co;x,z=root.x,-root.y
            delta=Vector((x-center_x,z));delta.normalize()
            front=max(0,min(1,z*.8+.5))
            buttress=.16*math.sin(x*.72+.35)+.11*math.sin(x*1.37-.4)
            # One broad ledge at the upper third and a stronger submerged foot.
            offsets=[.00,-.035,.16,-.12,.19,.12]
            amount=(offsets[ring]+buttress*(.18 if ring<2 else 1))*front
            v.co.x=original.x+delta.x*amount;v.co.y=original.y-delta.y*amount
            v.co.z=original.z+(root.z-baseline.vertices[bid].co.z)*(1-[.016,.055,.22,.54,.76,1.0][ring])
            if ring in [2,3,4]:v.co.z+=(.16*math.sin(x*.57)+.07*math.sin(x*1.21))*front
            if colors:
                base=color('7a8063' if ring==0 else ('909b91' if ring%2 else 'a1a99a'))
                shade=.94+.06*math.sin(x*.73+ring*.5)
                colors.data[v.index].color=tuple(c*shade for c in base[:3])+(1,)
    # A crisp material boundary and continuous UVs replace the airbrushed rim.
    me.materials[0]=ground
    uv=me.uv_layers.get('CoastUV') or me.uv_layers.new(name='CoastUV')
    me.uv_layers.active=uv
    for p in me.polygons:
        for li in p.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv=((v.x+20)/48,1-(-v.y+7)/12)
    me.set_sharp_from_angle(angle=math.radians(47));me.update()
    ob['coast_revision']='Palm coast, connected stepped bedrock, reference grass atlas, walking strip preserved'
    land.append(ob)

# Replace incorrect AG-packed maps on the existing reference rocks.
for key in 'ABCD':
    m=bpy.data.materials.get('Fish_Rock_'+key)
    if not m:continue
    decoded=next(MAPS.glob('T_Rock_'+key+'_Normal_*_OpenGL.png'))
    for node in m.node_tree.nodes:
        if node.type=='TEX_IMAGE' and node.image and 'Normal' in node.image.name:
            node.image=bpy.data.images.load(str(decoded),check_existing=True);node.image.colorspace_settings.name='Non-Color';node.image.pack()
        elif node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=1.0
        elif node.type=='BSDF_PRINCIPLED':
            node.inputs['Roughness'].default_value=.88;node.inputs['Specular IOR Level'].default_value=.18
    m['normal_encoding']='Unity AG decoded to RGB OpenGL';m['reference_base_color']=(.84,.88,.87)

# Replace the previous rocks' concatenated LOD meshes without changing placement.
rock_sources={'A':'Rock_A_4518.obj','B':'Rock_B_4192.obj','C':'Rock_C_3602.obj','D':'Rock_D_6272.obj'}
for key,file in rock_sources.items():
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.obj_import(filepath=str(lod0_obj(file)),forward_axis='NEGATIVE_Z',up_axis='Y',use_split_objects=False,use_split_groups=True)
    template=bpy.context.selected_objects[0]
    template.data.transform(template.matrix_world);template.matrix_world=Matrix.Identity(4)
    template.data.materials.clear();template.data.materials.append(bpy.data.materials['Fish_Rock_'+key])
    template.data.name='Coast_Rock_'+key+'_LOD0'
    for ob in list(scene.objects):
        if ob.name.startswith(('Fish_Ground_Rock_','Fish_Tidal_Reef_')) and ob.get('asset_role')=='Rock'+key:
            ob.data=template.data;ob['source_lod']=0
    bpy.data.objects.remove(template,do_unlink=True)

bpy.context.view_layer.update()
bvhs=[BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons]) for ob in land]
def height(x,z):
    hits=[b.ray_cast(Vector((x,-z,30)),Vector((0,0,-1))) for b in bvhs]
    return max((p.z for p,n,i,d in hits if p is not None),default=None)

palms=[]
placements=[('Bent',-16.4,-2.55,.82,.9),('Tall',-12.7,-4.15,.80,2.8),('Short',-8.35,-2.85,1.05,.5),('Bent',-3.15,-3.45,.84,4.2),('Young',1.25,-1.65,.93,2.7),('Short',17.55,-2.05,.95,1.5),('Tall',22,-3.10,.73,3.8),('Bent',24.35,-.7,.67,1.7)]
sources={'Bent':'Palm_Bent_4201.obj','Tall':'Palm_Tall_3358.obj','Short':'Palm_Short_4522.obj','Young':'Palm_Young_1034.obj'}
for i,(kind,x,z,s,angle) in enumerate(placements):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.obj_import(filepath=str(lod0_obj(sources[kind])),forward_axis='NEGATIVE_Z',up_axis='Y',use_split_objects=False,use_split_groups=True)
    y=height(x,z)
    for ob in list(bpy.context.selected_objects):
        part=int(ob.name.rsplit('_',1)[-1].split('.')[0])
        ob.data.transform(ob.matrix_world);ob.matrix_world=Matrix.Identity(4)
        for c in list(ob.users_collection):c.objects.unlink(ob)
        collection.objects.link(ob)
        ob.name='Coast_Palm_%02d_%s_%s'%(i,kind,['Body','Ripe','Young'][min(part,2)])
        ob.data.materials.clear();ob.data.materials.append([palm,ripe,young][min(part,2)])
        ob.location=(x,-z,y-.035);ob.scale=(s,s,s);ob.rotation_euler.z=angle
        ob['asset_role']='Palm';ob['source_mesh']=sources[kind];ob['ground_y']=y
        if part==0:palms.append({'object':ob.name,'x':x,'z':z,'ground_y':y,'scale':s,'source':sources[kind]})

# Low, broad tapered blades, organized around stone shoulders and palm roots.
# Each clump uses readable silhouette planes instead of threadlike fine blades.
patches=[(-17.2,-1.25,.8,.42),(-16.1,-2.4,.7,.48),(-14.9,1.55,.7,.38),(-12.8,-3.4,1.0,.6),(-11.5,-2.0,.95,.48),(-10.2,-1.45,.55,.3),(-8.4,-2.65,.75,.4),(-8.1,2.4,.65,.38),(-6.3,-2.7,.8,.4),(-4.6,-1.9,.85,.4),(-3.1,-3.1,.8,.5),(-.8,2.1,.75,.4),(1.3,-1.8,.7,.38),(2.7,-.9,.45,.3),(17.2,-1.5,.75,.45),(18.9,1.6,.7,.45),(21.7,-2.7,.95,.5),(23.1,-1.2,.8,.4),(24.3,.8,.7,.45)]
randomizer=random.Random(912);grass_count=0
for index,(cx,cz,rx,rz) in enumerate(patches):
    verts=[];faces=[];cols=[]
    for j in range(12):
        angle=j*2.399963;radius=math.sqrt((j+.5)/12)
        x=cx+math.cos(angle)*radius*rx;z=cz+math.sin(angle)*radius*rz
        pz=.25 if 4.5<=x<=14 else .4+math.sin(x*.25)*.44
        if abs(z-pz)<.75:continue
        y=height(x,z)
        if y is None:continue
        grass_count+=1
        for k in range(6):
            a=k*2.399963+j*.41
            h=.14+randomizer.random()*.10;width=.045+randomizer.random()*.025
            lean=.07+randomizer.random()*.065
            d=Vector((math.cos(a),math.sin(a)));side=Vector((-d.y,d.x))
            start=len(verts)
            for t,w in [(0,.28),(.48,1),(.81,.62),(1,0)]:
                bx=x+d.x*lean*t*t;bz=z+d.y*lean*t*t
                for sign in [-1,1]:
                    verts.append((bx+side.x*width*w*sign*.5,-(bz+side.y*width*w*sign*.5),y-.018+h*t))
                    cols.append(color('657b48' if t<.5 else '83965c'))
            for q in range(3):a0=start+q*2;faces.append((a0,a0+1,a0+3,a0+2))
    if not verts:continue
    me=bpy.data.meshes.new('Coast_Low_Grass_%02d'%index);me.from_pydata(verts,[],faces);me.materials.append(grass)
    attr=me.color_attributes.new(name='CoastColor',type='FLOAT_COLOR',domain='POINT')
    for i,c in enumerate(cols):attr.data[i].color=c
    for p in me.polygons:p.use_smooth=True
    me.update();ob=bpy.data.objects.new(me.name,me);collection.objects.link(ob)
    ob['asset_role']='Low stylized grass';ob['authoring']='Blender MCP; broad silhouette blades, maximum 0.24m'

bpy.context.view_layer.update()
report={'retired_objects':retired,'palms':palms,'grass_clumps':grass_count,'grass_patch_count':len(patches),'normal_fix':'Unity AG to RGB OpenGL','source_reference':'official screenshots 5351000, local supplied models/materials','walking_strip_unchanged':True,'palm_mesh_lod':0,'palm_lod_reason':'Supplied Unity export concatenates all LODs; select original LOD0 index ranges inside Blender'}
(ROOT/'artifacts/palm-style-review/authoring.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'nameless_island.blend'))
print('PALM_COAST_AUTHORED',len(palms),'palms,',grass_count,'low grass clumps; source saved.')
