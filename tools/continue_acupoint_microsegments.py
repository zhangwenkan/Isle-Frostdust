"""Prepare/run one 22-frame continuation; never resubmit an attempted job."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import shutil
import sys
import time

from PIL import Image

PROJECT = Path(__file__).resolve().parents[1]
ROOT = Path('D:/AI/minimax-h3-minimal')
BATCH = ROOT / 'action-batches/acupoint-microsegments-20261109'
REVIEW = PROJECT / 'artifacts/acupoint-microsegments-review'
sys.path.insert(0, str(ROOT))
from run_pixel import make_prompt
import run_acupoint_microsegments as runner


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(name, source, prompt_file, last_frame=None):
    folder = BATCH / name
    if folder.exists():
        raise FileExistsError('Existing segment preserved: ' + str(folder))
    assert Image.open(source).size == (512, 768)
    if last_frame:
        assert Image.open(last_frame).size == (512, 768)
    prompt = prompt_file.read_text(encoding='utf8')
    folder.mkdir()
    prefix = 'H3_acupoint_micro_20261109_' + name.replace('-', '_')
    inputs = ROOT / 'ComfyUI_windows_portable/ComfyUI/input'
    prepared = inputs / f'{prefix}_first.png'
    shutil.copy2(source, prepared)
    shutil.copy2(source, folder/'first-source.png')
    shutil.copy2(prompt_file, folder/'prompt.txt')
    shutil.copy2(BATCH/'manage_comfy.ps1', folder/'manage_comfy.ps1')
    wf = json.loads((BATCH/'probe-22/workflow.json').read_text(encoding='utf8'))
    nodes = {node['id']:node for node in wf['nodes']}
    nodes[131]['widgets_values'] = [prompt, 512, 768, 22]
    nodes[131]['widgets_values_named'] = dict(prompt=prompt, width=512, height=768, length=22)
    nodes[131]['title'] = '22-frame continuation from preceding original last frame'
    nodes[142]['widgets_values'] = [prepared.name, 'image']
    nodes[142]['title'] = 'Previous segment last frame; unchanged pixels and canvas'
    nodes[143]['widgets_values'] = [prefix+'/frame']
    nodes[92]['widgets_values'] = ['video/'+prefix,'mp4','h264']
    nodes[92]['widgets_values_named'] = {'filename_prefix':'video/'+prefix,'format':'mp4','format.codec':'h264'}
    last_record = None
    if last_frame:
        last_input = inputs / f'{prefix}_last.png'
        shutil.copy2(last_frame,last_input)
        shutil.copy2(last_frame,folder/'last-target.png')
        new_id = max(nodes)+1
        image_node = copy.deepcopy(nodes[142])
        image_node.update(id=new_id,title='Original user stance: final recovery target',pos=[0,1250])
        image_node['widgets_values'] = [last_input.name,'image']
        link_id = max(link[0] for link in wf['links'])+1
        image_node['outputs'][0]['links'] = [link_id]
        image_node['outputs'][1]['links'] = []
        wf['nodes'].append(image_node)
        slot = next(i for i,v in enumerate(nodes[131]['inputs']) if v['name']=='last_frame')
        nodes[131]['inputs'][slot]['link'] = link_id
        wf['links'].append([link_id,new_id,0,131,slot,'IMAGE'])
        wf.update(last_node_id=new_id,last_link_id=link_id)
        last_record=dict(path=str(last_frame),prepared=str(last_input),sha256=sha(last_input))
    api = make_prompt(wf,512,22,8,prefix,768)
    assert api['131']['inputs']['first_frame'] == ['142',0]
    assert ('last_frame' in api['131']['inputs']) == bool(last_frame)
    source_record=dict(source=str(source),source_sha256=sha(source),prepared=str(prepared),
        input_sha256=sha(prepared),canvas=[512,768],input_pixels_unchanged=True,
        input_rescaling=False,input_translation=False,original_identity_anchor=str(REVIEW/'reference/anchor-512x768.png'),
        model_image_inputs=['previous segment last original frame'] + (['original user stance as last frame'] if last_frame else []),
        original_game_images_or_video_input=False,last_target=last_record)
    save(folder/'source.json',source_record)
    save(folder/'workflow.json',wf)
    save(folder/'job.json',dict(output_prefix=prefix,width=512,height=768,frames=22,fps=24,steps=8,seed=42,
        direction=name,action=name,source=source_record,client_id=prefix,prompt=api))
    save(folder/'batch.json',dict(status='prepared',runtime_root=str(ROOT),segment=name,source=source_record,
        user_approved=False,godot_integrated=False,service_stopped=True))
    print('PREPARED '+str(folder),flush=True)


def run(name):
    folder = BATCH / name
    runner.BATCH = folder
    h3 = runner.h3
    h3.manage = runner.manage
    path = folder/'batch.json'
    manifest = h3.read(path)
    with h3.lock(ROOT):
        if h3.read(folder/'job.json').get('result',{}).get('status',{}).get('status_str')=='success':
            print('REUSE already completed segment',flush=True)
            return
        try:
            manifest.update(status='running',service_stopped=False)
            h3.save(path,manifest)
            started = time.monotonic()
            job = h3.submitted_job(folder,ROOT,manifest,path)
            manifest.update(status='generated-awaiting-review',prompt_id=job['prompt_id'],wall_seconds=time.monotonic()-started)
            print('GENERATED '+name,flush=True)
        except Exception as exc:
            manifest.update(status='stopped',error=str(exc))
            raise
        finally:
            if h3.alive() and h3.own_server(ROOT,manifest):
                h3.empty_queue()
                runner.manage(ROOT,'Stop')
            manifest['service_stopped'] = not h3.alive()
            for stream in ('stdout','stderr'):
                source_log=ROOT/f'comfy.{stream}.log'
                if source_log.exists():shutil.copy2(source_log,folder/source_log.name)
            h3.save(path,manifest)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('mode',choices=['prepare','run'])
    p.add_argument('name')
    p.add_argument('--source',type=Path)
    p.add_argument('--prompt-file',type=Path)
    p.add_argument('--last-frame',type=Path)
    a=p.parse_args()
    if a.mode=='prepare':
        if not a.source or not a.prompt_file:p.error('prepare requires --source and --prompt-file')
        prepare(a.name,a.source,a.prompt_file,a.last_frame)
    else:run(a.name)
