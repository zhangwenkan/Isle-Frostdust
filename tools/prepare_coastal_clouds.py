"""Paint a transparent equirectangular cloud cover; no scene geometry is generated."""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
w,h=2048,1024
u,v=np.meshgrid(np.arange(w)/w,np.arange(h)/h)
alpha=np.zeros((h,w),dtype=np.float64)
light=np.zeros_like(alpha)
# Long low cloud banks with overlapping soft lobes, kept sparse above the peaks.
for center,cy,width in [(0.04,.480,.045),(.24,.478,.052),(.43,.481,.041),(.63,.479,.054),(.83,.480,.047)]:
    for dx,dy,sx,sy in [(-.45,.002,.55,.004),(-.19,-.001,.40,.006),(0,-.004,.34,.009),(.26,-.002,.48,.007),(.48,.003,.42,.004)]:
        du=((u-center-dx*width+.5)%1)-.5
        q=(du/(width*sx))**2+((v-cy-dy)/sy)**2
        a=np.clip((1.5-q)*1.4,0,1)
        a=a*a*(3-2*a)
        alpha=1-(1-alpha)*(1-a*.65)
        light=np.maximum(light,a*np.clip((cy+.01-v)/.025,0,1))
rgb=np.empty((h,w,3),dtype=np.float64)
for i,(low,high) in enumerate(zip((191,207,208),(246,244,226))):rgb[:,:,i]=low+(high-low)*light
rgba=np.dstack((rgb,np.minimum(alpha,.88)*255)).clip(0,255).astype('uint8')
Image.fromarray(rgba).save(ROOT/'assets/sky/coastal_cloud_cover.png')
print('Saved 2048x1024 transparent cloud panorama')
