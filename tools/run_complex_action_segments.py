"""Run one reviewed continuation, with exact preceding RGB endpoint input."""
import argparse
import json
import shutil

import continue_acupoint_microsegments as continuation
from prepare_complex_action_segments import BATCH, ROOT, REVIEW, PROMPTS, sha, save, W, H
from PIL import Image


def run(name):
    names = list(PROMPTS)
    folder = BATCH / name
    job = json.loads((folder / 'job.json').read_text(encoding='utf8'))
    index = job['segment_index']-1
    previous_name = job.get('previous_segment', names[index-1] if index else None)
    if job.get('prompt_id') or job.get('result'):
        # Delegate completed/pending/no-retry checks to the established runner.
        pass
    elif index:
        previous = json.loads((BATCH / previous_name / 'job.json').read_text(encoding='utf8'))
        assert previous.get('result', {}).get('status', {}).get('status_str') == 'success'
        paths = sorted((ROOT / 'ComfyUI_windows_portable/ComfyUI/output' / previous['output_prefix']).glob('frame_*.png'))
        assert len(paths) == 22
        source = paths[-1]
        assert Image.open(source).size == (W, H)
        target = ROOT / 'ComfyUI_windows_portable/ComfyUI/input' / job['prompt']['142']['inputs']['image']
        shutil.copy2(source, target)
        shutil.copy2(source, folder / 'first-source.png')
        record = dict(previous_segment=previous_name, previous_frame=21, source=str(source),
            source_sha256=sha(source), prepared=str(target), input_sha256=sha(target),
            original_pixels_unchanged=True, canvas=[W,H], rescale=False, translation=False,
            original_identity_anchor=str(REVIEW / 'reference/anchor-576x896.png'),
            original_game_images_or_video_input=False)
        assert record['source_sha256'] == record['input_sha256']
        save(folder / 'source.json', record)
        job['source'] = record
        save(folder / 'job.json', job)
    if not (folder / 'batch.json').exists():
        save(folder / 'batch.json', dict(status='prepared', runtime_root=str(ROOT), segment=name,
            user_approved=False, godot_integrated=False, service_stopped=True))
    if not (folder / 'manage_comfy.ps1').exists():
        shutil.copy2(BATCH / 'manage_comfy.ps1', folder / 'manage_comfy.ps1')
    continuation.BATCH = BATCH
    continuation.run(name)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('name')
    run(p.parse_args().name)
