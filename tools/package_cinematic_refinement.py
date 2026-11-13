"""Conservative edge-only temporal filtering and review packaging."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from refine_cinematic_rise import SOURCE, OUT, WEIGHTS, WEIGHT_SHA, composite, boards


def temporal():
    base=OUT/'transparent_png'
    dest=OUT/'transparent_stable';dest.mkdir(exist_ok=True)
    records=[]
    cached={}
    def frame(i):
        if i not in cached:
            a=np.array(Image.open(base/f'frame_{i:03}.png'))
            p=OUT/'eye_repaired_rgb'/f'frame_{i:03}.png'
            rgb=np.array(Image.open(p if p.exists() else OUT/'upscaled_rgb'/f'frame_{i:03}.png').resize((768,448),Image.Resampling.LANCZOS))
            cached[i]=(a,cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY))
        return cached[i]
    gy,gx=np.mgrid[:448,:768].astype(np.float32)
    yy,xx=np.mgrid[:896,:1536].astype(np.float32)
    for i in range(175):
        rgba,gray=frame(i)
        alpha=rgba[...,3].astype(np.float32)/255
        # Limit changes to a two-pixel band; foreground colors and interior alpha stay.
        core=(alpha>.5).astype(np.uint8)
        k=np.ones((5,5),np.uint8)
        edge=cv2.dilate(core,k)-cv2.erode(core,k)
        accum=np.zeros_like(alpha);weights=np.zeros_like(alpha)
        for j in [i-1,i+1]:
            if not 0<=j<175:continue
            neighbor,ngray=frame(j)
            flow=cv2.calcOpticalFlowFarneback(gray,ngray,None,.5,4,25,4,7,1.5,0)
            reverse=cv2.calcOpticalFlowFarneback(ngray,gray,None,.5,4,25,4,7,1.5,0)
            mx,my=gx+flow[...,0],gy+flow[...,1]
            reverse_w=cv2.remap(reverse,mx,my,cv2.INTER_LINEAR)
            agreement=np.exp(-np.sum((flow+reverse_w)**2,2)/.7**2)
            photo=np.abs(gray.astype(np.float32)-cv2.remap(ngray,mx,my,cv2.INTER_LINEAR).astype(np.float32))
            confidence=agreement*np.exp(-photo**2/12**2)
            flow2=cv2.resize(flow,(1536,896),interpolation=cv2.INTER_LINEAR)*2
            warped=cv2.remap(neighbor[...,3].astype(np.float32)/255,xx+flow2[...,0],yy+flow2[...,1],cv2.INTER_LINEAR)
            # Large disagreement is a moving/occluded detail, not key noise.
            weight=.25*cv2.resize(confidence,(1536,896))*np.exp(-((warped-alpha)/.2)**2)*edge
            accum+=weight*warped;weights+=weight
        new=(alpha+accum)/(1+weights)
        # Do not resurrect a pixel outside this frame's matte or alter opaque eye whites.
        new[(alpha==0)|(alpha==1)]=alpha[(alpha==0)|(alpha==1)]
        result=rgba.copy();result[...,3]=np.rint(new*255).astype(np.uint8)
        Image.fromarray(result).save(dest/f'frame_{i:03}.png',compress_level=3)
        records.append({'frame':i,'changed_alpha_pixels':int(np.count_nonzero(result[...,3]!=rgba[...,3])),
                        'max_alpha_delta':int(np.abs(result[...,3].astype(np.int16)-rgba[...,3]).max())})
        cached.pop(i-1,None)
        if i%20==0:print(f'temporal {i:03}',flush=True)
    (OUT/'temporal-check.json').write_text(json.dumps(records,indent=2),encoding='utf8')


def package():
    count=175
    records=[]
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
    contacts=OUT/'contact';contacts.mkdir(exist_ok=True)
    for page,start in enumerate(range(0,count,25)):
        board=Image.new('RGB',(1600,5*212),'#253039');d=ImageDraw.Draw(board)
        for j,i in enumerate(range(start,min(count,start+25))):
            path=OUT/'transparent_stable'/f'frame_{i:03}.png'
            a=Image.open(path).convert('RGBA');assert a.size==(1536,896)
            raw=np.array(a)
            for folder,color in [('dark_png','#28353e'),('light_png','#e5e3da')]:
                im=composite(a,color);im.save(OUT/folder/f'frame_{i:03}.png')
            thumb=composite(a,'#e5e3da').resize((320,187),Image.Resampling.LANCZOS)
            board.paste(thumb,((j%5)*320,(j//5)*212+25));d.text(((j%5)*320+6,(j//5)*212+2),f'{i:03} / {i/24:.2f}s',font=font,fill='white')
            original=SOURCE/'raw_png'/f'frame_{i:03}.png'
            records.append({'frame':i,'source_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
                            'rgba_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bbox':a.getbbox(),
                            'partial_alpha_pixels':int(np.count_nonzero((raw[...,3]>0)&(raw[...,3]<255)))})
        board.save(contacts/f'light-{page:02}.png')
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    for folder,name in [('dark_png','cinematic-rise-refined.mp4'),('light_png','light-background.mp4')]:
        subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-framerate','24','-i',str(OUT/folder/'frame_%03d.png'),
                        '-frames:v','175','-c:v','libx264','-crf','14','-preset','slow','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/name)],check=True)
    subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-framerate','24','-i',str(OUT/'transparent_stable/frame_%03d.png'),
                    '-frames:v','175','-plays','0','-f','apng',str(OUT/'cinematic-rise-refined.apng')],check=True)
    cap=cv2.VideoCapture(str(OUT/'cinematic-rise-refined.mp4'))
    assert int(cap.get(cv2.CAP_PROP_FRAME_COUNT))==175 and cap.get(cv2.CAP_PROP_FPS)==24
    cap.release()
    with Image.open(OUT/'cinematic-rise-refined.apng') as animated:
        assert animated.n_frames==175
        for i in range(175):
            animated.seek(i)
            assert animated.convert('RGBA').tobytes()==Image.open(OUT/'transparent_stable'/f'frame_{i:03}.png').convert('RGBA').tobytes()
    previous=json.loads((SOURCE/'verification.json').read_text(encoding='utf8'))
    for old,new in zip(previous['records'],records):assert old['source_sha256']==new['source_sha256']
    report={'frames':175,'fps':24,'duration_seconds':175/24,'source_size':[768,448],'delivery_size':[1536,896],
            'source_unchanged_hashes_verified':True,'motion_regenerated':False,'frames_removed_or_interpolated':False,
            'uniform_upscale_only':True,'per_frame_alignment_or_zoom':False,'upscaler':'RealESRGAN Compact animevideov3 4x, deliver at 2x',
            'weights_sha256':WEIGHT_SHA,'weights_url':'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth',
            'eyes_repair_frames':[165,174],'eye_repair_source':'same-shot frame174 near eye, perspective-compressed, local optical-flow tracking',
            'alpha':'local foreground/background color projection at 4x, blue decontamination, premultiplied downsample, confidence-gated edge-only temporal stabilization',
            'apng_roundtrip_exact':True,'game_integration':False,'visual_acceptance':'pending',
            'limits':['Superresolution estimates missing detail; it does not recover true close-up detail.',
                      'Source hair/clothing shapes still vary across frames; alpha filtering cannot eliminate that motion.',
                      'Far eye remains narrower due perspective; repair does not make eyes symmetric.'],
            'records':records}
    (OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    boards()
    print(json.dumps({k:v for k,v in report.items() if k!='records'},ensure_ascii=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['temporal','package'])
    args=p.parse_args()
    if args.stage=='temporal':temporal()
    else:package()
