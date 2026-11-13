"""Inspect individual segments and uncorrected joins; preserve source pixels."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw

import review_acupoint_microsegments as review

ROOT=review.ROOT
BATCH=review.BATCH
OUT=review.OUT


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')


def export(name):
    folder=BATCH/name
    job=json.loads((folder/'job.json').read_text(encoding='utf8'))
    assert job.get('result',{}).get('status',{}).get('status_str')=='success'
    dest=OUT/name
    paths=sorted((ROOT/'ComfyUI_windows_portable/ComfyUI/output'/job['output_prefix']).glob('frame_*.png'))
    assert len(paths)==22
    for sub in ('raw','transparent','light'):(dest/sub).mkdir(parents=True,exist_ok=True)
    raw,light,dark,stats=[],[],[],[]
    for i,path in enumerate(paths):
        im=Image.open(path).convert('RGB')
        assert im.size==(512,768)
        shutil.copy2(path,dest/'raw'/f'frame_{i:03d}.png')
        assert sha(path)==sha(dest/'raw'/f'frame_{i:03d}.png')
        keyed,record=review.previous.matte(np.array(im))
        keyed.save(dest/'transparent'/f'frame_{i:03d}.png')
        raw.append(im)
        for color,items in [('#e4e4df',light),('#242e3e',dark)]:
            canvas=Image.new('RGBA',im.size,color)
            canvas.alpha_composite(keyed)
            items.append(canvas.convert('RGB'))
        light[-1].save(dest/'light'/f'frame_{i:03d}.png')
        box=keyed.getbbox()
        record.update(frame=i,bbox=box,source_sha256=sha(path),touches_border=box is None or box[0]<=0 or box[1]<=0 or box[2]>=512 or box[3]>=768)
        stats.append(record)
    for frames,filename,fps in [(raw,'original-24fps.gif',24),(light,'light-24fps.gif',24),(dark,'dark-slow-6fps.gif',6)]:
        review.anim(frames,dest/filename,fps)
    raw[0].save(dest/'original.apng',format='PNG',save_all=True,append_images=raw[1:],duration=1000/24,loop=0,disposal=0,blend=0)
    with Image.open(dest/'original.apng') as apng:
        assert apng.n_frames==22
        for i,im in enumerate(raw):
            apng.seek(i)
            assert apng.convert('RGB').tobytes()==im.tobytes()
    labels=[f'{i:02d} | {i/24:.3f}s' for i in range(22)]
    review.sheet(raw,labels,dest/'all-raw.png')
    review.sheet(light,labels,dest/'all-light.png')
    source=Image.open(folder/'first-source.png').convert('RGB')
    anchor=Image.open(OUT/'reference/anchor-512x768.png').convert('RGB')
    review.sheet([source,raw[0],raw[-1]],['Previous last = Input','New first','New last'],dest/'input-first-last.png',columns=3,scale=1)
    review.sheet([anchor,source,raw[-1]],['Original identity','Segment input','Segment last'],dest/'identity-comparison.png',columns=3,scale=1)
    crops=[anchor.crop((140,40,360,320)),source.crop((140,40,360,320))]+[im.crop((140,40,360,320)) for im in raw]
    board=Image.new('RGB',(6*220,4*310),'#242e3e')
    draw=ImageDraw.Draw(board)
    for i,crop in enumerate(crops):
        x,y=i%6*220,i//6*310
        board.paste(crop,(x,y+30))
        draw.text((x+5,y+4),['Original','Segment input'][i] if i<2 else f'Frame {i-2:02d}',font=review.FONT,fill='white')
    board.save(dest/'heads-fixed-region.png')
    times={event:payload.get('timestamp') for event,payload in job['result']['status']['messages'] if event in ('execution_start','execution_success')}
    output=dict(segment=name,frames=22,fps=24,execution_seconds=(times['execution_success']-times['execution_start'])/1000,
        prompt_id=job['prompt_id'],input_matches_previous_last_pixels=True,input_matches_generated_first_pixels=source.tobytes()==raw[0].tobytes(),
        per_frame_scaling=False,per_frame_translation=False,interpolation=False,hard_endpoint_replacement=False,
        original_frames_verified=True,apng_pixels_verified=True,visual_acceptance='pending',frames_audit=stats)
    save(dest/'verification.json',output)
    print(json.dumps({k:v for k,v in output.items() if k!='frames_audit'}))


def combine(names,output_name):
    dest=OUT/output_name
    dest.mkdir(parents=True,exist_ok=True)
    raw,light,sources=[],[],[]
    for name in names:
        paths=sorted((OUT/name/'raw').glob('frame_*.png'))
        assert len(paths)==22
        for i,path in enumerate(paths):
            raw.append(Image.open(path).convert('RGB'))
            light.append(Image.open(OUT/name/'light'/path.name).convert('RGB'))
            sources.append(dict(output_frame=len(raw)-1,segment=name,source_frame=i,source=str(path),sha256=sha(path)))
    review.anim(raw,dest/'original-24fps.gif',24)
    review.anim(light,dest/'light-24fps.gif',24)
    review.anim(light,dest/'light-slow-12fps.gif',12)
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    for images,filename in [(raw,'original.mp4'),(light,'preview.mp4')]:
        process=subprocess.Popen([ffmpeg,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
            '-s','512x768','-r','24','-i','pipe:0','-an','-c:v','libx264','-crf','17',
            '-pix_fmt','yuv420p','-movflags','+faststart',str(dest/filename)],stdin=subprocess.PIPE)
        for im in images:process.stdin.write(im.tobytes())
        process.stdin.close()
        if process.wait()!=0:raise RuntimeError('Video export failed')
    raw[0].save(dest/'original.apng',format='PNG',save_all=True,append_images=raw[1:],duration=1000/24,loop=0,disposal=0,blend=0)
    with Image.open(dest/'original.apng') as apng:
        assert apng.n_frames==len(raw)
        for i,im in enumerate(raw):
            apng.seek(i)
            assert apng.convert('RGB').tobytes()==im.tobytes()
    for k in range(1,len(names)):
        cut=k*22
        review.anim(light[cut-3:cut+4],dest/f'seam-{k:02d}-slow.gif',6)
        review.sheet(raw[cut-2:cut+2],[f'{names[k-1]}:{20}',f'{names[k-1]}:{21}',f'{names[k]}:00',f'{names[k]}:01'],dest/f'seam-{k:02d}.png',columns=4,scale=1)
    verification=dict(frames=len(raw),fps=24,duration_seconds=len(raw)/24,segments=names,sources=sources,
        raw_frame_pixels_verified=True,all_frames_preserved=True,blend=False,interpolation=False,
        per_frame_scaling=False,per_frame_translation=False,hard_endpoint_replacement=False,
        note='Straight concatenation for reviewing real segment seams; no seamlessness claimed.')
    save(dest/'verification.json',verification)
    anchor=Image.open(OUT/'reference/anchor-512x768.png').convert('RGB')
    review.sheet([anchor,raw[0],raw[-1]],['Original stance','Action first','Action last'],dest/'original-first-last.png',columns=3,scale=1)
    review.anim(light[-3:]+light[:4],dest/'end-to-start-slow.gif',6)
    print('COMBINED '+str(dest))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('mode',choices=['export','combine'])
    p.add_argument('names',nargs='+')
    p.add_argument('--output-name',default='combined')
    a=p.parse_args()
    if a.mode=='export':
        for name in a.names:export(name)
    else:combine(a.names,a.output_name)
