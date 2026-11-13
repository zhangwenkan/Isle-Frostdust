"""A small tracked eye repair made from the same frame's visible near eye."""
from pathlib import Path
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/cinematic-rest-rise-review/result-toon3d-refined'


def donor():
    src = np.array(Image.open(OUT / 'upscaled_rgb/frame_174.png')).astype(np.float32)
    h, w = src.shape[:2]
    # Copy the existing eye opening and pupil; compress it for the far side perspective.
    near_shape = np.array([(329.6,74.1),(331.8,72.8),(335,71.7),(338.5,71.6),
                           (341.4,72.1),(343.4,73.1),(344.1,74.7),(343.4,76.3),
                           (341.2,77.7),(337.5,78.1),(334,77.9),(331.4,76.6)],np.float32)*4
    mask = np.zeros((h,w),np.float32)
    cv2.fillPoly(mask,[np.rint(near_shape).astype(np.int32)],1)
    mask = cv2.GaussianBlur(mask,(3,3),.65)
    transform = np.array([[.44,0,(355.5-.44*329.6)*4],[-.055,.77,(73.1-.77*71.6+.055*329.6)*4]],np.float32)
    eye = cv2.warpAffine(src,transform,(w,h),flags=cv2.INTER_CUBIC)
    a = cv2.warpAffine(mask,transform,(w,h),flags=cv2.INTER_LINEAR)
    eye *= .91
    fixed = np.rint(src*(1-a[...,None])+np.clip(eye,0,255)*a[...,None]).astype(np.uint8)
    Image.fromarray(fixed).save(OUT/'tail-eye-donor.png')
    return src.astype(np.uint8),fixed,a


def build():
    source,fixed,alpha=donor()
    # Work in a fixed face region. Motion estimates track the face, not a global resize.
    x0,y0,x1,y1=275*4,25*4,390*4,150*4
    ref_gray=cv2.cvtColor(source[y0:y1,x0:x1],cv2.COLOR_RGB2GRAY)
    donor_color=fixed[y0:y1,x0:x1]
    donor_alpha=alpha[y0:y1,x0:x1]
    h,w=ref_gray.shape
    grid_x,grid_y=np.meshgrid(np.arange(w,dtype=np.float32),np.arange(h,dtype=np.float32))
    dest=OUT/'eye_repaired_rgb';dest.mkdir(exist_ok=True)
    masks=OUT/'eye_masks';masks.mkdir(exist_ok=True)
    records=[]
    # The earlier head turn already has open eyes and is outside this local correction.
    for i in [163,164]:
        for folder in [dest,masks]:
            old=folder/f'frame_{i:03}.png'
            if old.exists():old.unlink()
    for i in range(165,175):
        path=OUT/'upscaled_rgb'/f'frame_{i:03}.png'
        if not path.exists():continue
        rgb=np.array(Image.open(path))
        current_gray=cv2.cvtColor(rgb[y0:y1,x0:x1],cv2.COLOR_RGB2GRAY)
        flow=cv2.calcOpticalFlowFarneback(current_gray,ref_gray,None,.5,5,35,5,7,1.5,0)
        mx,my=grid_x+flow[...,0],grid_y+flow[...,1]
        warped_alpha=cv2.remap(donor_alpha,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
        warped_color=cv2.remap(donor_color,mx,my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT101)
        strength=min(1,(i-164)/3)
        warped_alpha*=strength
        before=rgb[y0:y1,x0:x1].copy()
        rgb[y0:y1,x0:x1]=np.rint(before*(1-warped_alpha[...,None])+warped_color*warped_alpha[...,None]).astype(np.uint8)
        Image.fromarray(rgb).save(dest/f'frame_{i:03}.png')
        fullmask=np.zeros(rgb.shape[:2],np.uint8);fullmask[y0:y1,x0:x1]=np.rint(warped_alpha*255).astype(np.uint8)
        Image.fromarray(fullmask).save(masks/f'frame_{i:03}.png')
        yy,xx=np.where(fullmask>0)
        records.append({'frame':i,'strength':strength,'changed_pixels':int(np.count_nonzero(np.any(rgb!=np.array(Image.open(path)),2))),
                        'region_4x':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]})
    (OUT/'eye-repair.json').write_text(json.dumps(records,indent=2),encoding='utf8')


if __name__=='__main__':
    build()
