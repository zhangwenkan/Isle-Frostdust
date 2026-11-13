"""Export complex action raw frames, keyed previews, seams and provenance."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw

import review_acupoint_microsegments as common
from prepare_complex_action_segments import ROOT, BATCH, REVIEW, W, H, N, sha, save


def sheet(frames, labels, path, columns=5, scale=.5):
    w, h = round(W*scale), round(H*scale)
    board = Image.new('RGB', (columns*w, ((len(frames)+columns-1)//columns)*(h+30)), '#242e3e')
    draw = ImageDraw.Draw(board)
    for i, (frame,label) in enumerate(zip(frames,labels)):
        x,y=(i%columns)*w,(i//columns)*(h+30)
        board.paste(frame.resize((w,h),Image.Resampling.NEAREST),(x,y+30))
        draw.text((x+5,y+4),label,font=common.FONT,fill='white')
    board.save(path)


def apng_checked(frames,path):
    frames[0].save(path,format='PNG',save_all=True,append_images=frames[1:],duration=1000/24,loop=0,disposal=0,blend=0)
    with Image.open(path) as apng:
        assert apng.n_frames==len(frames)
        for i,im in enumerate(frames):
            apng.seek(i)
            assert apng.convert('RGB').tobytes()==im.tobytes()


def video(frames,path):
    process=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error',
        '-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','24','-i','pipe:0','-an',
        '-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
    for im in frames:process.stdin.write(im.tobytes())
    process.stdin.close()
    if process.wait()!=0:raise RuntimeError('Video export failed')


def export(name):
    folder=BATCH/name
    job=json.loads((folder/'job.json').read_text(encoding='utf8'))
    assert job.get('result',{}).get('status',{}).get('status_str')=='success'
    paths=sorted((ROOT/'ComfyUI_windows_portable/ComfyUI/output'/job['output_prefix']).glob('frame_*.png'))
    assert len(paths)==N
    dest=REVIEW/name
    for sub in ('raw','transparent','light','dark'):(dest/sub).mkdir(parents=True,exist_ok=True)
    raw,light,dark,stats=[],[],[],[]
    for i,path in enumerate(paths):
        im=Image.open(path).convert('RGB')
        assert im.size==(W,H)
        shutil.copy2(path,dest/'raw'/f'frame_{i:03d}.png')
        assert sha(path)==sha(dest/'raw'/f'frame_{i:03d}.png')
        keyed,record=common.previous.matte(np.array(im))
        keyed.save(dest/'transparent'/f'frame_{i:03d}.png')
        raw.append(im)
        for color,items,sub in [('#e4e4df',light,'light'),('#242e3e',dark,'dark')]:
            canvas=Image.new('RGBA',im.size,color);canvas.alpha_composite(keyed)
            items.append(canvas.convert('RGB'));items[-1].save(dest/sub/f'frame_{i:03d}.png')
        box=keyed.getbbox()
        record.update(frame=i,bbox=box,source_sha256=sha(path),
            touches_border=box is None or box[0]<=0 or box[1]<=0 or box[2]>=W or box[3]>=H)
        stats.append(record)
    for frames,filename,fps in [(raw,'original-24fps.gif',24),(light,'light-24fps.gif',24),(dark,'dark-slow-6fps.gif',6)]:
        common.anim(frames,dest/filename,fps)
    apng_checked(raw,dest/'original.apng')
    labels=[f'{i:02d} | {i/24:.3f}s' for i in range(N)]
    sheet(raw,labels,dest/'all-raw.png');sheet(light,labels,dest/'all-light.png')
    source=Image.open(folder/'first-source.png').convert('RGB')
    anchor=Image.open(REVIEW/'reference/anchor-576x896.png').convert('RGB')
    sheet([source,raw[0],raw[-1]],['Input','Generated first','Generated last'],dest/'input-first-last.png',columns=3,scale=1)
    sheet([anchor,source,raw[-1]],['Original identity','Segment input','Segment last'],dest/'identity-comparison.png',columns=3,scale=1)
    times={event:payload.get('timestamp') for event,payload in job['result']['status']['messages'] if event in ('execution_start','execution_success')}
    result=dict(segment=name,frames=N,fps=24,execution_seconds=(times['execution_success']-times['execution_start'])/1000,
        prompt_id=job['prompt_id'],input_matches_generated_first_pixels=source.tobytes()==raw[0].tobytes(),
        per_frame_scaling=False,per_frame_translation=False,interpolation=False,hard_endpoint_replacement=False,
        raw_pixels_verified=True,apng_pixels_verified=True,visual_acceptance='pending',frames_audit=stats)
    save(dest/'verification.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='frames_audit'}))


def combine(names):
    dest=REVIEW/'combined';dest.mkdir(exist_ok=True)
    raw,light,dark,sources=[],[],[],[]
    for name in names:
        paths=sorted((REVIEW/name/'raw').glob('frame_*.png'));assert len(paths)==N
        for i,path in enumerate(paths):
            raw.append(Image.open(path).convert('RGB'))
            light.append(Image.open(REVIEW/name/'light'/path.name).convert('RGB'))
            dark.append(Image.open(REVIEW/name/'dark'/path.name).convert('RGB'))
            sources.append(dict(output_frame=len(raw)-1,segment=name,source_frame=i,source=str(path),sha256=sha(path)))
    for images,filename,fps in [(raw,'original-24fps.gif',24),(light,'light-24fps.gif',24),
                              (light,'light-slow-12fps.gif',12),(dark,'dark-24fps.gif',24)]:
        common.anim(images,dest/filename,fps)
    apng_checked(raw,dest/'original.apng')
    video(raw,dest/'original.mp4');video(light,dest/'preview.mp4')
    for k in range(1,len(names)):
        cut=k*N
        common.anim(light[cut-3:cut+4],dest/f'seam-{k:02d}-slow.gif',6)
        sheet(raw[cut-2:cut+2],[f'{names[k-1]}:20',f'{names[k-1]}:21',f'{names[k]}:00',f'{names[k]}:01'],
              dest/f'seam-{k:02d}.png',columns=4,scale=1)
    anchor=Image.open(REVIEW/'reference/anchor-576x896.png').convert('RGB')
    sheet([anchor,raw[0],raw[-1]],['Original stance','Generated first','Generated last'],dest/'original-first-last.png',columns=3,scale=1)
    common.anim(light[-3:]+light[:4],dest/'end-to-start-slow.gif',6)
    save(dest/'verification.json',dict(frames=len(raw),fps=24,duration_seconds=len(raw)/24,segments=names,
        sources=sources,all_frames_preserved=True,raw_and_apng_pixels_verified=True,blend=False,
        interpolation=False,per_frame_scaling=False,per_frame_translation=False,hard_endpoint_replacement=False,
        note='Direct concatenation to expose actual segment seams; no seamlessness or anatomy claim.'))
    print('COMBINED '+str(dest))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['export','combine']);p.add_argument('names',nargs='+')
    a=p.parse_args()
    if a.mode=='export':
        for name in a.names:export(name)
    else:combine(a.names)
