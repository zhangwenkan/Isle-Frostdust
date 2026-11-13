"""Blender MCP: replace stretched foreground boulders with broken rock shoulders."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
mat=bpy.data.materials['Coast_Sculpted_Bedrock']
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def color(h):return tuple(linear(int(h[i:i+2],16)/255) for i in (0,2,4))+(1.,)
def mix(a,b,t):return tuple(x*(1-t)+y*t for x,y in zip(a,b))
base=color('98a38e');shade=color('788b7c');top_color=color('afb59e')
records=[]
for index in range(8):
    ob=scene.objects['Depth_Foreground_Crag_%02d'%index]
    key=ob.name+'_Before_Cliff_Forms';original=bpy.data.meshes.get(key)
    if original is None:original=ob.data.copy();original.name=key;original.use_fake_user=True
    bounds=[(min(v.co[k] for v in original.vertices),max(v.co[k] for v in original.vertices)) for k in range(3)]
    cx=(bounds[0][0]+bounds[0][1])/2;cy=(bounds[1][0]+bounds[1][1])/2
    rx=(bounds[0][1]-bounds[0][0])/2;ry=(bounds[1][1]-bounds[1][0])/2
    low=bounds[2][0];top=bounds[2][1]
    # Preserve the original irregular rock topology and matched UVs. Sculpt
    # diagonal shoulders into it instead of introducing a regular radial stack.
    me=original.copy();me.name=ob.name+'_Broken_Bedrock'
    bm=bmesh.new();bm.from_mesh(me)
    bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=1,use_grid_fill=True)
    for v in bm.verts:
        p=v.co;t=max(0,min(1,(p.z-low)/(top-low)))
        u=(p.x-cx)/rx;w=(p.y-cy)/ry
        belt=.35+.08*u-.04*w
        belt2=.65-.06*u+.05*w
        ridge=.12*max(0,1-abs((t-belt)/.09))+.10*max(0,1-abs((t-belt2)/.08))
        fracture=.10*abs(math.sin(u*4.2+w*2.1+t*3+index))**4*math.sin(t*math.pi)
        radial=1+ridge-fracture
        p.x=cx+(p.x-cx)*radial+.18*math.sin(index*.8)*math.sin(t*math.pi)
        p.y=cy+(p.y-cy)*radial+.12*math.sin(index+u)*math.sin(t*math.pi)
        # Set the crown slightly into its coastal footing and avoid a tall egg.
        p.z=low+(p.z-low)*(.96 if index%2 else .98)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    if me.has_custom_normals:
        # The stretched source's stored normals no longer describe the sculpt.
        ob.data=me
        bpy.context.view_layer.objects.active=ob
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
    me.set_sharp_from_angle(angle=math.radians(38));me.update();ob.data=me
    records.append({'name':ob.name,'old_vertices':len(original.vertices),'new_vertices':len(ob.data.vertices)})

# Seat the existing front bamboo on the refined caps, preserving its wind weights.
dg=bpy.context.evaluated_depsgraph_get()
trees=[BVHTree.FromObject(scene.objects['Depth_Foreground_Crag_%02d'%i],dg) for i in range(8)]
for i in range(3):
    ob=scene.objects['Depth_Bamboo_Fore_%02d'%i]
    key=ob.name+'_Before_Cliff_Forms';baseline=bpy.data.meshes.get(key)
    if baseline is None:baseline=ob.data.copy();baseline.name=key;baseline.use_fake_user=True
    ob.data=baseline.copy()
    low=min(v.co.z for v in ob.data.vertices)
    rootverts=[v for v in ob.data.vertices if v.co.z<low+.045]
    root=sum((v.co for v in rootverts),Vector())/len(rootverts)
    hits=[tree.ray_cast(Vector((root.x,root.y,20)),Vector((0,0,-1)))[0] for tree in trees]
    hits=[p for p in hits if p is not None]
    assert hits,'Missing bamboo support'
    dz=max(p.z for p in hits)-low-.025
    for v in ob.data.vertices:v.co.z+=dz
    ob.data.update()
    records.append({'bamboo':ob.name,'root_adjustment':dz})
(ROOT/'artifacts/cliff-form-review/foreground-authoring.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
print('FOREGROUND_CLIFFS_COMPLETE',json.dumps(records))
