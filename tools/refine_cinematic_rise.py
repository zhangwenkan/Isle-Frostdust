"""Repair the approved shot from lossless frames; never regenerate its motion."""
from pathlib import Path
import argparse
import hashlib
import json
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'artifacts/cinematic-rest-rise-review'
SOURCE = REVIEW / 'result-toon3d'
OUT = REVIEW / 'result-toon3d-refined'
WEIGHTS = Path('D:/AI/minimax-h3-minimal/ComfyUI_windows_portable/ComfyUI/models/upscale_models/realesr-animevideov3.pth')
WEIGHT_SHA = 'b8a8376811077954d82ca3fcf476f1ac3da3e8a68a4f4d71363008000a18b75d'
SAMPLES = [0, 48, 96, 130, 155, 165, 170, 174]


def nearest_values(values, seeds):
    _, labels = cv2.distanceTransformWithLabels((~seeds).astype(np.uint8), cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    return values[seeds][labels - 1]


def matte(rgb, scale=4, crop=True):
    """Estimate coverage and remove the locally observed blue backdrop from edges."""
    if crop:
        signed = rgb.astype(np.int16)
        candidate = ((signed[..., 2]-signed[..., 1]) < 9) | ((signed[..., 2]-signed[..., 0]) < 16)
        yy, xx = np.where(candidate)
        pad = 5*scale
        x0,x1=max(0,int(xx.min())-pad),min(rgb.shape[1],int(xx.max())+pad+1)
        y0,y1=max(0,int(yy.min())-pad),min(rgb.shape[0],int(yy.max())+pad+1)
        if (x1-x0)*(y1-y0)<rgb.shape[0]*rgb.shape[1]*.85:
            result=np.zeros((*rgb.shape[:2],4),np.uint8)
            result[y0:y1,x0:x1]=matte(rgb[y0:y1,x0:x1],scale,crop=False)
            return result
    f = rgb.astype(np.float32) / 255
    bg = f[..., 2] - f[..., 1]
    br = f[..., 2] - f[..., 0]
    core = (bg < 9 / 255) | (br < 16 / 255)
    # These are trimap bands, not a largest-component operation: keep detached leaves/hair.
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * scale + 1, 2 * scale + 1))
    fg = cv2.erode(core.astype(np.uint8), k).astype(bool)
    bk = ~cv2.dilate(core.astype(np.uint8), k).astype(bool)
    assert fg.any() and bk.any()
    F = nearest_values(f, fg)
    B = nearest_values(f, bk)
    v = F - B
    alpha = np.clip(((f - B) * v).sum(2) / np.maximum((v * v).sum(2), .001), 0, 1)
    alpha[fg] = 1
    alpha[bk] = 0
    # Remove only subpixel detached key noise, never select a largest body component.
    n, labels, stats, _ = cv2.connectedComponentsWithStats((alpha > .12).astype(np.uint8), 8)
    tiny = np.flatnonzero(stats[:, cv2.CC_STAT_AREA] < scale * scale)
    tiny = tiny[tiny != 0]
    if len(tiny):
        alpha[np.isin(labels, tiny)] = 0
    # A very small coverage smoothing at 4x removes stair steps without eroding hair.
    alpha = cv2.GaussianBlur(alpha, (3, 3), .48)
    alpha[fg] = 1
    alpha[bk] = 0
    unmixed = (f - (1 - alpha[..., None]) * B) / np.maximum(alpha[..., None], .05)
    # Very low coverage cannot provide stable chroma; use nearby foreground only there.
    trust = np.clip((alpha - .08) / .52, 0, 1)[..., None]
    color = np.clip(unmixed * trust + F * (1 - trust), 0, 1)
    color[fg] = f[fg]
    boundary_distance = cv2.distanceTransform((alpha > .95).astype(np.uint8), cv2.DIST_L2, 5)
    spill = np.maximum(color[..., 2] - np.maximum(color[..., 0], color[..., 1]), 0)
    color[..., 2] -= spill * np.clip(1 - boundary_distance / (3 * scale), 0, 1)
    rgba = np.rint(np.concatenate([color, alpha[..., None]], 2) * 255).astype(np.uint8)
    rgba[rgba[..., 3] == 0, :3] = 0
    return rgba


def composite(rgba, color):
    a = Image.fromarray(rgba) if isinstance(rgba, np.ndarray) else rgba
    return Image.alpha_composite(Image.new('RGBA', a.size, color), a).convert('RGB')


