"""Paint registered facet washes and selective real-edge strokes inside Blender MCP."""
exec(compile(open('D:/自己做着玩的/孤屿霜尘/tools/blender/left_finish_common.py',encoding='utf8').read(),'left_finish_common.py','exec'))
import numpy as np
R=ROOT/'artifacts/rock-stair-composition-review';T=OUT/'rock_stair_composition';T.mkdir(exist_ok=True)
LAYOUT=json.loads((R/'trimmed-layout.json').read_text(encoding='utf8'));state=LAYOUT['reference_cape']['rock_stair_composition']
assert not state.get('face_paint_done')
W,H=960,640;CELL=320;PAD=14
def axes(p):
 a=max(range(3),key=lambda i:abs(p.normal[i]));sgn=0 if p.normal[a]>0 else 1
 return a*2+sgn,[(1,2),(0,2),(0,1)][a]
def segment(canvas,a,b,width,color,opacity=.65,interval=(0,1)):
 a=np.asarray(a);b=np.asarray(b);delta=b-a;den=max(float(delta@delta),.001)
 lo=np.maximum(0,np.floor(np.minimum(a,b)-width*3).astype(int));hi=np.minimum([W-1,H-1],np.ceil(np.maximum(a,b)+width*3).astype(int))
 if np.any(hi<=lo):return
 yy,xx=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1];t=((xx-a[0])*delta[0]+(yy-a[1])*delta[1])/den
 dist=np.sqrt((xx-a[0]-np.clip(t,0,1)*delta[0])**2+(yy-a[1]-np.clip(t,0,1)*delta[1])**2)
 edge=np.clip(1-dist/width,0,1)*np.clip((t-interval[0])*.08*math.sqrt(den),0,1)*np.clip((interval[1]-t)*.08*math.sqrt(den),0,1)*opacity
 region=canvas[lo[1]:hi[1]+1,lo[0]:hi[0]+1,:3];region[:]=region*(1-edge[:,:,None])+np.array(color)*edge[:,:,None]
records=[]
names=state['rocks']+['Cape_Terminus_Bedrock','WALK_Cape_Stairs','Cape_Stair_Support']
for index,name in enumerate(names):
 o=SCENE.objects[name];me=o.data
 lo=np.array([min(v.co[i] for v in me.vertices) for i in range(3)]);hi=np.array([max(v.co[i] for v in me.vertices) for i in range(3)]);span=np.maximum(hi-lo,.001)
 stone='Rock_' in name;is_step=name=='WALK_Cape_Stairs'
 base=np.array([.66,.63,.53]) if stone else np.array([.62,.60,.51])
 base+=np.array([.012,.007,-.003])*((index%3)-1)
 pixels=np.ones((H,W,4),dtype=np.float32);pixels[:,:,:3]=base
 uv=me.uv_layers.get('UVMap') or me.uv_layers.new(name='UVMap')
 def project(v,group,ax):
  x=group%3*CELL+PAD+(v.co[ax[0]]-lo[ax[0]])/span[ax[0]]*(CELL-2*PAD)
  y=group//3*CELL+PAD+(v.co[ax[1]]-lo[ax[1]])/span[ax[1]]*(CELL-2*PAD)
  return np.array([x,y])
 for p in me.polygons:
  group,ax=axes(p);points=np.array([project(me.vertices[vi],group,ax) for vi in p.vertices])
  for li,xy in zip(p.loop_indices,points):uv.data[li].uv=(xy[0]/W,xy[1]/H)
  x0,y0=np.maximum(0,np.floor(points.min(axis=0)).astype(int));x1,y1=np.minimum([W-1,H-1],np.ceil(points.max(axis=0)).astype(int))
  if x1<=x0 or y1<=y0:continue
  yy,xx=np.mgrid[y0:y1+1,x0:x1+1];mask=np.zeros(xx.shape,dtype=bool)
  for a,b in zip(points,np.roll(points,-1,axis=0)):
   cross=((a[1]>yy)!=(b[1]>yy))&(xx<(b[0]-a[0])*(yy-a[1])/(b[1]-a[1]+1e-8)+a[0]);mask^=cross
  # Low-frequency washes follow a face's real projection and broad height.
  wash=.012*np.sin((xx%CELL)/CELL*5.4+(yy%CELL)/CELL*2.7+index*.39)+.006*np.sin((yy%CELL)/CELL*8.1)
  tone=.028*p.normal.z-.014*max(0,-p.normal.y)+.009*math.sin(p.center.z*1.15+index*.31)
  color=np.clip(base[None,None,:]+wash[:,:,None]+tone,0,1)
  region=pixels[y0:y1+1,x0:x1+1,:3];region[mask]=color[mask]
 # Only selected structural edges receive broken strokes; there is no
 # stamped crack tile, full contour ring or per-triangle texture restart.
 bm=bmesh.new();bm.from_mesh(me)
 edges=[e for e in bm.edges if e.is_manifold and .28<e.calc_face_angle()<1.65 and e.calc_length()>.62]
 edges.sort(key=lambda e:e.calc_length()*e.calc_face_angle(),reverse=True)
 budget=8 if stone else (0 if is_step or name=='Cape_Stair_Support' else 4)
 strokes=0
 for e in edges[:budget]:
  for f in e.link_faces:
   if f.normal.z<-.3:continue
   class Face:pass
   fp=Face();fp.normal=f.normal;group,ax=axes(fp)
   a,b=[project(v,group,ax) for v in e.verts]
   dark=base*np.array([.66,.66,.63])
   for interval in [(.12,.42),(.54,.79)]:segment(pixels,a,b,1.75,dark,.58,interval)
   strokes+=1
 bm.free()
 # Subtle, localized moss on only the rooted shelves, with a feathered
 # diagonal footprint; nearby grass remains the dominant living cover.
 if 'Root_' in name:
  group=4;x0,y0=group%3*CELL,group//3*CELL;yy,xx=np.mgrid[0:CELL,0:CELL]
  strength=np.clip(1-((xx-CELL*.72)**2/(CELL*.34)**2+(yy-CELL*.74)**2/(CELL*.20)**2),0,1)*.35
  region=pixels[y0:y0+CELL,x0:x0+CELL,:3];region[:]=region*(1-strength[:,:,None])+np.array([.35,.40,.22])*strength[:,:,None]
 image=bpy.data.images.new('CompositionPaint_'+name,width=W,height=H,alpha=True)
 image.colorspace_settings.name='sRGB';image.pixels.foreach_set(pixels.ravel());image.filepath_raw=str(T/(name+'.png'));image.file_format='PNG';image.save();image.pack()
 m=bpy.data.materials.new('StrictCoast_Composition_'+name);m.use_nodes=True;m.diffuse_color=(*base,1)
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.90;bs.inputs['Specular IOR Level'].default_value=.10
 tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 me.materials.clear();me.materials.append(m)
 for p in me.polygons:p.material_index=0;p.use_smooth=False
 if len(me.uv_layers)<2:me.uv_layers.new(name='Wind')
 records.append({'object':name,'texture':str(image.filepath_raw),'strokes_on_face_sides':strokes,'projection':'six continuous physical-axis islands registered to actual facets'})
state['face_paint_done']=True;state['stage']='colored effect review, pending user evaluation';state['paint_records']=records
(T/'paint-design.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
(R/'authoring-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf8')
export('rock-stair-composition-colored-review')
print(json.dumps({'painted_objects':len(records),'exported':True}))
