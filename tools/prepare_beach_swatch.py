"""Prepare a fixed sand albedo from the supplied isolated painting, without foam."""
from pathlib import Path
import numpy as np,cv2,json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'assets/layered_island/beach_swatch'
source=R/'assets/layered_island/textures/land.png'
rgba=np.array(Image.open(source).convert('RGBA'));rgb=rgba[:,:,:3]
N=1024;H=640
u=np.linspace(0,1,N,dtype=np.float32);v=np.linspace(0,1,H,dtype=np.float32)
source_x=np.array([225,300,400,500,600,700,820,932],dtype=np.float32)
back=np.array([1285,1263,1234,1218,1220,1240,1259,1290],dtype=np.float32)
front=np.array([1305,1337,1364,1345,1363,1356,1335,1303],dtype=np.float32)
xx=np.interp(u,np.linspace(0,1,8),source_x).astype(np.float32)
yb=np.interp(u,np.linspace(0,1,8),back);yf=np.interp(u,np.linspace(0,1,8),front)
# Each part of the beach uses one stable corresponding strip of sand; no tiled
# crop and no painted waterline baked into the ground texture.
sx=np.broadcast_to(xx,(H,N)).copy()
sy=(yb[None,:]+(yf-yb)[None,:]*(.03+.92*v[:,None]**.93)).astype(np.float32)
sample=cv2.remap(rgb,sx,sy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
alpha=cv2.remap(rgba[:,:,3],sx,sy,cv2.INTER_NEAREST)
a=sample.astype(float);rr,gg,bb=a[:,:,0],a[:,:,1],a[:,:,2]
vegetation=(gg>rr*.94)&(bb<gg*.90)
pebbles=(rr<145)&(bb>gg*.79)&(abs(rr-gg)<13)
mask=np.uint8((vegetation|pebbles|(alpha<200))*255)
mask=cv2.dilate(mask,np.ones((5,5),np.uint8))
for center,axes in [((249,269),(15,28)),((303,196),(32,61)),((346,130),(30,51)),((459,75),(15,31))]:
    cv2.ellipse(mask,center,axes,0,0,360,255,-1)
clean=cv2.inpaint(sample,mask,7,cv2.INPAINT_TELEA)
# Keep the diagonal brush character, but compress the strongest fixed painted
# highlights so actual bamboo shadows remain legible when they move.
cl=clean.astype(float);luma=np.mean(cl,2)
compress=np.maximum(0,luma-205)*.48
cl=np.clip(cl-compress[:,:,None],0,255).astype(np.uint8)
Image.fromarray(cl).save(O/'sand_albedo.png')
Image.fromarray(mask).save(O/'removed-painted-objects-mask.png')
(O/'SOURCE.json').write_text(json.dumps({'source':str(source.relative_to(R)),'original_reference':'C:/Users/51440/Downloads/武侠孤岛场景-山洞扩大版.png','method':'Unique strip remap of supplied painted sand; painted vegetation, pebble silhouettes and alpha edge removed; highlights compressed; no foam baked into albedo.','source_x':source_x.tolist(),'source_back_y':back.tolist(),'source_front_y':front.tolist(),'sha256':hashlib.sha256((O/'sand_albedo.png').read_bytes()).hexdigest()},ensure_ascii=False,indent=2),encoding='utf-8')
print('Prepared unique sand albedo',N,H,'masked fraction',float(np.mean(mask>0)))
