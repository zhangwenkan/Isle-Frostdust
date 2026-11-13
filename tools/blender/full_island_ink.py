"""Full-island brush extension, executed only inside live Blender via MCP."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('D:/自己做着玩的/孤屿霜尘');O=R/'artifacts/full-island-ink-review'
assert Path(bpy.data.filepath).resolve()==(R/'assets/island_blender/nameless_island.blend').resolve()
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
def active():return [o for o in scene.objects if o.type=='MESH' and not any(c.name.startswith('90_') for c in o.users_collection)]
def digest(ob):
    m=ob.data;h=hashlib.sha256()
    for data in [[list(v.co) for v in m.vertices],[list(p.vertices) for p in m.polygons],
                 [list(n.vector) for n in m.corner_normals],[[list(d.uv) for d in u.data] for u in m.uv_layers],
                 [list(row) for row in ob.matrix_world]]:h.update(json.dumps(data,separators=(',',':')).encode())
    return h.hexdigest()
before={o.name:digest(bpy.data.objects.get('FullInkBaseline_'+o.name) or o) for o in active()}
arc=bpy.data.collections.get('90_Before_Full_Island_Ink')
if arc is None:arc=bpy.data.collections.new('90_Before_Full_Island_Ink');scene.collection.children.link(arc)
arc.hide_render=True
def restore(o):
    name='FullInkBaseline_'+o.name;saved=bpy.data.objects.get(name)
    if saved is None:
        saved=o.copy();saved.data=o.data.copy();saved.name=name;arc.objects.link(saved);saved.hide_set(True);saved.hide_render=True
    o.data=saved.data.copy();o.matrix_world=saved.matrix_world.copy();return saved
def color(h):
    a=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in a)+(1,)
def paint_material(name,file):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    ns=m.node_tree.nodes;ns.clear();bs=ns.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=1
    tex=ns.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/file),check_existing=True);tex.image.reload()
    out=ns.new('ShaderNodeOutputMaterial');m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);m.node_tree.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    return m
rockmat=paint_material('InkIsland_Rock_Wash','assets/full_island_ink/cliff_wash.png')
report={'grass':[],'bamboo':[],'east_rocks':[],'reefs':[]}

# Eight remaining broad grass patches adopt the sample's tapered blades and UV2.
for o in list(active()):
    saved=bpy.data.objects.get('FullInkBaseline_'+o.name)
    check=saved if saved else o
    if not any(m and m.name=='Coast_Grass' for m in check.data.materials):continue
    baseline=restore(o);me=o.data;assert len(me.vertices)%8==0
    error=0
    for start in range(0,len(me.vertices),8):
        for a,b in [(0,1),(2,3),(4,5)]:
            va=me.vertices[start+a];vb=me.vertices[start+b];mid=(va.co+vb.co)*.5
            va.co=mid+(va.co-mid)*.46;vb.co=mid+(vb.co-mid)*.46
        error=max(error,((me.vertices[start].co+me.vertices[start+1].co-baseline.data.vertices[start].co-baseline.data.vertices[start+1].co)*.5).length)
    for ca in list(me.color_attributes):me.color_attributes.remove(ca)
    ca=me.color_attributes.new(name='InkColor',type='FLOAT_COLOR',domain='POINT')
    for v in me.vertices:ca.data[v.index].color=color(['586e40','687e4b','607749'][(v.index//24)%3])
    me.color_attributes.active_color=ca;me.color_attributes.render_color_index=0
    me.materials.clear();me.materials.append(bpy.data.materials['InkSample_Grass'])
    for p in me.polygons:p.material_index=0
    for uv in list(me.uv_layers):me.uv_layers.remove(uv)
    u=me.uv_layers.new(name='BrushUV');w=me.uv_layers.new(name='WindWeight')
    coords=[(.5,0),(.5,0),(0,.48),(1,.48),(.23,.81),(.77,.81),(.5,1),(.5,1)]
    for loop in me.loops:
        p=coords[loop.vertex_index%8];u.data[loop.index].uv=p;w.data[loop.index].uv=(p[1],0)
    me.update();assert error<1e-5
    report['grass'].append({'object':o.name,'blades':len(me.vertices)//8,'root_error':error})

# Existing eastern bamboo keeps all culms, leaves, roots and wind coordinates.
for o in list(active()):
    if not o.name.startswith('Depth_Bamboo_Main_'):continue
    baseline=restore(o);me=o.data
    wind_before=[tuple(v.uv) for v in me.uv_layers[1].data]
    leafids=set(v for p in me.polygons if p.material_index==1 for v in p.vertices)
    adj=[set() for v in me.vertices]
    for e in me.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
    remaining=set(leafids);lookup={};groups=0
    while remaining:
        seed=min(remaining);remaining.remove(seed);stack=[seed];ids=[]
        while stack:
            i=stack.pop();ids.append(i)
            for j in adj[i]:
                if j in remaining:remaining.remove(j);stack.append(j)
        ids.sort()
        if len(ids)==7:
            groups+=1
            for j,i in enumerate(ids):lookup[i]=[(.5,0),(0,.43),(.5,.43),(1,.43),(.22,.76),(.78,.76),(.5,1)][j]
    for loop in me.loops:
        if loop.vertex_index in lookup:me.uv_layers[0].data[loop.index].uv=lookup[loop.vertex_index]
    for ca in list(me.color_attributes):me.color_attributes.remove(ca)
    ca=me.color_attributes.new(name='InkColor',type='FLOAT_COLOR',domain='POINT')
    for v in me.vertices:
        shade=['3e5b35','4f6c3f','617b48','738956'][int(abs(math.sin(v.co.x*.8+v.co.y*.7+v.co.z*.3))*3.99)]
        ca.data[v.index].color=color(shade if v.index in leafids else '687b49')
    me.color_attributes.active_color=ca;me.color_attributes.render_color_index=0
    indices=[p.material_index for p in me.polygons];me.materials.clear()
    me.materials.append(bpy.data.materials['InkSample_Bamboo_Stem']);me.materials.append(bpy.data.materials['InkSample_Bamboo_Leaf'])
    for p,i in zip(me.polygons,indices):p.material_index=i
    assert wind_before==[tuple(v.uv) for v in me.uv_layers[1].data]
    assert [tuple(v.co) for v in me.vertices]==[tuple(v.co) for v in baseline.data.vertices]
    report['bamboo'].append({'object':o.name,'leaves':groups,'wind_uv_unchanged':True,'positions_unchanged':True})

land=scene.objects['Fish_East_Continuous_Land']
tree=BVHTree.FromPolygons([land.matrix_world@v.co for v in land.data.vertices],[tuple(p.vertices) for p in land.data.polygons])
def height(x,y):
    hit=tree.ray_cast(Vector((x,y,30)),Vector((0,0,-1)))[0];assert hit is not None;return hit.z
for index,template,width,depth,rise,turn in [(7,'InkSample_Rock_04',1.55,1.12,.30,-8),(8,'InkSample_Rock_02',1.85,1.34,.40,11)]:
    o=scene.objects['Fish_Ground_Rock_%02d_Body'%index];base=restore(o)
    pts=[base.matrix_world@v.co for v in base.data.vertices];cx=(min(p.x for p in pts)+max(p.x for p in pts))*.5;cy=(min(p.y for p in pts)+max(p.y for p in pts))*.5
    source=scene.objects[template];sp=[source.matrix_world@v.co for v in source.data.vertices]
    lo=Vector([min(p[k] for p in sp) for k in range(3)]);hi=Vector([max(p[k] for p in sp) for k in range(3)])
    me=source.data.copy();o.data=me;o.matrix_world=Matrix.Identity(4);N=len(me.vertices)//2;a=math.radians(turn)
    g=height(cx,cy)
    cap_min=min(p.z for p in sp[N:]);cap_max=max(p.z for p in sp[N:])
    for i,(v,p) in enumerate(zip(me.vertices,sp)):
        x=((p.x-lo.x)/(hi.x-lo.x)-.5)*width;y=((p.y-lo.y)/(hi.y-lo.y)-.5)*depth
        # Different broad slants, using the already established cut-plane topology.
        x+=.11*y*(1 if index==7 else -1)
        wx=cx+math.cos(a)*x-math.sin(a)*y;wy=cy+math.sin(a)*x+math.cos(a)*y
        z=height(wx,wy)-.28 if i<N else g+rise-(cap_max-p.z)/max(.001,cap_max-cap_min)*(.20 if index==7 else .25)
        v.co=(wx,wy,z)
    for mod in list(o.modifiers):o.modifiers.remove(mod)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
    # The same restrained 16% corner-normal blend as the current sample.
    normals=[]
    for p in me.polygons:
        p.use_smooth=True
        for li in p.loop_indices:
            v=me.vertices[me.loops[li].vertex_index]
            normals.append(tuple((p.normal*.84+v.normal*.16).normalized()))
    me.normals_split_custom_set(normals)
    bm=bmesh.new();bm.from_mesh(me);assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume()>0;bm.free()
    min_gap=min(height(v.co.x,v.co.y)-v.co.z for v in me.vertices[:N]);assert min_gap>.27
    o['style_extension']='Current western clean watercolor planes; same center, embedded foot'
    report['east_rocks'].append({'object':o.name,'template':template,'center':[cx,cy],'width':width,'depth':depth,'rise':rise,'base_embed_min':min_gap,'closed':True})

# Reefs retain their silhouettes and positions, with clean watercolor pigment.
for o in list(active()):
    if not o.name.startswith('Fish_Tidal_Reef_'):continue
    restore(o);o.data.materials.clear();o.data.materials.append(rockmat)
    for p in o.data.polygons:p.material_index=0
    report['reefs'].append(o.name)

after={o.name:digest(o) for o in active()}
report['changed_geometry_uv_normals']=[n for n in before if before[n]!=after[n]]
report['unchanged_geometry_uv_normals']=[n for n in before if before[n]==after[n]]
assert before['Fish_West_Continuous_Land']==after['Fish_West_Continuous_Land']
assert before['Fish_East_Continuous_Land']==after['Fish_East_Continuous_Land']
assert all(before[n]==after[n] for n in before if n.startswith(('Bridge_','Mist_','ForestVisibility_','InkSample_Rock_')))
(O/'blender-authoring.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
exec(compile((R/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
p=R/'assets/island_blender/asset_manifest.json';m=json.loads(p.read_text(encoding='utf-8'))
m['revision']='Full-island colored brush extension: east grass and rock planes, clean coastal pigment; established terrain and mountains preserved'
ref='../../artifacts/full-island-ink-review/README.md'
if ref not in m['source_manifests']:m['source_manifests'].append(ref)
p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
print('FULL_ISLAND_INK_EXPORTED',{k:len(v) for k,v in report.items()})
