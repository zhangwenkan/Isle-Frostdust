"""Coherent bamboo interiors and grass/stone seams, through Blender MCP."""
import bpy,math,random,json
from pathlib import Path
from mathutils import Vector
root=Path('D:/自己做着玩的/孤屿霜尘');scene=bpy.data.scenes['Fresh_Pixel_Cape'];bpy.context.window.scene=scene
assert scene['revision']=='fresh-cape-reference-polish-4'
bamboo=bpy.data.collections['Fresh_05_Bamboo'];green=bpy.data.collections['Fresh_04_Grass']
def mesh(name,vs,fs,col,mat):
    me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(vs,[],fs);me.update()
    ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(mat)
    uv=me.uv_layers.new(name='UVMap')
    for li,l in enumerate(me.loops):p=me.vertices[l.vertex_index].co;uv.data[li].uv=(p.x*.2,p.z*.2+p.y*.1)
    ob['fresh_sample']=True;ob['authored_from']='coherent interior for new leaf cluster'
    return ob
for j,ob in enumerate(list(bamboo.objects)):
    if 'Bamboo_Shadow_Proxy' in ob.name:ob.display_type='WIRE';ob.hide_render=True
    if 'Bamboo_Leaf_Cluster' not in ob.name:continue
    c=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
    pr=random.Random(j*81);n=22;vs=[tuple(c+Vector((0,-.08,.04)))]
    # Sparse lanceolate leaf tips remain separate; a quiet core groups them.
    for i in range(n):
        a=i*math.tau/n;r=pr.uniform(.79,1.08)
        vs.append(tuple(c+Vector((math.cos(a)*.62*r,.05,math.sin(a)*.23*r))))
    leaf=mesh(ob.name.replace('Leaf_Cluster','Leaf_Core'),vs,[(0,i+1,(i+1)%n+1) for i in range(n)],bamboo,ob.data.materials[0])
    ns=[]
    for p in leaf.data.polygons:
        p.use_smooth=True
        for li in p.loop_indices:
            q=leaf.data.vertices[leaf.data.loops[li].vertex_index].co-c
            ns.append(tuple(Vector((q.x*.5,-.22,q.z*1.2+.85)).normalized()))
    leaf.data.normals_split_custom_set(ns)

# Thin irregular turf tongues lap across a few upper rock edges only.
grass=bpy.data.materials['Fresh_Grass_Main']
for j,(x,y,w,d) in enumerate([(-9.8,-3.03,.75,.26),(-8.4,-3.16,.62,.30),(-6.6,-3.26,.65,.28),(-5.3,-3.13,.70,.24),(-3.6,-2.96,.50,.25)]):
    vs=[(x-w,y+.22,3.135),(x+w,y+.22,3.135),(x+w*.8,y-.03,3.12),(x+w*.30,y-d,3.02),(x-w*.18,y-d*.65,3.065),(x-w*.65,y-.05,3.11)]
    mesh('Grass_Patch_Rock_Lip_%02d'%j,vs,[(0,1,2),(0,2,4),(2,3,4),(0,4,5)],green,grass)
scene['revision']='fresh-cape-reference-polish-5'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/fresh_pixel_cape/fresh_pixel_cape.blend'))
print(json.dumps({'revision':scene['revision']}))
