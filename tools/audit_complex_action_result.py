"""Check delivered frame provenance and summarize the actual segmented trial."""
from pathlib import Path
import json

from PIL import Image
import numpy as np

from prepare_complex_action_segments import BATCH, REVIEW, ROOT, sha, save
from review_complex_action_segments import sheet
import review_acupoint_microsegments as common

NAMES=['01-takeoff','02-air-roll-only-v2','03-land-strike-v2','04-recover-v2']


def main():
    records=[]
    for index,name in enumerate(NAMES):
        batch=BATCH/name
        result=REVIEW/name
        job=json.loads((batch/'job.json').read_text(encoding='utf8'))
        manifest=json.loads((batch/'batch.json').read_text(encoding='utf8'))
        audit=json.loads((result/'verification.json').read_text(encoding='utf8'))
        assert job['result']['status']['status_str']=='success'
        assert manifest['service_stopped']
        paths=sorted((result/'raw').glob('frame_*.png'))
        assert len(paths)==22
        for path in paths:
            assert Image.open(path).size==(576,896)
        if index:
            assert sha(batch/'first-source.png')==sha(REVIEW/NAMES[index-1]/'raw/frame_021.png')
        assert not any(frame['touches_border'] for frame in audit['frames_audit'])
        records.append(dict(segment=name,prompt_id=job['prompt_id'],execution_seconds=audit['execution_seconds'],
            source_sha256=sha(batch/'first-source.png'),first_bbox=audit['frames_audit'][0]['bbox'],
            last_bbox=audit['frames_audit'][-1]['bbox'],service_stopped=True))
    assert sha(BATCH/NAMES[-1]/'last-target.png')==sha(REVIEW/'reference/anchor-576x896.png')
    combined=json.loads((REVIEW/'combined/verification.json').read_text(encoding='utf8'))
    assert combined['segments']==NAMES and combined['frames']==88
    for rec in combined['sources']:
        assert sha(Path(rec['source']))==rec['sha256']
    raw=[Image.open(rec['source']).convert('RGB') for rec in combined['sources']]
    with Image.open(REVIEW/'combined/original.apng') as apng:
        assert apng.n_frames==88
        for i,frame in enumerate(raw):
            apng.seek(i)
            assert apng.convert('RGB').tobytes()==frame.tobytes()
    # Fixed canvas overview: no pose-dependent crop, scale, translation or warp.
    picks=[0,5,10,15,21,22,27,32,35,39,43,44,46,49,54,60,65,66,70,74,78,82,86,87]
    light=[]
    for k in picks:
        rec=combined['sources'][k]
        light.append(Image.open(REVIEW/rec['segment']/'light'/f"frame_{rec['source_frame']:03d}.png").convert('RGB'))
    sheet(light,[f'F{k:02d} | {k/24:.2f}s' for k in picks],REVIEW/'combined/key-poses.jpg',columns=6,scale=.5)
    anchor=Image.open(REVIEW/'reference/anchor-576x896.png').convert('RGB')
    rgba,_=common.previous.matte(np.array(anchor));bg=Image.new('RGBA',anchor.size,'#e4e4df');bg.alpha_composite(rgba)
    ids=[0,21,65,72,80,87]
    compare=[bg.convert('RGB')]
    for k in ids:
        rec=combined['sources'][k]
        compare.append(Image.open(REVIEW/rec['segment']/'light'/f"frame_{rec['source_frame']:03d}.png").convert('RGB'))
    sheet(compare,['Original']+[f'F{k:02d}' for k in ids],REVIEW/'diagnosis/body-return-comparison.jpg',columns=7,scale=.75)
    summary=dict(frames=88,fps=24,duration_seconds=88/24,segments=records,
        generation_seconds_used=sum(r['execution_seconds'] for r in records),
        discarded_attempt_seconds=json.loads((REVIEW/'02-air-roll-attack/verification.json').read_text(encoding='utf8'))['execution_seconds'],
        all_continuation_inputs_exact_previous_original_last=True,final_target_exact_prepared_original=True,
        selected_frames_touching_border=[],all_88_original_apng_frames_pixel_verified=True,
        per_frame_transform=False,interpolation=False,hard_frame_replacement=False,godot_integrated=False,
        acceptance='Trial awaiting user review; observed limb artifacts, temporal holds and ground drift remain')
    save(REVIEW/'audit.json',summary)
    parent=json.loads((BATCH/'batch.json').read_text(encoding='utf8'))
    parent.update(status='completed-trial-awaiting-user-review',selected_segments=NAMES,
        rejected_segments=['02-air-roll-attack'],unused_prepared_segments=['03-landing-recover'],
        service_stopped=True,user_approved=False,godot_integrated=False,
        review_directory=str(REVIEW),review_audit=str(REVIEW/'audit.json'))
    save(BATCH/'batch.json',parent)
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
