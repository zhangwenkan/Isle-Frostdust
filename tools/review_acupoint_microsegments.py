"""Export original short probes and inspection sheets without motion correction."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROJECT = Path(__file__).resolve().parents[1]
ROOT = Path('D:/AI/minimax-h3-minimal')
BATCH = ROOT / 'action-batches/acupoint-microsegments-20261109'
OUT = PROJECT / 'artifacts/acupoint-microsegments-review'
FONT = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 18)
spec = importlib.util.spec_from_file_location('previous_action_export', ROOT / 'action-batches/acupoint-right-20261107-v5b/export_preview.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf8')


def anim(frames, path, fps):
    pal = Image.fromarray(np.concatenate([np.array(f.resize((128, 192))) for f in frames], axis=1)).quantize(colors=256)
    quantized = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    durations = [10 * (round((i+1)*100/fps) - round(i*100/fps)) for i in range(len(frames))]
    quantized[0].save(path, save_all=True, append_images=quantized[1:], duration=durations,
                      loop=0, optimize=False, disposal=2)


def sheet(frames, labels, path, columns=5, scale=0.5):
    w, h = round(512*scale), round(768*scale)
    board = Image.new('RGB', (columns*w, ((len(frames)+columns-1)//columns)*(h+30)), '#242e3e')
    draw = ImageDraw.Draw(board)
    for i, (frame, label) in enumerate(zip(frames, labels)):
        x, y = (i % columns)*w, (i//columns)*(h+30)
        board.paste(frame.resize((w,h), Image.Resampling.NEAREST), (x, y+30))
        draw.text((x+5,y+4), label, font=FONT, fill='white')
    board.save(path)


def main():
    anchor = Image.open(OUT / 'reference/anchor-512x768.png').convert('RGB')
    summaries = []
    counts = [int(v) for v in sys.argv[1:]] or [5, 22]
    for count in counts:
        folder = BATCH / f'probe-{count:02d}'
        job = json.loads((folder/'job.json').read_text(encoding='utf8'))
        if job.get('result',{}).get('status',{}).get('status_str') != 'success':
            print('Not complete:', count)
            continue
        source = ROOT / 'ComfyUI_windows_portable/ComfyUI/output' / job['output_prefix']
        paths = sorted(source.glob('frame_*.png'))
        assert len(paths) == count
        dest = OUT / f'probe-{count:02d}'
        for sub in ['raw', 'transparent', 'light']:
            (dest/sub).mkdir(parents=True, exist_ok=True)
        raw, light, dark, transparent, stats = [], [], [], [], []
        for i, path in enumerate(paths):
            im = Image.open(path).convert('RGB')
            assert im.size == anchor.size
            shutil.copy2(path, dest/'raw'/f'frame_{i:03d}.png')
            rgba, record = previous.matte(np.array(im))
            # No previous per-frame fingertip fixes, no per-frame alignment.
            rgba.save(dest/'transparent'/f'frame_{i:03d}.png')
            transparent.append(rgba)
            raw.append(im)
            for color, collection in [('#e4e4df',light),('#242e3e',dark)]:
                bg = Image.new('RGBA', im.size, color)
                bg.alpha_composite(rgba)
                collection.append(bg.convert('RGB'))
            light[-1].save(dest/'light'/f'frame_{i:03d}.png')
            box = rgba.getbbox()
            record.update(frame=i, bbox=box, source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                touches_border=box is None or box[0]<=0 or box[1]<=0 or box[2]>=512 or box[3]>=768)
            stats.append(record)
        anim(raw,dest/'original-24fps.gif',24)
        anim(light,dest/'light-24fps.gif',24)
        anim(dark,dest/'dark-slow-6fps.gif',6)
        raw[0].save(dest/'original.apng',format='PNG',save_all=True,append_images=raw[1:],duration=1000/24,loop=0,disposal=0,blend=0)
        with Image.open(dest/'original.apng') as apng:
            assert apng.n_frames == count
            for i, im in enumerate(raw):
                apng.seek(i)
                assert apng.convert('RGB').tobytes() == im.tobytes()
        labels = [f'{i:02d} | {i/24:.3f}s' for i in range(count)]
        sheet(raw,labels,dest/'all-raw.png')
        sheet(light,labels,dest/'all-light.png')
        sheet([anchor,raw[0],raw[-1]],['Input anchor','Generated first','Generated last'],dest/'anchor-first-last.png',columns=3,scale=1)
        crops = [anchor.crop((145,45,345,260))] + [f.crop((145,45,345,260)) for f in raw]
        heads = Image.new('RGB',(6*200,((len(crops)+5)//6)*245),'#242e3e')
        draw = ImageDraw.Draw(heads)
        for i,crop in enumerate(crops):
            x,y=(i%6)*200,(i//6)*245
            heads.paste(crop,(x,y+30))
            draw.text((x+5,y+4),'Anchor' if i==0 else f'Frame {i-1:02d}',font=FONT,fill='white')
        heads.save(dest/'heads-fixed-region.png')
        messages=job['result']['status'].get('messages',[])
        timing={name:payload.get('timestamp') for name,payload in messages if name in ('execution_start','execution_success')}
        seconds=(timing['execution_success']-timing['execution_start'])/1000 if len(timing)==2 else None
        summary=dict(frames=count,fps=24,duration_seconds=count/24,execution_seconds=seconds,
            prompt_id=job['prompt_id'],fixed_canvas=[512,768],per_frame_scaling=False,
            per_frame_translation=False,interpolation=False,frame_removal=False,
            original_frames_copied_exactly=True,apng_all_frames_pixel_verified=True,
            input_is_condition_not_guaranteed_exact_output=True,visual_acceptance='pending review',frames_audit=stats)
        save(dest/'verification.json',summary)
        summaries.append({k:v for k,v in summary.items() if k!='frames_audit'})
        print(json.dumps(summaries[-1],ensure_ascii=False))
    save(OUT/'probe-summary.json',summaries)


if __name__ == '__main__':
    main()
