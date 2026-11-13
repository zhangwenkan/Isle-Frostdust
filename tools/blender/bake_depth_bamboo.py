"""Bake our eastern 3D bamboo to transparent color/normal sprites via Blender MCP.

No external geometry generation. Keeps the actual island scene untouched.
"""
import bpy,bmesh,math,json,time,traceback
from pathlib import Path
from mathutils import Vector,Matrix
R=Path('D:/自己做着玩的/孤屿霜尘');A=R/'assets/bamboo_depth';O=R/'artifacts/bamboo-mist-depth-review'
A.mkdir(exist_ok=True)
island=bpy.data.scenes['Island_Refined']
if bpy.data.scenes.get('Bamboo_Sprite_Studio'):
    old=bpy.data.scenes['Bamboo_Sprite_Studio']
    for ob in list(old.objects):bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.scenes.remove(old)
studio=bpy.data.scenes.new('Bamboo_Sprite_Studio');bpy.context.window.scene=studio
studio.render.engine='CYCLES';studio.cycles.samples=12
studio.cycles.use_denoising=False;studio.render.film_transparent=True
studio.render.image_settings.file_format='PNG';studio.render.image_settings.color_mode='RGBA';studio.render.image_settings.color_depth='8'
studio.view_settings.view_transform='Standard';studio.view_settings.look='None';studio.view_settings.exposure=0;studio.view_settings.gamma=1
world=bpy.data.worlds.new('BambooBakeWorld');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[1].default_value=0;studio.world=world
camd=bpy.data.cameras.new('BambooBakeCamera');cam=bpy.data.objects.new('BambooBakeCamera',camd);studio.collection.objects.link(cam);studio.camera=cam
camd.type='ORTHO';camd.clip_end=100
angle=math.radians(18);up=Vector((0,math.sin(angle),math.cos(angle)));front=Vector((0,-math.cos(angle),math.sin(angle)))
cam.rotation_euler=(-front).to_track_quat('-Z','Y').to_euler()

def components(me):
    adj=[[] for _ in me.vertices]
    for e in me.edges:a,b=e.vertices;adj[a].append(b);adj[b].append(a)
    rem=set(range(len(adj)));groups=[]
    while rem:
        seed=min(rem);rem.remove(seed);stack=[seed];ids=[]
        while stack:
            vi=stack.pop();ids.append(vi)
            for k in adj[vi]:
                if k in rem:rem.remove(k);stack.append(k)
        groups.append(sorted(ids))
    return groups

