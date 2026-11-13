grain=Batch();endgrain=Batch();pegs=Batch();lashings=Batch();ropes=Batch();supports=Batch()
for i in range(39):
    x=4.15+i*10.5/38;y=bridge_y(x)
    half=.125;depth=R.uniform(.89,.99);shift=R.uniform(-.025,.025)
    # Eight vertices per plank, worn edges, skew, and end-grain details.
    vs=[]
    for yy in [-.09,.045]:
        for xx,zz in [(-half,-depth),(half,-depth),(half,depth),(-half,depth)]:
            vs.append((x+xx+R.uniform(-.012,.012),y+yy+zz*.015*math.sin(i),.25+zz+shift))
    ob=mesh(f'Bridge_Plank_{i:02d}',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],['wood','wood_end'],'07_Bridge',[0,0,1,0,1,0])
    bevel(ob,.014,2)
    # Narrow grain grooves align along the actual long axis of each board.
    for j in range(3):
        px=x+(-.07+j*.068)
        pts=[(px+.008*math.sin(k*2+i+j),y+.052,.25-depth+.10+k*(2*depth-.2)/8) for k in range(9)]
        tube(grain,pts,[.006]*9,4)
    for z in [-.48,.98]:
        tube(pegs,[(x,y+.045,z),(x,y+.062,z)],[.023,.020],8)

for side in [-1,1]:
    z=.25+side*.93
    for i in range(8):
        x=4.2+i*10.3/7;y=bridge_y(x)
        tube(supports,[(x,y-.27,z),(x+.03*side,y+.45,z),(x+.07*side,y+1.05,z)],[.065,.061,.052],10)
        # Multiple binding turns around each post and a short hanging tail.
        for band in [.46,.91]:
            pts=[]
            for j in range(41):
                a=j*math.tau/10
                pts.append((x+.074*math.cos(a),y+band+j*.003,z+.074*math.sin(a)))
            tube(lashings,pts,[.013]*len(pts),5)
        tube(lashings,[(x+.07,y+.58,z),(x+.12,y+.4,z+.06),(x+.1,y+.28,z+.08)],[.013]*3,5)
    for h in [.46,.96,-.13]:
        pts=[]
        for j in range(169):
            x=4.2+j*10.3/168
            sag=math.sin(((j/168*7)%1)*math.pi)*.1 if h>0 else 0
            pts.append(Vector((x,bridge_y(x)+h-sag,z)))
        tube(ropes,pts,[.025 if h>0 else .043]*len(pts),8)
        # Real spiral fibres add silhouette detail to the exposed top ropes.
        if h>.8:
            for strand in range(2):
                fibre=[]
                for j in range(337):
                    f=j/2;lo=int(f);t=f-lo;p=pts[min(lo,168)].lerp(pts[min(lo+1,168)],t)
                    a=j*.85+strand*math.pi
                    fibre.append(p+Vector((0,math.cos(a)*.026,math.sin(a)*.026)))
                tube(lashings,fibre,[.006]*len(fibre),4)
for x in [4.4,14.2]:
    for z in [-.55,1.05]:
        tube(supports,[(x,WATER-.3,z),(x,bridge_y(x)+.1,z)],[.14,.11],12)
    tube(supports,[(x,WATER+.3,-.55),(x,bridge_y(x)-.2,1.05)],[.06,.055],8)
    tube(supports,[(x,WATER+.3,1.05),(x,bridge_y(x)-.2,-.55)],[.06,.055],8)
supports.finish('Bridge_Weathered_Posts_Cross_Braces',['wood'],'07_Bridge',True)
ropes.finish('Bridge_Sagging_Rope_Rails',['rope_dark'],'07_Bridge',True)
lashings.finish('Bridge_Hand_Tied_Bindings_and_Twisted_Fibres',['rope'],'07_Bridge',True)
grain.finish('Bridge_Plank_Grain_Grooves',['wood_dark'],'07_Bridge')
pegs.finish('Bridge_Wooden_Pegs',['wood_dark'],'07_Bridge')

# Small seabirds with curved wing profiles, tails and bodies, not crossed beams.
for i in range(4):
    b=Batch();v=[];f=[]
    for side in [-1,1]:
        pts=[(0,0,0),(.18*side,.035,-.06),(.38*side,.08,-.01),(.58*side,.12,.10),(.36*side,.035,.09),(.16*side,-.01,.08)]
        b.add(pts,[(0,1,5),(1,2,4,5),(2,3,4)],0)
    tube(b,[(0,0,-.11),(0,0,.08),(0,.015,.17)],[.035,.06,.015],8,1)
    b.add([(-.04,0,.11),(.04,0,.11),(.09,0,.25),(-.09,0,.25)],[(0,1,2,3)],1)
    ob=b.finish(f'Seabird_{i:02d}',['bird_white','bird_grey'],'12_Birds',True)
    ob.location=G((-9+i*3.7,7+i*.45,-15-i*1.8))

# Authoring camera and lighting, excluded from the Godot export.
cam_data=bpy.data.cameras.new('Gameplay_Midshot');cam=bpy.data.objects.new('Gameplay_Midshot',cam_data);COL['90_Presentation'].objects.link(cam)
focus=Vector((-6.8+1.2,height(-6.8,path_z(-6.8))+1.04,path_z(-6.8)))
cam.location=G(focus+Vector((0,5.8,18.5)))
direction=G(focus)-cam.location;cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
cam_data.type='PERSP';cam_data.lens=34.5;cam_data.sensor_width=36
scene.camera=cam
sun_data=bpy.data.lights.new('Noon_Sun','SUN');sun_data.energy=2.3;sun_data.angle=.035
sun=bpy.data.objects.new('Noon_Sun',sun_data);COL['90_Presentation'].objects.link(sun);sun.rotation_euler=(.2,-.27,-.5)
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA'
        area.spaces.active.shading.type='MATERIAL'
save()
print('Worn individual planks, cross braces, rope fibres, post lashings, seabirds and authoring camera saved.')
