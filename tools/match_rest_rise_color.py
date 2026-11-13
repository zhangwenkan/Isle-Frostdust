"""Match the settled rise colors to the actual gameplay idle; never alter alpha/geometry."""
from pathlib import Path
import hashlib
import json
import re

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'artifacts/interaction-rest-rise-review/review-chin/hero'
OUT = ROOT / 'artifacts/rest-rise-color-review'
ASSET = ROOT / 'assets/characters/rest_rise_right/color_matched'


def smoothstep(value):
    value = np.clip(value, 0.0, 1.0)
    return value * value * (3.0 - 2.0 * value)


def main():
    OUT.mkdir(exist_ok=True)
    (ASSET / 'atlases').mkdir(parents=True, exist_ok=True)
    idle = np.array(Image.open(ROOT / 'assets/characters/green_three_walk/right_idle.png').convert('RGBA'))
    ref = idle[:, :, :3].astype(np.float32)
    cv2.setRNGSeed(42)
    colors = ref[idle[:, :, 3] > 245][::4]
    _, _, palette = cv2.kmeans(colors, 12, None,
        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 80, .05), 4, cv2.KMEANS_PP_CENTERS)
    source_samples, target_samples = [], []
    for frame in [100, 101, 102]:
        original = np.array(Image.open(SOURCE / f'transparent_png/frame_{frame:03}.png'))[:, 160:672]
        # Exclude silhouettes and moving ink lines from the palette measurement.
        mask = cv2.erode(((original[:, :, 3] > 245) & (idle[:, :, 3] > 245)).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
        source_color = cv2.GaussianBlur(original[:, :, :3].astype(np.float32), (5, 5), 0)
        target_color = cv2.GaussianBlur(ref, (5, 5), 0)
        mask &= np.max(np.abs(source_color - target_color), axis=2) < 20
        source_samples.append(source_color[mask])
        target_samples.append(target_color[mask])
    source_samples = np.concatenate(source_samples)
    target_samples = np.concatenate(target_samples)
    labels = np.sum((source_samples[:, None, :] - palette) ** 2, axis=2).argmin(axis=1)
    offsets = np.array([np.median(target_samples[labels == i] - source_samples[labels == i], axis=0) for i in range(12)])
    offsets = np.clip(offsets, -10.0, 10.0)

    def correct(rgb):
        # A fixed soft color map, shared by every ending frame; no per-frame auto exposure.
        flat = rgb.astype(np.float32).reshape(-1, 3)
        result = flat.copy()
        for start in range(0, len(flat), 65536):
            part = flat[start:start + 65536]
            distance = np.sum((part[:, None, :] - palette) ** 2, axis=2)
            weights = np.exp(-(distance - distance.min(axis=1)[:, None]) / (2 * 22.0 ** 2))
            adjustment = weights @ offsets / weights.sum(axis=1)[:, None]
            # Keep the repaired black chin line and all near-black ink intact.
            adjustment *= smoothstep((part.max(axis=1) - 16) / 24)[:, None]
            result[start:start + len(part)] += adjustment
        return result.reshape(rgb.shape)

    atlas_paths = sorted((ROOT / 'assets/characters/rest_rise_right/atlases').glob('sheet_*.png'))
    atlases = [Image.open(path).convert('RGBA') for path in atlas_paths]
    resource = (SOURCE / 'rest_rise_chin.tres').read_text(encoding='utf8')
    regions = re.findall(r'\[sub_resource type="AtlasTexture" id="Frame_(\d+)"\]\s+atlas = ExtResource\("(\d+)"\)\s+region = Rect2\((\d+), (\d+), (\d+), (\d+)\)', resource)
    assert len(regions) == 103
    placement = {int(frame): (int(atlas) - 1, int(x), int(y), int(w), int(h)) for frame, atlas, x, y, w, h in regions}
    changed = []
    output_frames = {}
    for frame in range(103):
        src = np.array(Image.open(SOURCE / f'transparent_png/frame_{frame:03}.png').convert('RGBA'))
        atlas_id, x, y, width, height = placement[frame]
        assert (width, height) == (832, 768)
        assert np.array_equal(np.array(atlases[atlas_id].crop((x, y, x + width, y + height))), src)
        result = src.copy()
        weight = float(smoothstep((frame - 78) / 20))
        if weight > 0:
            mapped = correct(src[:, :, :3])
            result[:, :, :3] = np.rint(np.clip(src[:, :, :3] + (mapped - src[:, :, :3]) * weight, 0, 255)).astype(np.uint8)
            result[src[:, :, 3] == 0] = src[src[:, :, 3] == 0]
        assert np.array_equal(result[:, :, 3], src[:, :, 3])
        assert np.array_equal(result[src[:, :, :3].max(axis=2) <= 16], src[src[:, :, :3].max(axis=2) <= 16])
        if frame <= 78:
            assert np.array_equal(result, src)
        diff = np.abs(result[:, :, :3].astype(np.int16) - src[:, :, :3])
        changed.append({'frame':frame,'strength':weight,'changed_pixels':int(np.any(diff,axis=2).sum()),'max_channel_delta':int(diff.max())})
        # Preserve every region from the original resource, including its atlas layout.
        atlases[atlas_id].paste(Image.fromarray(result), (x, y))
        if frame in [78, 90, 98, 102]:
            output_frames[frame] = result
    # Reuse untouched atlases. Only three final sheets need derived files.
    for i, atlas in enumerate(atlases):
        if i < 6:
            replacement = f'res://assets/characters/rest_rise_right/atlases/sheet_{i:02}.png'
        else:
            destination = ASSET / f'atlases/sheet_{i:02}.png'
            atlas.save(destination)
            replacement = f'res://assets/characters/rest_rise_right/color_matched/atlases/sheet_{i:02}.png'
        resource = resource.replace(f'path="atlases/sheet_{i:02}.png"', f'path="{replacement}"')
    (ASSET / 'rest_rise_color_matched.tres').write_text(resource, encoding='utf8')
    tail = output_frames[102][:, 160:672]
    original_tail = np.array(Image.open(SOURCE / 'transparent_png/frame_102.png'))[:, 160:672]
    mask = cv2.erode(((tail[:, :, 3] > 245) & (idle[:, :, 3] > 245)).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    source_blur = cv2.GaussianBlur(original_tail[:, :, :3].astype(np.float32), (5, 5), 0)
    target_blur = cv2.GaussianBlur(ref, (5, 5), 0)
    mask &= np.max(np.abs(source_blur - target_blur), axis=2) < 20
    after_blur = cv2.GaussianBlur(tail[:, :, :3].astype(np.float32), (5, 5), 0)
    report = {'reference':'assets/characters/green_three_walk/right_idle.png','frames':103,'fps':24,
        'alpha_unchanged_all_frames':True,'black_ink_unchanged':True,'frames_0_to_78_identical':True,
        'color_map_palette':palette.tolist(),'color_map_offsets':offsets.tolist(),
        'before_mean_rgb_bias':np.mean(target_blur[mask]-source_blur[mask],axis=0).tolist(),
        'after_mean_rgb_bias':np.mean(target_blur[mask]-after_blur[mask],axis=0).tolist(),
        'records':changed,'original_asset_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in atlas_paths}}
    (OUT/'asset-verification.json').write_text(json.dumps(report, indent=2),encoding='utf8')
    (ASSET/'source.json').write_text(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2),encoding='utf8')
    board=Image.new('RGB',(780,800),'#7b8778');draw=ImageDraw.Draw(board)
    for i,(label,array) in enumerate([('Original rise ending',original_tail),('Matched rise ending',tail),('Gameplay idle',idle)]):
        im=Image.fromarray(array);small=im.resize((256,384));board.paste(small,(i*260,30),small)
        head=im.crop((145,45,355,235)).resize((256,232));board.paste(head,(i*260,430),head);draw.text((i*260+4,8),label,fill='white')
    board.save(OUT/'color-match-comparison.png')
    print(json.dumps({k:v for k,v in report.items() if k not in ['records','color_map_palette','color_map_offsets','original_asset_sha256']},indent=2))


if __name__ == '__main__':
    main()