def pigment_mat(kind):
    mat=bpy.data.materials.new('FineBake_'+kind);mat.use_nodes=True
    ns=mat.node_tree.nodes;ns.clear();lk=mat.node_tree.links
    out=ns.new('ShaderNodeOutputMaterial');em=ns.new('ShaderNodeEmission');lk.new(em.outputs[0],out.inputs['Surface'])
    vc=ns.new('ShaderNodeVertexColor');vc.layer_name='InkColor'
    # Mild directional modeling in the pigment, supplemented by dynamic normals.
    geo=ns.new('ShaderNodeNewGeometry');dot=ns.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT'
    dot.inputs[1].default_value=Vector((-.5,-.4,.76)).normalized();lk.new(geo.outputs['Normal'],dot.inputs[0])
    shade=ns.new('ShaderNodeMapRange');shade.inputs['From Min'].default_value=-1;shade.inputs['From Max'].default_value=1
    shade.inputs['To Min'].default_value=.70 if kind=='Stem' else .78;shade.inputs['To Max'].default_value=1.15
    lk.new(dot.outputs['Value'],shade.inputs['Value'])
    mix=ns.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1
    lk.new(vc.outputs['Color'],mix.inputs[1]);lk.new(shade.outputs['Result'],mix.inputs[2])
    if kind=='Leaf':
        uv=ns.new('ShaderNodeTexCoord');xy=ns.new('ShaderNodeSeparateXYZ');lk.new(uv.outputs['UV'],xy.inputs[0])
        sub=ns.new('ShaderNodeMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=.5;lk.new(xy.outputs['X'],sub.inputs[0])
        ab=ns.new('ShaderNodeMath');ab.operation='ABSOLUTE';lk.new(sub.outputs[0],ab.inputs[0])
        line=ns.new('ShaderNodeMapRange');line.inputs['From Min'].default_value=.012;line.inputs['From Max'].default_value=.05
        line.inputs['To Min'].default_value=.81;line.inputs['To Max'].default_value=1;line.clamp=True;lk.new(ab.outputs[0],line.inputs['Value'])
        brush=ns.new('ShaderNodeMixRGB');brush.blend_type='MULTIPLY';brush.inputs[0].default_value=1
        lk.new(mix.outputs[0],brush.inputs[1]);lk.new(line.outputs['Result'],brush.inputs[2]);lk.new(brush.outputs[0],em.inputs[0])
    else:lk.new(mix.outputs[0],em.inputs[0])
    return mat
stem=pigment_mat('Stem');leaf=pigment_mat('Leaf')
normalmat=bpy.data.materials.new('FineBake_SurfaceNormal');normalmat.use_nodes=True
ns=normalmat.node_tree.nodes;ns.clear();lk=normalmat.node_tree.links
out=ns.new('ShaderNodeOutputMaterial');em=ns.new('ShaderNodeEmission');lk.new(em.outputs[0],out.inputs['Surface'])
geo=ns.new('ShaderNodeNewGeometry');sep=ns.new('ShaderNodeSeparateXYZ');lk.new(geo.outputs['Normal'],sep.inputs[0])
combine=ns.new('ShaderNodeCombineXYZ')
for dest,source,sign in [('X','X',1),('Y','Z',1),('Z','Y',-1)]:
    mul=ns.new('ShaderNodeMath');mul.operation='MULTIPLY_ADD';mul.inputs[1].default_value=sign*.5;mul.inputs[2].default_value=.5
    lk.new(sep.outputs[source],mul.inputs[0]);lk.new(mul.outputs[0],combine.inputs[dest])
lk.new(combine.outputs[0],em.inputs[0])
source_cache={}
def culm(source_name,chosen,shift,turn):
    source=island.objects[source_name];me=source.data
    if source_name not in source_cache:
        roots=[source.matrix_world.inverted()@Vector((r[0],-r[2],r[1])) for r in json.loads(source['root_positions_godot'])]
        groups=components(me);owner={v:min(ids) for ids in groups for v in ids}
        starts=sorted((owner[min(me.vertices,key=lambda v:(v.co-r).length_squared).index],i) for i,r in enumerate(roots))
        source_cache[source_name]=(roots,starts)
    roots,starts=source_cache[source_name];start,k=starts[chosen];end=starts[chosen+1][0] if chosen+1<len(starts) else len(me.vertices)
    local=me.copy();bm=bmesh.new();bm.from_mesh(local);bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if not start<=v.index<end],context='VERTS');bm.to_mesh(local);bm.free()
    # Each main lateral branch is a connected 15-vertex tube followed by its
    # 3 twig fans. Remove the complete lowest branch assemblies, not leaf tips.
    groups=components(local)
    branches=[ids for ids in groups if len(ids)==15]
    root=source.matrix_world@roots[k]
    height=max((source.matrix_world@v.co-root).z for v in local.vertices)
    branch_ranges=[]
    for n,ids in enumerate(branches):
        branch_start=min(ids)
        branch_end=min(branches[n+1]) if n+1<len(branches) else len(local.vertices)-35
        anchor_height=(source.matrix_world@local.vertices[branch_start].co-root).z/height
        if anchor_height<.59:branch_ranges.append((branch_start,branch_end))
    if branch_ranges:
        bm=bmesh.new();bm.from_mesh(local);bm.verts.ensure_lookup_table()
        gone=[v for v in bm.verts if any(a<=v.index<b for a,b in branch_ranges)]
        bmesh.ops.delete(bm,geom=gone,context='VERTS');bm.to_mesh(local);bm.free()
    print('RAISED_CROWN',source_name,chosen,'removed_branch_fans',len(branch_ranges))
    transform=Matrix.Rotation(turn,4,'Z')
    for v in local.vertices:
        v.co=transform@((source.matrix_world@v.co-root)*(6.0/height))+Vector((shift,0,0))
    indices=[p.material_index for p in local.polygons]
    local.materials.clear();local.materials.append(stem);local.materials.append(leaf)
    for p,mi in zip(local.polygons,indices):p.material_index=mi
    local.update()
    obj=bpy.data.objects.new('FineSource_'+source_name+'_'+str(chosen),local);studio.collection.objects.link(obj)
    return obj

