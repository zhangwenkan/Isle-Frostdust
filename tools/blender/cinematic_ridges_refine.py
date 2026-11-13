import bmesh
import bpy,math
from mathutils import Vector
from pathlib import Path
ROOT=Path('D:/自己做着玩的/孤屿霜尘')
scene=bpy.data.scenes['Island_Refined'];bpy.context.window.scene=scene
ridge_col=bpy.data.collections['23_Layered_Mist_Ridges']
for ob in list(ridge_col.objects):bpy.data.objects.remove(ob,do_unlink=True)
mountain_mat=bpy.data.materials['Depth_Mountain']
def G(p):
    # Godot (x, y, z) -> Blender (x, -z, y).
    return Vector((p[0], -p[2], p[1]))

def mesh_obj(name, verts, faces, mat, col):
    me = bpy.data.meshes.new(name + '_Mesh')
    me.from_pydata([G(v) for v in verts], [], faces)
    me.materials.append(mat)
    me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); col.objects.link(ob)
    return ob

def ridge(name, x, z, top, width, depth, phase, rotation):
    # A connected ridge has unequal crowns, offset saddles and a branching foot.
    # Its outline is sculpted at several scales; no repeating cone or noise texture.
    verts, faces, colors = [], [], []
    nx, nz, base = 92, 30, -8.0
    # Four different ridge structures: dominant spire, long shoulder, twin saddles,
    # and an ascending serrated crest. Depth groups do not share a stamped skyline.
    profiles = [
      [(-.64,.10,.44,.24),(-.27,-.13,1.10,.18),(.16,.08,.72,.23),(.58,.20,.48,.22)],
      [(-.66,-.12,.52,.24),(-.33,.16,.70,.27),(.03,.01,.58,.22),(.39,-.18,1.06,.17),(.66,.18,.46,.18)],
      [(-.59,.18,.86,.18),(-.19,-.16,.52,.25),(.25,.08,1.00,.19),(.61,-.12,.38,.23)],
      [(-.66,.05,.40,.22),(-.31,-.20,.66,.20),(.02,.13,.84,.17),(.33,-.13,1.05,.15),(.61,.10,.65,.20)]
    ]
    crowns = profiles[int(phase * 1.7) % 4]
    for j in range(nz+1):
        v = -1.0 + 2*j/nz
        for i in range(nx+1):
            u = -1.0 + 2*i/nx
            spine = .14*math.sin(u*4.1+phase)
            height = 0.0
            for k,(cx,cz,h,w) in enumerate(crowns):
                cx += .055*math.sin(phase+k*1.7)
                h *= 1+.10*math.sin(phase+k*1.1)
                height += h*math.exp(-(abs((u-cx)/w)**1.8)-((v-cz-spine)/(.44+.04*k))**2)
            height = min(height/1.18,1.08)
            # Broken shoulders and oblique rock ribs give each crown a distinct side.
            height = height ** .80
            seam = abs(math.sin(u*24+v*5.0+phase*2.0))
            height *= 1.0-.075*(seam**7.0)*min(1.0,height*3.0)
            ledge = .020*math.sin(v*23+u*9+phase)*height
            height += ledge
            taper = min(1.0,(1-abs(u))*9,(1-abs(v))*5)
            # Long rock buttresses and broken shelves follow the ridge, not fine noise.
            fold = .10*math.sin(u*27+v*5+phase)+.045*math.cos(u*59-v*7+phase)
            h = base+(top-base)*(height+fold*height*.42)*max(0,taper)
            px=u*width; pz=v*depth
            co=math.cos(rotation);si=math.sin(rotation)
            verts.append((x+px*co-pz*si,h,z+px*si+pz*co))
            tone=.50+.29*math.cos(u*24+v*5+phase*2)+.08*math.sin(v*10+phase)
            colors.append((.105+tone*.065,.16+tone*.07,.145+tone*.06,1))
    for j in range(nz):
        for i in range(nx):
            a=j*(nx+1)+i; b=a+1; c=a+nx+1; d=c+1
            faces.extend([(a,c,b),(b,c,d)])
    ob=mesh_obj(name,verts,faces,mountain_mat,ridge_col)
    ca=ob.data.color_attributes.new(name='DepthColor',type='FLOAT_COLOR',domain='POINT')
    ca.data.foreach_set('color',[v for c in colors for v in c])
    for poly in ob.data.polygons: poly.use_smooth=True
    ob['depth_role']='Connected multi-crown ridge; separate cloud valleys between groups'
    return ob

ridge_specs = [
 ('Mist_Ridge_Front_00',-68,-86,8.8,23,10,.2,.18),
 ('Mist_Ridge_Front_01',-28,-94,10.0,22,11,1.4,-.23),
 ('Mist_Ridge_Front_02',15,-83,6.8,20,10,2.7,.19),
 ('Mist_Ridge_Front_03',58,-96,10.8,25,12,4.1,-.17),
 ('Mist_Ridge_Mid_00',-94,-133,14.0,29,13,1.0,-.12),
 ('Mist_Ridge_Mid_01',-46,-143,16.7,31,14,2.0,.21),
 ('Mist_Ridge_Mid_02',7,-132,14.2,28,14,3.2,-.24),
 ('Mist_Ridge_Mid_03',57,-148,18.8,30,13,4.7,.12),
 ('Mist_Ridge_Mid_04',105,-138,13.0,26,12,5.7,-.2),
 ('Mist_Ridge_Far_00',-135,-207,24.0,43,17,1.5,.12),
 ('Mist_Ridge_Far_01',-76,-218,23.5,46,18,2.6,-.15),
 ('Mist_Ridge_Far_02',18,-206,23.3,42,17,3.8,.19),
 ('Mist_Ridge_Far_03',93,-222,25.0,48,18,5.2,-.11),
 ('Mist_Ridge_Far_04',165,-213,22.0,40,17,6.1,.15),
]
for spec in ridge_specs: ridge(*spec)


exec(compile((ROOT/'tools/blender/fish_export.py').read_text(encoding='utf-8'),'fish_export.py','exec'))