def upscale(indices):
    import torch
    from spandrel import ModelLoader
    assert hashlib.sha256(WEIGHTS.read_bytes()).hexdigest() == WEIGHT_SHA
    torch.set_num_threads(6)
    device = 'xpu' if torch.xpu.is_available() else 'cpu'
    model = ModelLoader().load_from_file(str(WEIGHTS)).eval().to(device)
    if device == 'xpu':
        model = model.half()
    print(f'Model {model.architecture.name}; scale {model.scale}; device {device}', flush=True)
    (OUT / 'upscaled_rgb').mkdir(parents=True, exist_ok=True)
    with torch.inference_mode():
        for i in indices:
            dest = OUT / 'upscaled_rgb' / f'frame_{i:03}.png'
            if dest.exists():
                continue
            started = time.time()
            a = np.array(Image.open(SOURCE / 'raw_png' / f'frame_{i:03}.png').convert('RGB'))
            t = torch.from_numpy(a.transpose(2, 0, 1).copy()).float().div_(255).unsqueeze(0).to(device)
            if device == 'xpu':
                t = t.half()
            output = model(t).float().clamp_(0, 1).squeeze(0).permute(1, 2, 0).cpu().numpy()
            Image.fromarray(np.rint(output * 255).astype(np.uint8)).save(dest)
            print(f'upscale {i:03} {time.time()-started:.1f}s', flush=True)


def export(indices):
    for name in ['transparent_4x', 'transparent_png', 'dark_png', 'light_png']:
        (OUT / name).mkdir(parents=True, exist_ok=True)
    for i in indices:
        repaired = OUT / 'eye_repaired_rgb' / f'frame_{i:03}.png'
        rgb = np.array(Image.open(repaired if repaired.exists() else OUT / 'upscaled_rgb' / f'frame_{i:03}.png'))
        rgba = Image.fromarray(matte(rgb))
        if i in SAMPLES:
            rgba.save(OUT / 'transparent_4x' / f'frame_{i:03}.png',compress_level=3)
        # Pillow RGBA resizing uses premultiplied alpha, avoiding black RGB bleeding.
        rgba = rgba.resize((1536, 896), Image.Resampling.LANCZOS)
        rgba.save(OUT / 'transparent_png' / f'frame_{i:03}.png',compress_level=3)
        for folder, color in [('dark_png', '#28353e'), ('light_png', '#e5e3da')]:
            composite(rgba, color).save(OUT / folder / f'frame_{i:03}.png')
        print(f'matte {i:03}', flush=True)


def boards():
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 22)
    # Each crop uses the same field of view and display scale before and after.
    crops = {0: (190, 0, 630, 430), 48: (220, 95, 510, 340), 96: (315, 170, 500, 355),
             130: (300, 200, 480, 385), 155: (265, 85, 420, 285),
             165: (270, 15, 410, 175), 170: (270, 10, 410, 170), 174: (265, 10, 405, 170)}
    board = Image.new('RGB', (1440, 4 * 560), '#222b33')
    d = ImageDraw.Draw(board)
    for j, i in enumerate([0, 96, 155, 174]):
        crop = crops[i]
        before = Image.open(SOURCE / 'dark_png' / f'frame_{i:03}.png').crop(crop)
        after = Image.open(OUT / 'dark_png' / f'frame_{i:03}.png').crop(tuple(2 * n for n in crop))
        w, h = before.size
        factor = min(700 / w, 510 / h)
        size = (round(w * factor), round(h * factor))
        for col, im in enumerate([before, after]):
            board.paste(im.resize(size, Image.Resampling.LANCZOS), (col * 720 + (720-size[0])//2, j*560+45))
        d.text((20, j*560+10), f'第 {i} 帧 · 原版', font=font, fill='white')
        d.text((740, j*560+10), '修复试样 · 同样的取景与显示大小', font=font, fill='white')
    board.save(OUT / 'clarity-comparison.png')
    i = 174
    a = Image.open(OUT / 'transparent_png' / f'frame_{i:03}.png')
    strip = Image.new('RGB', (1536, 896))
    for j, color in enumerate(['#101418', '#e5e3da', '#577a70']):
        strip.paste(composite(a, color).crop((480, 0, 992, 896)), (512*j, 0))
    strip.save(OUT / 'edge-backgrounds.png')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--stage', choices=['upscale', 'export', 'boards', 'sample'], default='sample')
    args = parser.parse_args()
    ids = list(range(175)) if args.all else SAMPLES
    if args.stage in ['upscale', 'sample']:
        upscale(ids)
    if args.stage in ['export', 'sample']:
        export(ids)
    if args.stage in ['boards', 'sample']:
        boards()
