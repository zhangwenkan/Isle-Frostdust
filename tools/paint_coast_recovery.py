"""Local registered cape painting; raster artwork only, no geometry."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
R=Path(__file__).resolve().parents[1];O=R/'assets/layered_island/coast_recovery';N=2048
src=np.asarray(Image.open(R/'assets/layered_island/strict_coast/floor.png').convert('RGB'),dtype=float)
y,x=np.mgrid[0:N,0:N];wx=-72.5+x/(N-1)*23;wy=35-y/(N-1)*31
sx=np.where(wx<-64,-64+(wx+64)/2.15,wx);ix=np.clip(((sx+68)/18*(src.shape[1]-1)).astype(int),0,src.shape[1]-1);iy=np.clip(((35-wy)/31*(src.shape[0]-1)).astype(int),0,src.shape[0]-1);old=src[iy,ix]
def smooth(a,b,v):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
# Quiet grass around a single used clearing and the real route. The old hard
# polygon fills were only a trial painting and are replaced inside this cape.
camp=np.sqrt(((wx+65.8)/3.25)**2+((wy-13.05)/2.05)**2)
campmask=1-smooth(.80,1.1,camp+.07*np.sin(wx*2.2+wy*1.4))
def line(a,b,w):
 dx=b[0]-a[0];dy=b[1]-a[1];t=np.clip(((wx-a[0])*dx+(wy-a[1])*dy)/(dx*dx+dy*dy),0,1)
 dist=np.sqrt((wx-a[0]-t*dx)**2+(wy-a[1]-t*dy)**2)
 return 1-smooth(w*.8,w*1.3,dist+.06*np.sin(wx*3+wy*2))
path=np.maximum(line((-65.8,13.05),(-60.5,13.4),.82),line((-63.5,12.8),(-63.3,8.6),.85));wear=np.maximum(path,campmask)
grass=np.zeros((N,N,3))+[81,95,52];earth=np.zeros((N,N,3))+[140,138,110]
wide=np.sin(wx*.7+wy*.3)*2.0+np.sin(wy*1.15-wx*.22)*1.4
grass+=wide[...,None]*[.8,1,.55];earth+=wide[...,None]*.8
art=grass*(1-wear[...,None])+earth*wear[...,None]
weight=(1-smooth(-60.0,-57.0,wx))*(1-smooth(16.3,18.1,wy));result=old*(1-weight[...,None])+art*weight[...,None]
Image.fromarray(np.uint8(np.clip(result,0,255))).save(O/'cape_floor.png')
# Large quiet mineral washes on the continuous core. Sparse structural strokes,
# no particle noise, grit blanket, or edge outlines.
w,h=2048,512;im=Image.new('RGB',(w,h),(137,142,124));d=ImageDraw.Draw(im)
for pts,col in [([(0,0),(290,0),(370,512),(0,512)],(130,135,117)),([(290,0),(390,0),(515,512),(370,512)],(145,148,130)),([(860,0),(1040,0),(930,512),(750,512)],(128,134,118)),([(1310,0),(1480,0),(1550,512),(1380,512)],(144,147,130)),([(1760,0),(1840,0),(1740,512),(1640,512)],(131,137,120))]:d.polygon(pts,fill=col)
im=im.filter(ImageFilter.GaussianBlur(8));d=ImageDraw.Draw(im)
for points in [[(310,80),(337,172),(353,209)],[(881,286),(857,366),(850,402)],[(1430,60),(1445,132)],[(1790,215),(1769,290)]]:d.line(points,fill=(109,117,102),width=2)
im.save(O/'core_wash.png')
