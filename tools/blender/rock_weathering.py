"""Localized rock weathering through Blender MCP; retain established scale and silhouette."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/自己做着玩的/孤屿霜尘');REVIEW=ROOT/'artifacts/rock-weathering-review'
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
assert Path(bpy.data.filepath).resolve()==(ROOT/'assets/island_blender/nameless_island.blend').resolve()
archive=bpy.data.collections.get('90_Before_Rock_Weathering') or bpy.data.collections.new('90_Before_Rock_Weathering')
if archive.name not in scene.collection.children:scene.collection.children.link(archive)
mat=bpy.data.materials['InkSample_Rock_Angular']
tex=next(n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE')
tex.image=bpy.data.images.load(str(ROOT/'assets/colored_ink_sample/rock_weathered_base.png'),check_existing=True);tex.image.reload()

# Deliberately placed wear, not a random distribution of pits and cracks.
# face, center interpolation (quad UV or polygon corner weight), ring scale, depth.
designs={
 2: {'patches':[(3,(.67,.77),(.34,.19),.016),(10,(.31,.24),(.23,.13),.011)],'chips':[(10,.050),(13,.031)]},
 3: {'patches':[(2,(.56,.77),(.28,.17),.010)],'chips':[(8,.027)]},
 4: {'patches':[(3,(.48,.80),(.31,.18),.012)],'chips':[(10,.033)]},
 0: {'patches':[(2,(.68,.78),(.27,.15),.011)],'chips':[(8,.032)]},
}
reports=[]
for index,d in designs.items():
    ob=scene.objects['InkSample_Rock_%02d'%index]
    savedname='PlaneBaseline_'+ob.name;saved=bpy.data.objects.get(savedname)
    if saved is None:
        saved=ob.copy();saved.data=ob.data.copy();saved.name=savedname
        archive.objects.link(saved);saved.hide_set(True);saved.hide_render=True
    source=saved.data;verts=[v.co.copy() for v in source.vertices];faces=[];tints=[];refnormals=[]
    patchmap={p[0]:p for p in d['patches']};patchreports=[]
    def add_face(ids,tint,normal):faces.append(tuple(ids));tints.append(tint);refnormals.append(tuple(normal))
    for p in source.polygons:
        ids=list(p.vertices);normal=p.normal.copy()
        if p.index not in patchmap:
            add_face(ids,1.,normal);continue
        _,uv,scales,depth=patchmap[p.index]
        pts=[source.vertices[i].co.copy() for i in ids];N=len(pts)
        center=sum(pts,Vector())/N
        if N==4:
            u,v=uv;target=pts[0].lerp(pts[1],u).lerp(pts[3].lerp(pts[2],u),v)
        else:
            target=center.lerp(pts[1],uv[0])+ (pts[2]-center)*uv[1]
        axis=(pts[1]-pts[0]).normalized();cross=normal.cross(axis).normalized()
        ring=[]
        # Two points per original corner allow asymmetric weathering edges
        # without altering shared outline edges of the underlying large face.
        for i in range(N):
            for j,point in enumerate([pts[i],pts[i].lerp(pts[(i+1)%N],.45)]):
                delta=point-center
                factor=[1.0,.84,1.10,.92,.94,1.06,.90,1.08,1.02,.88,1.0,.94][2*i+j]
                ring.append(target+axis*delta.dot(axis)*scales[0]*factor+cross*delta.dot(cross)*scales[1]*factor)
        start=len(verts);verts.extend(ring);M=len(ring)
        floor=[target+(q-target)*(.76 if k%3 else .81)-normal*depth for k,q in enumerate(ring)]
        verts.extend(floor)
        for i in range(N):
            j=(i+1)%N
            add_face([ids[i],ids[j],start+2*j,start+2*i+1,start+2*i],1.,normal)
        for i in range(M):
            j=(i+1)%M
            add_face([start+i,start+j,start+M+j,start+M+i],1.015,normal)
        add_face(range(start+M,start+2*M),1.025,normal)
        patchreports.append({'source_face':p.index,'depth_m':depth,'center':list(target),'width_m':max((q-target).length for q in ring)*2})
    me=bpy.data.meshes.new('Weathered_'+ob.name);me.from_pydata(verts,[],faces);me.materials.append(mat);me.update()
    # Keep a reference plane normal per face so a narrow shallow chip does not
    # turn into a deep, black crater under the stylized sky fill.
    ca=me.color_attributes.new(name='WeatherTint',type='FLOAT_COLOR',domain='CORNER')
    for p,tint in zip(me.polygons,tints):
        for li in p.loop_indices:ca.data[li].color=(tint,tint,tint*.997,1)
    me.color_attributes.active_color=ca
    me.color_attributes.render_color_index=list(me.color_attributes).index(ca)
    bm=bmesh.new();bm.from_mesh(me)
    reference=bm.faces.layers.float_vector.new('WeatherPlane')
    for f,n in zip(bm.faces,refnormals):f[reference]=Vector(n)
    bm.verts.ensure_lookup_table()
    for vid,width in d['chips']:
        bm.verts.ensure_lookup_table()
        # Original corner coordinates identify corners after previous bevels.
        co=source.vertices[vid].co
        v=min(bm.verts,key=lambda v:(v.co-co).length)
        assert (v.co-co).length<.001,(ob.name,vid)
        result=bmesh.ops.bevel(bm,geom=[v],offset=width,segments=1,affect='VERTICES',clamp_overlap=True)
        for f in result.get('faces',[]):
            f[reference]=f.normal
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    for f in bm.faces:
        if f[reference].length<.1:f[reference]=f.normal
    refs=[tuple(f[reference]) for f in bm.faces]
    bm.to_mesh(me);bm.free();me.update();ob.data=me
    # Neutral shared pigment means UV packing does not draw face boundaries.
    uv=me.uv_layers.new(name='WeatherPigment')
    lo=Vector([min(v.co[a] for v in me.vertices) for a in range(3)])
    hi=Vector([max(v.co[a] for v in me.vertices) for a in range(3)])
    for loop in me.loops:
        co=me.vertices[loop.vertex_index].co
        uv.data[loop.index].uv=((co.x-lo.x)/(hi.x-lo.x)*.18+.035,(co.z-lo.z)/(hi.z-lo.z)*.18+.035)
    # Reference normals keep the broad faces intact. Shallow scars receive
    # only a limited change in shading direction; their actual geometry remains.
    average=[Vector((0,0,0)) for v in me.vertices]
    for p in me.polygons:
        ref=Vector(refs[p.index]).normalized()
        for vi in p.vertices:average[vi]+=ref
    average=[n.normalized() for n in average]
    normals=[None]*len(me.loops)
    for p in me.polygons:
        ref=Vector(refs[p.index]).normalized()
        n=ref.lerp(p.normal,.38).normalized()
        p.use_smooth=True
        for li in p.loop_indices:normals[li]=tuple(n.lerp(average[me.loops[li].vertex_index],.12).normalized())
    me.normals_split_custom_set(normals);me.update()
    ob['source_role']='Existing angular rock with sparse shallow weathering; broad planes preserved'
    reports.append({'object':ob.name,'patches':patchreports,'corner_chips':[{'vertex':i,'width_m':w} for i,w in d['chips']],
                    'vertices':len(me.vertices),'faces':len(me.polygons),'bounds':[list(lo),list(hi)]})
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
p=ROOT/'assets/island_blender/asset_manifest.json';m=json.loads(p.read_text(encoding='utf-8'))
m['revision']='Western stone weathering: sparse modeled shallow spalls and chipped corners; clean plane lighting retained'
ref='../../artifacts/rock-weathering-review/README.md'
if ref not in m['source_manifests']:m['source_manifests'].append(ref)
p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
(REVIEW/'blender-authoring.json').write_text(json.dumps({'rocks':reports,'texture':tex.image.filepath},ensure_ascii=False,indent=2),encoding='utf-8')
print('ROCK_WEATHERING_EXPORTED')
