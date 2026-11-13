"""Review a complete rise shot without moving, scaling or dropping any frames."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROJECT=Path(__file__).resolve().parents[1]
RUNTIME=Path('D:/AI/minimax-h3-minimal')
BATCH=RUNTIME/'action-batches/rest-rise-cinematic-ref-20261108'
OUT=PROJECT/'artifacts/cinematic-rest-rise-review/result-v1'
FPS=24


def source_keyer():
    source=RUNTIME/'action-batches/rest-rise-right-20261108-v2-vram11/export_preview.py'
    spec=importlib.util.spec_from_file_location('existing_blue_key',source)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.key_blue


def key_toned_blue(rgb):
    # This result uses a desaturated blue cyclorama; saturated-only keying leaves it opaque.
    f=rgb.astype(np.float32)
    blue_green=f[:,:,2]-f[:,:,1]
    blue_red=f[:,:,2]-f[:,:,0]
    strength=np.minimum((blue_green-3)/17,(blue_red-10)/25)
    strong=strength>=1
    near=cv2.dilate(strong.astype(np.uint8),np.ones((5,5),np.uint8)).astype(bool)
    eligible=near&(blue_green>3)&(blue_red>10)
    alpha=np.full(rgb.shape[:2],255,dtype=np.uint8)
    alpha[eligible]=np.rint((1-np.clip(strength[eligible],0,1))*255).astype(np.uint8)
    opaque=alpha==255
    partial=(alpha>0)&(alpha<255)
    corrected=rgb.copy()
    assert opaque.any()
    _,nearest=cv2.distanceTransformWithLabels((~opaque).astype(np.uint8),cv2.DIST_L2,5,labelType=cv2.DIST_LABEL_PIXEL)
    corrected[partial]=rgb[opaque][nearest[partial]-1]
    rgba=np.dstack([corrected,alpha])
    rgba[alpha==0,:3]=0
    white=(rgb.min(2)>200)&((f.max(2)-f.min(2))<15)
    assert np.all(alpha[white]==255)
    assert np.array_equal(rgba[opaque,:3],rgb[opaque])
    return Image.fromarray(rgba),{'partial_alpha_pixels':int(partial.sum()),'neutral_white_preserved':True,
        'opaque_interior_rgb_unchanged':True,'blue_gradient_key':True}


def contact(frames,indices,path,columns=4):
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
    width=320
    height=round(frames[0].height*width/frames[0].width)
    thumb=(width,height)
    board=Image.new('RGB',(width*columns,(height+28)*((len(indices)+columns-1)//columns)),'#20272e')
    draw=ImageDraw.Draw(board)
    for j,i in enumerate(indices):
        x,y=j%columns*width,j//columns*(height+28)
        board.paste(frames[i].resize(thumb,Image.Resampling.NEAREST),(x,y+28))
        draw.text((x+7,y+4),f'{i:03d}  /  {i/FPS:.2f}s',font=font,fill='white')
    board.save(path)


def main():
    job=json.loads((BATCH/'job.json').read_text(encoding='utf8'))
    assert job.get('result',{}).get('status',{}).get('status_str')=='success'
    count,width,height=job['frames'],job['width'],job['height']
    source=RUNTIME/'ComfyUI_windows_portable/ComfyUI/output'/job['output_prefix']
    paths=sorted(source.glob('frame_*.png'))
    assert len(paths)==count,(len(paths),count)
    for folder in ['raw_png','transparent_png','dark_png','light_png','contact']:
        (OUT/folder).mkdir(parents=True,exist_ok=True)
    key_blue=key_toned_blue if BATCH.name.endswith('-toon3d') else source_keyer()
    raw,rgba,dark,light,records=[],[],[],[],[]
    for i,path in enumerate(paths):
        source_image=Image.open(path).convert('RGB')
        assert source_image.size==(width,height)
        raw.append(source_image)
        shutil.copy2(path,OUT/'raw_png'/f'frame_{i:03}.png')
        keyed,record=key_blue(np.array(source_image))
        keyed.save(OUT/'transparent_png'/f'frame_{i:03}.png')
        rgba.append(keyed)
        bounds=keyed.getbbox()
        record.update(frame=i,source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bbox=bounds,
                      composition='close_to_wide' if i<72 else 'full_body',
                      foreground_touches_border=bool(bounds and (bounds[0]==0 or bounds[1]==0 or bounds[2]==width or bounds[3]==height)))
        records.append(record)
        for color,collection,folder in [('#28353e',dark,'dark_png'),('#e5e3da',light,'light_png')]:
            backdrop=Image.new('RGBA',keyed.size,color)
            backdrop.alpha_composite(keyed)
            frame=backdrop.convert('RGB')
            collection.append(frame)
            frame.save(OUT/folder/f'frame_{i:03}.png')
    for label,frames in [('raw',raw),('dark',dark),('light',light)]:
        for page,start in enumerate(range(0,count,24)):
            contact(frames,list(range(start,min(start+24,count))),OUT/'contact'/f'{label}-{page:02}.png')
    contact(dark,[round(x) for x in np.linspace(0,count-1,16)],OUT/'contact-sheet.png')
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    for folder,name in [('raw_png','original-blue.mp4'),('dark_png','cinematic-rise-preview.mp4'),('light_png','light-background.mp4')]:
        subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-framerate',str(FPS),'-i',str(OUT/folder/'frame_%03d.png'),
            '-frames:v',str(count),'-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/name)],check=True)
    rgba[0].save(OUT/'cinematic-rise.apng',format='PNG',save_all=True,append_images=rgba[1:],duration=1000/FPS,loop=0,disposal=0,blend=0)
    with Image.open(OUT/'cinematic-rise.apng') as animated:
        assert animated.n_frames==count
        for i,frame in enumerate(rgba):
            animated.seek(i)
            assert animated.convert('RGBA').tobytes()==frame.tobytes()
    palette=Image.fromarray(np.concatenate([np.array(f.resize((128,round(128*height/width)))) for f in dark],axis=1)).quantize(colors=256)
    gif=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in dark]
    durations=[(round((i+1)*100/FPS)-round(i*100/FPS))*10 for i in range(count)]
    gif[0].save(OUT/'cinematic-rise-preview.gif',save_all=True,append_images=gif[1:],duration=durations,loop=0,disposal=2,optimize=False)
    capture=cv2.VideoCapture(str(OUT/'cinematic-rise-preview.mp4'))
    assert capture.isOpened() and capture.get(cv2.CAP_PROP_FRAME_COUNT)==count and capture.get(cv2.CAP_PROP_FPS)==FPS
    capture.release()
    report={'frames':count,'fps':FPS,'size':[width,height],'model':'Ref2VA Turbo Q4','image_reference_count':len(job['identity_references']),
            'keyframes':False,'first_last_anchors':False,'original_positions_preserved':True,'frame_scaling':False,
            'ground_alignment':False,'frame_removal':False,'alpha_from_model':False,'keying':'blue key; needs visual inspection',
            'apng_roundtrip_exact':True,'godot_integrated':False,'visual_review':'pending','records':records}
    (OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    for name in ['job.json','workflow.json','source.json','prompt.txt','batch.json','comfy.stdout.log','comfy.stderr.log']:
        path=BATCH/name
        if path.exists():shutil.copy2(path,OUT/name)
    print(json.dumps({k:v for k,v in report.items() if k!='records'},ensure_ascii=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--compact',action='store_true')
    parser.add_argument('--revision2',action='store_true')
    parser.add_argument('--toon3d',action='store_true')
    args=parser.parse_args()
    if args.toon3d:
        BATCH=RUNTIME/'action-batches/rest-rise-cinematic-ref-20261108-toon3d'
        OUT=PROJECT/'artifacts/cinematic-rest-rise-review/result-toon3d'
    elif args.revision2:
        BATCH=RUNTIME/'action-batches/rest-rise-cinematic-ref-20261108-compact-v2'
        OUT=PROJECT/'artifacts/cinematic-rest-rise-review/result-compact-v2'
    elif args.compact:
        BATCH=RUNTIME/'action-batches/rest-rise-cinematic-ref-20261108-compact'
        OUT=PROJECT/'artifacts/cinematic-rest-rise-review/result-compact'
    main()
