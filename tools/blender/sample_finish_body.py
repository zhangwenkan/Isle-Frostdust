for ob in list(COL[SAMPLE].objects):
 if ob.name.startswith(('Sample_Foreground_Fern','Sample_Finish_')):bpy.data.objects.remove(ob,do_unlink=True)
for img in bpy.data.images:
 if img.filepath and '/pixel/' in img.filepath.replace('\\','/'):
  img.reload();img.pack()

# The canopy has depth: tilted upper sprays catch direct noon light and cast broad shadows.
for ob in list(COL[SAMPLE].objects):
 if '_Leaves_' not in ob.name or 'Pine' not in ob.name:continue
 idx=int(ob.name.split('_')[-1])
 if idx not in [0,2,3,6]:continue
 dup=ob.copy();dup.data=ob.data.copy();dup.name='Sample_Finish_'+ob.name.removeprefix('Sample_')+'_Crown_Top'
 COL[SAMPLE].objects.link(dup)
 center=sum((v.co for v in dup.data.vertices),Vector())/len(dup.data.vertices)
 for v in dup.data.vertices:
  q=v.co-center
  v.co.x=center.x+q.x*.9
  v.co.y=center.y+q.y*.75-q.z*.95-.12
  v.co.z=center.z+q.z*.45+.12

# Foreground sprays sit on nearby unseen ledges, framing the walking plane.
for i,(x,z,y,w,roll) in enumerate([(-11.6,7.5,2.1,4.8,-.17),(-13.1,7.0,2.1,3.8,.05),(1.5,7.3,1.3,4.2,.12)]):
 card('Finish_Foreground_Leaves_%02d'%i,(x,y,z),w,w*.67,'PX_Fern',roll=roll)

# Larger joined roots and small fissure stones tie the main pine to its slope.
roots=Batch()
for pts in [[(-10.35,3.95,-2.65),(-10.0,3.69,-2.2),(-9.58,3.51,-1.85)],
 [(-10.35,3.94,-2.65),(-11.05,3.73,-2.35),(-11.75,3.69,-2.2)]]:
 pts=[Vector(p) for p in pts]
 for p in pts:p.y=height(p.x,p.z)+.09
 pts[0].y+=.28;tube(roots,pts,[.18,.10,.015],9)
roots.finish('Sample_Finish_Exposed_Pine_Roots',['bark'],SAMPLE,True)
for i,(x,z) in enumerate([(-11.28,-1.85),(-9.85,-1.82),(-6.5,-1.17),(-4.0,-.8),(2.8,.95)]):
 broken_rock('Finish_Root_Stone_%02d'%i,(x,height(x,z)+.02,z),(.24,.17,.20),i%3,.1,False)

# Configure a matching Blender review camera for asset editing.
cam=scene.camera
cam.data.sensor_fit='VERTICAL'
cam.data.sensor_height=24
cam.data.lens=24/(2*math.tan(math.radians(17)))
focus=Vector((-5.6,height(-6.8,path_z(-6.8))+1.04,path_z(-6.8)))
cam.location=G(focus+Vector((0,5.8,18.5)))
cam.rotation_euler=(G(focus)-cam.location).to_track_quat('-Z','Y').to_euler()
save()
print('Finished canopy volume, foreground framing, root contacts and screen-scale pixel sampling.')
