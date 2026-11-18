"""Verify actual captures and compose the character's shared-light review."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/hero-forest-light-review'
FONT = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 19)

bindings = json.loads((OUT / 'frame-bindings.json').read_text(encoding='utf-8'))
assert not bindings['failures']
differences = []
for key in bindings['render_pairs']:
    original = np.asarray(Image.open(OUT / 'frame-check' / f'{key}-original.png'))
    shader = np.asarray(Image.open(OUT / 'frame-check' / f'{key}-shader.png'))
    differences.append({
        'key': key,
        'alpha_diff_pixels': int((original[:, :, 3] != shader[:, :, 3]).sum()),
        'mean_channel_difference': float(np.abs(original.astype(int) - shader.astype(int)).mean()),
    })
pixels = {
    'pairs': differences,
    'max_alpha_diff_pixels': max(d['alpha_diff_pixels'] for d in differences),
    'max_mean_channel_difference': max(d['mean_channel_difference'] for d in differences),
}
assert pixels['max_alpha_diff_pixels'] == 0
assert pixels['max_mean_channel_difference'] < .03
(OUT / 'frame-pixel-check.json').write_text(json.dumps(pixels, indent=2), encoding='utf-8')

protected = json.loads((OUT / 'before/protected-hashes.json').read_text(encoding='utf-8'))
changed = [path for path, digest in protected.items()
           if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest]
assert not changed, changed
(OUT / 'preservation-check.json').write_text(json.dumps({
    'protected_files': len(protected), 'changed': changed,
    'note': 'Character paint, existing normals, layout, GLB, scene and forest shaders are unchanged.',
}, indent=2), encoding='utf-8')

motion = json.loads((OUT / 'motion-check.json').read_text(encoding='utf-8'))
assert not motion['failures'] and motion['bindings'] == 316
assert len(list((OUT / 'motion-frames').glob('frame-*.jpg'))) == 288
assert set(motion['facing_seen']) == {'left', 'right'}

board = Image.new('RGB', (960, 362), '#202924')
draw = ImageDraw.Draw(board)
field_stats = []
for column, time in enumerate([0, 5, 10, 15]):
    x = column * 240
    draw.text((x + 10, 5), f'同一位置 · {time}秒', font=FONT, fill='white')
    crop = Image.open(OUT / f'pass2-middle-t{time:02d}-lit.png').crop((595, 300, 685, 440))
    board.paste(crop.resize((216, 336), Image.Resampling.NEAREST), (x + 12, 26))
    field = np.asarray(Image.open(OUT / f'pass2-field-t{time:02d}.png'))[305:430, 620:660, :3]
    mask = (field.max(2) - field.min(2) < 1) & (field[:, :, 0] > 20)
    values = field[:, :, 0][mask]
    field_stats.append({'time': time, 'min_display_gray': int(values.min()),
                        'max_display_gray': int(values.max()), 'mean_display_gray': float(values.mean())})
board.save(OUT / 'character-light-times.png')
(OUT / 'field-display-samples.json').write_text(json.dumps(field_stats, indent=2), encoding='utf-8')

board = Image.new('RGB', (1024, 600), '#202924')
draw = ImageDraw.Draw(board)
for column, (mode, label) in enumerate([('before', '此前：普通场景受光'), ('lit', '现在：参与森林透光')]):
    x = column * 512
    draw.text((x + 10, 5), label, font=FONT, fill='white')
    image = Image.open(OUT / f'pass2-middle-t15-{mode}.png')
    board.paste(image.resize((512, 288), Image.Resampling.LANCZOS), (x, 30))
    crop = image.crop((595, 305, 685, 435))
    board.paste(crop.resize((180, 260), Image.Resampling.NEAREST), (x + 166, 330))
board.save(OUT / 'hero-light-comparison.jpg', quality=95)

print(f'{bindings["frames_checked"]} animation frames, {len(differences)} pixel pairs, '
      f'{len(protected)} protected files, 316 shared materials, 288 motion frames: passed')
