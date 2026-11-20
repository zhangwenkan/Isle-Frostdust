"""Package actual Godot screenshots and frame times; no artwork generation."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import argparse
import json
import subprocess
import imageio_ffmpeg

PROJECT = Path(__file__).resolve().parents[1]
OUT = PROJECT / 'artifacts/pixel-vegetation-harmony-review'
BEFORE = PROJECT / 'artifacts/pixel-vegetation-review'
FONT = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 21)
LABELS = {'default': '竹林与桥头', 'grass': '林下草地', 'trees': '洞前树冠', 'vines': '洞口藤叶'}


def comparisons():
    produced = []
    for label, title in LABELS.items():
        old, new = BEFORE / f'after-{label}.png', OUT / f'after-{label}.png'
        if not old.exists() or not new.exists():
            continue
        a, b = Image.open(old).convert('RGB'), Image.open(new).convert('RGB')
        if a.size != b.size:
            raise ValueError(f'Mismatched source sizes for {label}: {a.size} / {b.size}')
        w, h = a.size
        sheet = Image.new('RGB', (w * 2, h + 46), '#202a27')
        sheet.paste(a, (0, 46))
        sheet.paste(b, (w, 46))
        draw = ImageDraw.Draw(sheet)
        draw.text((18, 9), f'{title} · 调整前', font=FONT, fill='#eeeeea')
        draw.text((w+18, 9), f'{title} · 本轮实机', font=FONT, fill='#eeeeea')
        path = OUT / f'comparison-{label}.png'
        sheet.save(path)
        produced.append(path.name)
    return produced


def motion():
    times_path = OUT / 'motion-times.json'
    if not times_path.exists():
        return {'state': 'not captured'}
    times = json.loads(times_path.read_text(encoding='utf-8'))
    if len(times) < 2 or any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError('Need strictly increasing actual capture times')
    files = [OUT / 'motion' / f'{i:03d}.png' for i in range(len(times))]
    for file in files:
        if not file.exists():
            raise FileNotFoundError(file)
    # Match each captured image to the actual interval before the following image.
    durations = [b-a for a, b in zip(times, times[1:])]
    durations.append(durations[-1])
    frames = [Image.open(file).convert('RGB').resize((960, 540), Image.Resampling.NEAREST) for file in files]
    frames[0].save(OUT / 'harmony-motion.gif', save_all=True, append_images=frames[1:],
                   duration=[max(10, round(t*1000)) for t in durations], loop=0, optimize=False)
    concat = OUT / 'motion-concat.txt'
    lines = []
    for i, duration in enumerate(durations):
        lines.extend([f"file 'motion/{i:03d}.png'", 'option framerate 1000', f'duration {duration:.9f}'])
    lines.extend([f"file 'motion/{len(files)-1:03d}.png'", 'option framerate 1000'])
    concat.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    command = [imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-f', 'concat', '-safe', '0',
               '-i', str(concat), '-fps_mode', 'vfr', '-c:v', 'libx264', '-crf', '18',
               '-pix_fmt', 'yuv420p', '-video_track_timescale', '1000', '-movflags', '+faststart', str(OUT/'harmony-motion.mp4')]
    result = subprocess.run(command, check=False, capture_output=True, text=True, encoding='utf-8', errors='replace')
    (OUT/'package-ffmpeg.log').write_text(result.stderr, encoding='utf-8')
    result.check_returncode()
    indices = [round(i*(len(files)-1)/7) for i in range(8)]
    sheet = Image.new('RGB', (1280, 4*395), '#202a27')
    draw = ImageDraw.Draw(sheet)
    for j, i in enumerate(indices):
        image = Image.open(files[i]).convert('RGB').resize((640, 360), Image.Resampling.NEAREST)
        x, y = j % 2 * 640, j // 2 * 395
        sheet.paste(image, (x, y))
        draw.text((x+12, y+363), f'实机 {times[i]:.2f} 秒', font=FONT, fill='#eeeeea')
    sheet.save(OUT/'motion-contact-sheet.jpg', quality=94)
    return {'frames': len(files), 'first_capture_seconds': times[0], 'last_capture_seconds': times[-1],
            'last_frame_hold_seconds': durations[-1], 'timing': 'actual capture intervals, no interpolation'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--static-only', action='store_true')
    args = parser.parse_args()
    result = {'comparisons': comparisons()}
    if not args.static_only:
        result['motion'] = motion()
    (OUT/'package-check.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
