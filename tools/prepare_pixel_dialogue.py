"""Import the user's layered dialogue art; preserve originals and real alpha."""
from pathlib import Path
import hashlib
import json
import shutil

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('C:/Users/51440/Desktop/图片资源/孤屿霜尘/菜单')
OUT = ROOT / 'assets/ui/dialogue/pixel_wuxia'
REVIEW = ROOT / 'artifacts/pixel-dialogue-review'
for folder in (OUT, REVIEW / 'reference', REVIEW / 'backup'):
    folder.mkdir(parents=True, exist_ok=True)

for relative in ('scenes/ui/an_lixing_dialogue.tscn', 'scripts/dialogue/portrait_dialogue.gd'):
    backup = REVIEW / 'backup' / Path(relative).name
    if not backup.exists():
        shutil.copy2(ROOT / relative, backup)

manifest = {}
for original, output in (
    ('UI对话框元素分层_layer1.png', 'wood_frame.png'),
    ('UI对话框元素分层_layer2.png', 'landscape_paper.png'),
    ('UI对话框元素分层_layer5.png', 'cloud_advance.png'),
    ('空白角色姓名底牌.png', None),
    ('像素武侠对话UI设计.png', None),
):
    source = SOURCE / original
    shutil.copy2(source, REVIEW / 'reference' / original)
    if output:
        shutil.copy2(source, OUT / output)
    im = Image.open(source)
    manifest[original] = {'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                          'size': im.size, 'mode': im.mode, 'output': output}

# This layer alone is RGB on black. Flood only the connected exterior matte,
# keeping all dark red/black details inside the lacquer plaque intact.
rgb = np.asarray(Image.open(SOURCE / '空白角色姓名底牌.png').convert('RGB'))
candidate = Image.fromarray(np.uint8(rgb.max(axis=2) <= 20) * 255).copy()
for point in [(x, y) for x in (0, candidate.width - 1) for y in range(candidate.height)] + [(x, y) for y in (0, candidate.height - 1) for x in range(candidate.width)]:
    if candidate.getpixel(point) == 255:
        ImageDraw.floodfill(candidate, point, 128)
outside = np.asarray(candidate) == 128
alpha = np.where(outside, 0, 255).astype(np.uint8)
plaque = Image.fromarray(np.dstack((rgb, alpha)))
crop = plaque.getbbox()
plaque = plaque.crop(crop)
plaque.save(OUT / 'speaker_plaque.png')
manifest['plaque_processing'] = {'crop': crop, 'connected_black_threshold': 20,
                                'foreground_rgb_unchanged': True}

# A dark teal inset matches the design's paper surround. Its contour comes
# from the actual frame aperture, so no rectangular backing leaks at corners.
frame = Image.open(OUT / 'wood_frame.png').convert('RGBA')
aperture = Image.fromarray(np.uint8(np.asarray(frame)[:, :, 3] < 128) * 255).copy()
ImageDraw.floodfill(aperture, (frame.width // 2, frame.height // 2), 128)
aperture = Image.fromarray(np.uint8(np.asarray(aperture) == 128) * 255)
aperture = aperture.filter(ImageFilter.MaxFilter(7))
inset = Image.new('RGBA', frame.size, '#354b4b')
inset.putalpha(aperture)
inset.save(OUT / 'teal_inset.png')

# Review each transparent layer against both light and dark backgrounds.
sheet = Image.new('RGB', (1240, 540), '#e6dcc3')
for i, bg in enumerate(('#203d47', '#eadfc7')):
    panel = Image.new('RGBA', (620, 270), bg)
    for asset, box in (
        ('teal_inset.png', (0, 15, 620, 130)),
        ('landscape_paper.png', (20, 38, 581, 93)),
        ('wood_frame.png', (0, 15, 620, 130)),
        ('speaker_plaque.png', (56, 28, 105, 26)),
        ('cloud_advance.png', (535, 101, 48, 20)),
    ):
        texture = Image.open(OUT / asset).convert('RGBA')
        x, y, w, h = box
        panel.alpha_composite(texture.resize((w, h), Image.Resampling.LANCZOS), (x, y))
    panel.alpha_composite(plaque.resize((400, 100), Image.Resampling.LANCZOS), (100, 160))
    sheet.paste(panel.convert('RGB'), (i * 620, 0))
    icon = Image.open(OUT / 'cloud_advance.png').convert('RGBA')
    icon_bg = Image.new('RGBA', (620, 270), bg)
    icon_bg.alpha_composite(icon, (25, 20))
    sheet.paste(icon_bg.convert('RGB'), (i * 620, 270))
sheet.save(REVIEW / 'layer-alpha-review.png')
(REVIEW / 'asset-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print('Prepared pixel dialogue art:', OUT)
