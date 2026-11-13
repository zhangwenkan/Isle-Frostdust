# Remove the old micro-geometry in the sample. Retain the eastern island assets.
for col in ['06_Ferns_Grass','05_Bamboo']:
 for ob in list(COL[col].objects):
  if ob.type!='MESH':continue
  coords=[ob.matrix_world@Vector(v) for v in ob.bound_box]
  cx=sum(p.x for p in coords)/8
  if cx<6 and (col=='06_Ferns_Grass' or 'Leaves' in ob.name or 'Fine_Twigs' in ob.name):
   bpy.data.objects.remove(ob,do_unlink=True)
for ob in list(COL[SAMPLE].objects):
 if ob.name.startswith(('Sample_Coastal_Joint','Sample_Tidal_Buttress','Sample_Polish_')):bpy.data.objects.remove(ob,do_unlink=True)
for img in bpy.data.images:
 if img.filepath and '/pixel/' in img.filepath.replace('\\','/'):
  img.reload();img.pack()
pixelmat('PX_Bamboo','bamboo_spray.png',True)
pixelmat('PX_Ivy','hanging_ivy.png',True)

# Front edge traced from the existing terrain, not a row of identical columns.
def edge_z(x):
 front=sorted([(x,z) for x,z in OUTLINE if z>.7])
 for (ax,az),(bx,bz) in zip(front,front[1:]):
  if ax<=x<=bx:return az+(bz-az)*(x-ax)/(bx-ax)
 return 1.2

# Different heights, setbacks and inclinations make a broken granite headland.
# The broad faces use asymmetric top bevels; no uniform ring of moss atop each block.
configs=[
 (-17.3,1.20,1.45,.66,-.28,0),(-15.5,1.04,2.45,.71,.18,2),
 (-13.5,1.36,1.72,.73,-.17,1),(-11.35,1.07,2.65,.69,.29,0),
 (-9.48,1.12,1.62,.76,-.25,2),(-7.38,1.46,2.1,.82,.15,1),
 (-4.98,1.11,1.58,.71,-.2,0),(-3.1,1.04,2.0,.69,.27,2),
 (-1.15,1.12,1.32,.72,-.25,1),(.8,1.05,1.95,.63,.12,0),(2.64,.84,1.42,.62,.3,2)]
for i,(x,sx,sy,sz,tilt,p) in enumerate(configs):
 z=edge_z(x)-.18;top=height(x,z)-.14-(i%3)*.12
 ob=broken_rock('Polish_Rock_Face_%02d'%i,(x,top-sy*.83,z),(sx,sy,sz),p,tilt,False)
 # Cut one upper corner and skew one exposed shoulder in edit-space.
 for v in ob.data.vertices:
  xx=v.co.x-x
  if xx*sx>0 and v.co.z>top-.6:
   v.co.z-=max(0,xx)*(.16+.07*(i%3))
 for pface in ob.data.polygons:pface.use_smooth=True
 # Broken overlapping footstone occupies selected crevices.
 if i in [1,2,4,6,9]:
  broken_rock('Polish_Foot_Slab_%02d'%i,(x+.7,top-sy*1.35,z+.44),(sx*.70,.58,sz*.63),(p+1)%3,-tilt,False)

# Scattered turf tongues hang over some fractures; widths and lengths vary.
for i,(x,wide,drop) in enumerate([(-16.8,.82,.6),(-14.5,1.1,.9),(-11.3,.7,.7),(-9.7,.9,1.35),(-7.4,.78,.8),(-5.4,.95,1.2),(-2.4,.73,.8),(.2,.8,.65),(2.5,.72,.8)]):
 z=edge_z(x)+.12;y=height(x,z)-drop*.5
 card('Polish_Ivy_Leaves_%02d'%i,(x,y,z),wide,drop,'PX_Ivy',roll=(i%3-1)*.08)

# Moss grows across angled upper seams instead of perfect level caps.
for i,(x,z,sx,sy,sz,p) in enumerate([(-13.2,2.8,.6,.16,.48,1),(-8.7,3.5,.78,.16,.40,2),(-4.6,3.3,.66,.13,.45,0),(-.1,2.9,.52,.15,.38,2)]):
 ob=broken_rock('Polish_Turf_Shelf_%02d'%i,(x,height(x,z)-.12,z),(sx,sy,sz),p,0,False)
 ob.data.materials.clear();ob.data.materials.append(MAT['moss'])

# Bamboo canopy with legible lanceolate leaf groups, keeping original jointed culms.
for i,(x,y,z,w,roll) in enumerate([
 (-4.95,5.15,-2.2,1.45,.12),(-4.3,5.8,-2.6,1.7,-.1),(-3.8,6.45,-2.8,1.65,.12),
 (-5.05,6.7,-2.65,1.7,-.16),(-4.65,7.25,-2.7,1.4,.05),(-3.45,5.8,-2.4,1.6,.14),
 (-3.8,7.0,-2.9,1.6,-.1),(-5.45,5.9,-2.4,1.3,.08)]):
 card('Polish_Bamboo_Leaves_%02d'%i,(x,y,z),w,w*.67,'PX_Bamboo',roll=roll)

# Grounded clusters leave intervals of exposed turf and trail.
for i,(x,z,s) in enumerate([(-14.2,1.48,.8),(-12.1,-1.2,1.1),(-10.6,1.65,.8),(-9.2,2.55,.6),(-7.1,-.9,.75),(-5.6,1.6,.7),(-3.5,2.5,.9),(-2.1,-1.0,.65),(.8,1.3,.65)]):
 card('Polish_Fern_Leaves_%02d'%i,(x,height(x,z)+.32*s,z),1.45*s,.96*s,'PX_Fern')
save()
print('Sample polish: irregular jointed bank, no old west micro-grass, bamboo sprays, hanging ivy and contact vegetation.')
