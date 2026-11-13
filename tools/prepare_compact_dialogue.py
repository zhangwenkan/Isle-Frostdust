"""Remove only the exterior checker matte from the supplied compact UI art."""
from pathlib import Path
import hashlib
import json
import shutil

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('C:/Users/51440/Desktop/图片资源/孤屿霜尘/菜单/像素武侠对话框·透明底.png')
REVIEW = ROOT / 'artifacts/compact-dialogue-review'
OUTPUT = ROOT / 'assets/ui/dialogue/pixel_wuxia/compact_frame.png'
for folder in (REVIEW / 'reference', REVIEW / 'backup'):
    folder.mkdir(parents=True, exist_ok=True)
shutil.copy2(SOURCE, REVIEW / 'reference' / SOURCE.name)
for relative in ('scenes/ui/an_lixing_dialogue.tscn', 'scripts/dialogue/portrait_dialogue.gd'):
    backup = REVIEW / 'backup' / Path(relative).name
    if not backup.exists():
        shutil.copy2(ROOT / relative, backup)

source_image = Image.open(SOURCE).convert('RGB')
rgb = np.asarray(source_image).astype(np.int16)
neutral = (rgb.max(axis=2) - rgb.min(axis=2) <= 12) & (rgb.min(axis=2) >= 145)
mask = Image.fromarray(np.uint8(neutral) * 255).copy()
ImageDraw.floodfill(mask, (0, 0), 128)
exterior = np.asarray(mask) == 128
alpha = np.where(exterior, 0, 255).astype(np.uint8)
rgba = Image.fromarray(np.dstack((rgb.astype(np.uint8), alpha)))
crop = rgba.getbbox()
rgba = rgba.crop(crop)
rgba.save(OUTPUT)

canvas = Image.new('RGB', (rgba.width * 2, rgba.height), '#253d46')
for index, color in enumerate(('#253d46', '#ece1ca')):
    backdrop = Image.new('RGBA', rgba.size, color)
    backdrop.alpha_composite(rgba)
    canvas.paste(backdrop.convert('RGB'), (index * rgba.width, 0))
canvas.save(REVIEW / 'alpha-review.png')
report = {'source':str(SOURCE), 'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'source_mode':source_image.mode,'source_size':source_image.size,'crop':crop,
          'output_size':rgba.size,'foreground_rgb_preserved':True,
          'operation':'Remove exterior-connected neutral checker background; crop only.'}
(REVIEW / 'asset-manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=True))