specs=[('slender_a','Depth_Bamboo_Main_07',[(0,0,.12)]),('slender_b','Depth_Bamboo_Main_08',[(2,0,-.25)]),('slender_c','Depth_Bamboo_Main_09',[(5,0,.30)]),
       ('cluster_a','Depth_Bamboo_Main_07',[(1,-.62,.2),(3,.15,-.4),(5,.68,.1)]),('cluster_b','Depth_Bamboo_Main_08',[(0,-.65,-.3),(4,0,.2),(6,.7,.6)])]
variants=[]
for name,src,spec in specs:
    objects=[culm(src,k,shift,turn) for k,shift,turn in spec]
    for ob in objects:ob.name='FineSource_'+name+'_'+ob.name
    pts=[ob.matrix_world@v.co for ob in objects for v in ob.data.vertices]
    xmin=min(p.x for p in pts)-.12;xmax=max(p.x for p in pts)+.12
    vmin=min(0,min(p.dot(up) for p in pts))-.10;vmax=max(p.dot(up) for p in pts)+.12
    h=vmax-vmin;w=xmax-xmin
    width=int(math.ceil(1024*w/h/64))*64
    variants.append(dict(name=name,source=src,selected_culms=[s[0] for s in spec],objects=[o.name for o in objects],center=[(xmin+xmax)/2,(vmin+vmax)/2],height=h,required_width=w,width_px=width,height_px=1024,world_height=6.0))
    for ob in objects:ob.hide_render=True

jobs=[(i,mode) for i in range(len(variants)) for mode in ['color','normal']]
state=dict(next=0,jobs=len(jobs),status='queued',variants=variants)
def write_state(): (O/'bake-status.json').write_text(json.dumps(state,indent=2),encoding='utf-8')
write_state()
def run_next():
    try:
        if state['next']>=len(jobs):
            state['status']='complete';write_state()
            (A/'atlas-manifest.json').write_text(json.dumps(dict(source='Own eastern bamboo with lowest complete branch fans removed in Blender MCP; clear lower forest sightlines',variants=variants),indent=2),encoding='utf-8')
            bpy.context.window.scene=studio
            bpy.ops.wm.save_as_mainfile(filepath=str(A/'bamboo_sprite_source.blend'),copy=True)
            bpy.context.window.scene=island
            return None
        i,mode=jobs[state['next']];entry=variants[i];state['status']='rendering';state['current']=entry['name']+'_'+mode;write_state()
        for e in variants:
            for n in e['objects']:bpy.data.objects[n].hide_render=e['name']!=entry['name']
        studio.render.resolution_x=entry['width_px'];studio.render.resolution_y=1024;studio.render.resolution_percentage=100
        camd.ortho_scale=entry['height'];cx,cy=entry['center'];cam.location=Vector((cx,0,0))+up*cy+front*20
        # Read the actual camera bounds instead of assuming Blender's sensor fit.
        frame=camd.view_frame(scene=studio);w=max(p.x for p in frame)-min(p.x for p in frame);h=max(p.y for p in frame)-min(p.y for p in frame)
        camd.ortho_scale*=max(entry['height']/h,entry['required_width']/w)
        frame=camd.view_frame(scene=studio);w=max(p.x for p in frame)-min(p.x for p in frame);h=max(p.y for p in frame)-min(p.y for p in frame)
        entry['plane_bounds']=[cx-w/2,cx+w/2,(cy-h/2)/math.cos(angle),(cy+h/2)/math.cos(angle)]
        studio.view_layers[0].material_override=normalmat if mode=='normal' else None
        studio.view_settings.view_transform='Raw' if mode=='normal' else 'Standard'
        studio.render.filepath=str(A/(entry['name']+'_'+mode+'.png'))
        bpy.ops.render.render(write_still=True,scene=studio.name)
        state['next']+=1;write_state();return .3
    except Exception:
        state['status']='error';state['error']=traceback.format_exc();write_state();bpy.context.window.scene=island;return None
bpy.app.timers.register(run_next,first_interval=1.0)
print('FINE_BAMBOO_BAKE_QUEUED',len(jobs))
