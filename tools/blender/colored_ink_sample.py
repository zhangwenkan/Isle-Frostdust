"""Author the western ink-and-color sample ONLY through Blender MCP."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
OUT=ROOT/'artifacts/colored-ink-sample-review'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()

def coll(name):
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in scene.collection.children:scene.collection.children.link(c)
    return c
sample=coll('28_Colored_Ink_Sample');archive=coll('90_Before_Colored_Ink_Sample')
for ob in list(sample.objects):bpy.data.objects.remove(ob,do_unlink=True)
def archive_object(ob):
    for c in list(ob.users_collection):c.objects.unlink(ob)
    archive.objects.link(ob);ob.hide_set(True);ob.hide_render=True
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def color(h):return tuple(linear(int(h[i:i+2],16)/255) for i in (0,2,4))+(1,)
def mat(name,hex_color,texture=None,vertex=None):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    nodes=m.node_tree.nodes;nodes.clear();bs=nodes.new('ShaderNodeBsdfPrincipled');out=nodes.new('ShaderNodeOutputMaterial')
    bs.inputs['Base Color'].default_value=color(hex_color);bs.inputs['Roughness'].default_value=1
    m.node_tree.links.new(bs.outputs['BSDF'],out.inputs['Surface']);m.diffuse_color=color(hex_color)
    if texture:
        t=nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/texture),check_existing=True);t.image.reload()
        m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color'])
    if vertex:
        v=nodes.new('ShaderNodeVertexColor');v.layer_name=vertex;m.node_tree.links.new(v.outputs['Color'],bs.inputs['Base Color'])
    return m
rockmats=[mat('InkSample_Rock_'+str(i),'849792','assets/colored_ink_sample/rock_brush_%d.png'%i) for i in range(2)]
stemmat=mat('InkSample_Bamboo_Stem','526c54',vertex='InkColor')
leafmat=mat('InkSample_Bamboo_Leaf','4a6c52',vertex='InkColor')
grassmat=mat('InkSample_Grass','536f51',vertex='InkColor')
land=scene.objects['Fish_West_Continuous_Land']
tree=BVHTree.FromPolygons([land.matrix_world@v.co for v in land.data.vertices],[tuple(p.vertices) for p in land.data.polygons])

# Four individually placed stones form the two pairs already in the normal view.
# Each uses the existing uneven stone topology with a sloping, painted shoulder.
rock_reports=[]
for i,index in enumerate([2,3,4,5]):
    old=scene.objects['Fish_Ground_Rock_%02d_Body'%index]
    source=[old.matrix_world@v.co for v in old.data.vertices]
    low=Vector([min(p[a] for p in source) for a in range(3)]);high=Vector([max(p[a] for p in source) for a in range(3)])
    center=(low+high)*.5;width=(high.x-low.x)*1.04;depth=(high.y-low.y)*.91;height=(high.z-low.z)*1.16
    support=tree.ray_cast(Vector((center.x,center.y,30)),Vector((0,0,-1)))[0]
    base=(support.z if support is not None else low.z)-.35
    # Retain the established uneven stone topology, shaping a sloping shoulder
    # and an embedded broad foot instead of extruding a flat slab silhouette.
    me=old.data.copy();me.name='Ink_Leaning_Stone_%02d'%index
    for v,p in zip(me.vertices,source):
        u=(p.x-low.x)/(high.x-low.x)-.5
        q=(p.y-low.y)/(high.y-low.y)-.5
        t=(p.z-low.z)/(high.z-low.z)
        lean=.31 if i%2==0 else -.20
        x=center.x+(u*(1.12-.20*t)+lean*(t-.3))*width
        y=center.y+q*depth+.12*t*depth
        # A broad slanted face keeps intermediate mass and uneven side shoulders.
        if q<-.12:y=y*.60+(center.y-.40*depth+.20*t*depth+.10*u*depth)*.40
        z=base+(t**.88)*height
        hit=tree.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))[0]
        if hit is not None and t<.48:
            z=min(z,hit.z-.16)
        v.co=Vector((x,y,z))
    bm=bmesh.new();bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
    boundary=[e for e in bm.edges if e.is_boundary]
    if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
    ob=bpy.data.objects.new('InkSample_Rock_%02d'%index,me);sample.objects.link(ob)
    me.materials.clear();me.materials.append(rockmats[i%2])
    uv=me.uv_layers.active;uv.name='StructurePainting'
    for p in me.polygons:
        p.use_smooth=True
        for li in p.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv=((v.x-center.x)/width+.50,(v.z-base)/height)
    ob['source_role']='Hand-composed leaning stone; front projection for structural brush marks'
    bpy.context.view_layer.objects.active=ob
    modifier=ob.modifiers.new('Broad plane normals','WEIGHTED_NORMAL')
    modifier.keep_sharp=False;modifier.weight=35
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    archive_object(old)
    rock_reports.append({'object':ob.name,'replaces':old.name,'base_z':base,'height':height,'vertices':len(me.vertices),'uv':'StructurePainting'})

# Reorganize existing bamboo leaf components while preserving each root and its
# original wind weights. UV0 records leaf-side and tip coordinates for brush edges.
bamboo_reports=[]
for index in [3,4,5]:
    old=scene.objects['Depth_Bamboo_Main_%02d'%index]
    me=old.data.copy();ob=bpy.data.objects.new('InkSample_Bamboo_%02d'%index,me);sample.objects.link(ob);ob.matrix_world=old.matrix_world.copy()
    adj=[set() for v in me.vertices]
    for e in me.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
    leaf_ids=set(v for p in me.polygons if p.material_index==1 for v in p.vertices)
    remaining=set(leaf_ids);groups=[]
    while remaining:
        seed=min(remaining);stack=[seed];remaining.remove(seed);component=[]
        while stack:
            v=stack.pop();component.append(v)
            for n in adj[v]:
                if n in remaining:remaining.remove(n);stack.append(n)
        groups.append(sorted(component))
    remove=set();valid=[]
    for k,ids in enumerate(groups):
        if len(ids)!=7:continue
        # Empty pockets vary spatially; entire leaves are removed, never fragments.
        base=me.vertices[ids[0]].co
        band=math.sin(base.x*1.7+base.y*.9+base.z*.8+index)
        if (k%4==1 and band>-.25) or (k%7 in [2,3]):remove.update(ids);continue
        axis=(me.vertices[ids[6]].co-base).normalized()
        for j in [1,3,4,5]:
            v=me.vertices[ids[j]];projection=base+axis*(v.co-base).dot(axis)
            v.co=projection+(v.co-projection)*1.12
        valid.append(ids)
    uv=me.uv_layers[0]
    lookup={vid:(k,j) for k,ids in enumerate(valid) for j,vid in enumerate(ids)}
    coords=[(.5,0),(0,.43),(.5,.43),(1,.43),(.22,.76),(.78,.76),(.5,1)]
    for loop in me.loops:
        if loop.vertex_index in lookup:
            _,j=lookup[loop.vertex_index];uv.data[loop.index].uv=coords[j]
    ca=me.color_attributes.get('InkColor') or me.color_attributes.new(name='InkColor',type='FLOAT_COLOR',domain='POINT')
    palette=['3e5b35','4f6c3f','617b48','738956']
    old_colors=me.color_attributes.get('DepthColor')
    for v in me.vertices:
        h=palette[int(abs(math.sin(v.co.x*.8+v.co.y*.7+v.co.z*.3))*3.99)]
        c=color(h if v.index in leaf_ids else '687b49')
        if v.index not in leaf_ids and old_colors:
            source_color=old_colors.data[v.index].color
            amount=max(.76,min(1.13,.78+source_color[0]*.65))
            c=tuple(t*amount for t in c[:3])+(1,)
        ca.data[v.index].color=c
    me.color_attributes.active_color=ca;me.color_attributes.render_color_index=list(me.color_attributes).index(ca)
    bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[bm.verts[i] for i in remove],context='VERTS')
    bm.to_mesh(me);bm.free()
    indices=[p.material_index for p in me.polygons]
    me.materials.clear();me.materials.append(stemmat);me.materials.append(leafmat)
    for p,mi in zip(me.polygons,indices):p.material_index=mi
    for attribute in list(me.color_attributes):
        if attribute.name!='InkColor':me.color_attributes.remove(attribute)
    me.update()
    ob['root_positions_godot']=old.get('root_positions_godot','')
    archive_object(old)
    bamboo_reports.append({'object':ob.name,'retained_leaf_groups':len(valid),'removed_leaf_groups':len(remove)//7,'uv':[u.name for u in me.uv_layers]})

# Small real grass clusters give the painted path edge an irregular silhouette.
land=scene.objects['Fish_West_Continuous_Land']
tree=BVHTree.FromPolygons([land.matrix_world@v.co for v in land.data.vertices],[tuple(p.vertices) for p in land.data.polygons])
vertices=[];faces=[];colors=[];uvs=[];weights=[];roots=[];grass_positions=[]
for k in range(63):
    x=-13.5+k*.185+.07*math.sin(k*2.31)
    if k%8 in [2,3,4]:continue
    side=-1 if k%2==0 else 1
    z=.4+math.sin(x*.25)*.44+side*(.78+.12*math.sin(k*1.7))
    grass_positions.append((x,z))
retired_grass=[]
for index in range(4,11):
    old=next((o for o in scene.objects if o.name.startswith('Coast_Low_Grass_%02d.'%index)),None)
    if old is None:continue
    points=[old.matrix_world@v.co for v in old.data.vertices]
    cx=sum(p.x for p in points)/len(points);cz=-sum(p.y for p in points)/len(points)
    for j in range(9):
        x=cx+math.sin(j*2.399)*(.18+.30*j/9);z=cz+math.cos(j*2.399)*(.12+.28*j/9)
        if abs(z-(.4+math.sin(x*.25)*.44))>.86:grass_positions.append((x,z))
    retired_grass.append(old.name);archive_object(old)
for k,(x,z) in enumerate(grass_positions):
    hit=tree.ray_cast(Vector((x,-z,30)),Vector((0,0,-1)))[0]
    if hit is None:continue
    roots.append(tuple(hit))
    for j in range(3+k%3):
        length=.08+.13*(.5+.5*math.sin(k*2.1+j*1.6))
        root=hit+Vector(((j-1.5)*.038,.02*math.sin(j),-.012))
        tip=root+Vector(((j-1.5)*.045+.04*math.sin(k),.015*math.cos(k),length))
        mid=root.lerp(tip,.43);width=.018
        points=[root,mid+Vector((-width,0,0)),mid+Vector((width,0,0)),tip]
        offset=len(vertices);vertices.extend(points);faces.extend([(offset,offset+1,offset+2),(offset+1,offset+3,offset+2)])
        colors.extend([color(['586e40','687e4b','607749'][k%3])]*4);weights.extend([0,.43,.43,1]);uvs.extend([(.5,0),(0,.43),(1,.43),(.5,1)])
me=bpy.data.meshes.new('InkSample_Path_Grass');me.from_pydata(vertices,[],faces);me.materials.append(grassmat);me.update()
ob=bpy.data.objects.new('InkSample_Path_Grass',me);sample.objects.link(ob)
ca=me.color_attributes.new(name='InkColor',type='FLOAT_COLOR',domain='POINT');ca.data.foreach_set('color',[c for col in colors for c in col])
u=me.uv_layers.new(name='BrushUV');w=me.uv_layers.new(name='WindWeight')
for loop in me.loops:u.data[loop.index].uv=uvs[loop.vertex_index];w.data[loop.index].uv=(weights[loop.vertex_index],0)

# The land mesh and walking strip remain byte-for-byte geometrically identical.
report={'rocks':rock_reports,'bamboo':bamboo_reports,'grass_clusters':len(roots),'grass_roots':roots,'retired_grass':retired_grass,'terrain_vertices':len(land.data.vertices)}
(OUT/'blender-authoring.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
manifest_path=ROOT/'assets/island_blender/asset_manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['revision']='Western colored ink sample: shaped stones, brush ground/path and bamboo; prior coast retained elsewhere'
manifest['style_reference']='Existing coastal layout plus user-supplied colored ink references (2026-11-08) for the western sample'
reference='../../artifacts/colored-ink-sample-review/README.md'
if reference not in manifest['source_manifests']:manifest['source_manifests'].append(reference)
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('COLORED_INK_SAMPLE_EXPORTED',len(rock_reports),'rocks',len(bamboo_reports),'bamboo clumps',len(roots),'grass groups')
