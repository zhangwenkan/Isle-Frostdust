"""Prepare and run one independently referenced cinematic rise, without game edits."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import shutil
import subprocess
import sys
import time
import uuid

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
REVIEW = PROJECT / 'artifacts/cinematic-rest-rise-review'
RUNTIME = Path('D:/AI/minimax-h3-minimal')
BATCH = RUNTIME / 'action-batches/rest-rise-cinematic-ref-20261108'
PREVIOUS = RUNTIME / 'action-batches/rest-rise-right-20261108-v2-vram11'
sys.path.insert(0, str(RUNTIME / 'walk-kit/scripts'))
import h3_walk as service


def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def visual_workflow(api):
    """Retain the familiar graph, replacing the pose-anchor node with references."""
    workflow = service.read(PREVIOUS / 'workflow.json')
    originals = {str(n['id']): n for n in workflow['nodes']}
    nodes = {}
    output_types = {
        '127':['MODEL'], '128':['CLIP'], '119':['VAE'],
        '131':['CONDITIONING','LATENT'], '129':['NOISE'], '126':['GUIDER'],
        '123':['SAMPLER'], '124':['SIGMAS'], '125':['LATENT','LATENT'],
        '122':['IMAGE'], '130':['VIDEO'], '92':[], '141':['CLIP'],
        '142':['IMAGE','MASK'], '144':['IMAGE','MASK'], '146':['IMAGE','MASK'], '143':[],
    }
    for order, (key, value) in enumerate(api.items()):
        template = originals.get(key, originals['142'])
        node = copy.deepcopy(template)
        node.update(id=int(key), type=value['class_type'], order=order, inputs=[])
        node['outputs'] = [{'name': kind, 'type':kind, 'links':[]} for kind in output_types[key]]
        node['properties'] = {'Node name for S&R':value['class_type']}
        node['widgets_values_named'] = {k:v for k,v in value['inputs'].items() if not isinstance(v,list)}
        node['widgets_values'] = list(node['widgets_values_named'].values())
        if key in ['142','144','146']:
            node['widgets_values'] += ['image']
            node['pos'] = [0, 650 + (int(key)-142)*180]
        if key == '131':
            node['title'] = 'Three identity references / no frame anchors'
            node['size'] = [500,700]
        nodes[key] = node
    links = []
    for key, data in api.items():
        for name, value in data['inputs'].items():
            if not isinstance(value,list):
                continue
            source, source_slot = value
            kind = output_types[source][source_slot]
            link = len(links)+1
            target_slot = len(nodes[key]['inputs'])
            nodes[key]['inputs'].append({'name':name,'type':kind,'link':link})
            nodes[source]['outputs'][source_slot]['links'].append(link)
            links.append([link,int(source),source_slot,int(key),target_slot,kind])
    workflow.update(nodes=list(nodes.values()),links=links,last_node_id=146,last_link_id=len(links))
    return workflow


def prepare():
    BATCH.mkdir(parents=True,exist_ok=True)
    if (BATCH/'job.json').exists():
        print('Preserving existing batch; no new job prepared.',flush=True)
        return
    api = service.read(REVIEW/'workflow-api.prepared.json')
    toon3d = BATCH.name.endswith('-toon3d')
    compact = '-compact' in BATCH.name or toon3d
    revision2 = BATCH.name.endswith('-compact-v2')
    input_folder = 'cinematic_rest_20261108_toon3d' if toon3d else ('cinematic_rest_20261108_compact_v2' if revision2 else ('cinematic_rest_20261108_compact' if compact else 'cinematic_rest_20261108'))
    inputs = RUNTIME/'ComfyUI_windows_portable/ComfyUI/input'/input_folder
    inputs.mkdir(exist_ok=True)
    sources = []
    image_nodes=[('142','turnaround')] if toon3d else [('142','front'),('144','right'),('146','back')]
    if toon3d:
        api.pop('144')
        api.pop('146')
        api['131']['inputs'].pop('ref_images.ref_image_1')
        api['131']['inputs'].pop('ref_images.ref_image_2')
    for node, direction in image_nodes:
        source = REVIEW/'references'/('turnaround-compact-reference.png' if toon3d else f'{direction}-blue.png')
        target = inputs/source.name
        if not compact and target.exists() and digest(target)!=digest(source):
            raise RuntimeError('Refusing to overwrite different reference: '+str(target))
        if compact and not toon3d:
            from PIL import Image
            with Image.open(source) as image:
                image.resize((384,576),Image.Resampling.NEAREST).save(target)
        else:
            shutil.copy2(source,target)
        api[node]['inputs']['image'] = input_folder+'/'+target.name
        sources.append({'direction':direction,'prepared':str(target),'input_sha256':digest(target),
                        'source':str(source),'reference_resize':[384,576] if compact and not toon3d else None})
    prompt = (REVIEW/('prompt-toon3d.txt' if toon3d else ('prompt-compact-v2.txt' if revision2 else ('prompt-compact.txt' if compact else 'prompt.txt')))).read_text(encoding='utf8')
    api['131']['inputs']['prompt'] = prompt
    if compact:
        api['131']['inputs'].update(width=768,height=448)
    if revision2 or toon3d:
        api['124']['inputs']['steps']=8
    prefix = 'H3_rest_rise_cinematic_ref_20261108'+('_toon3d' if toon3d else ('_compact_v2' if revision2 else ('_compact' if compact else '')))
    api['143']['inputs']['filename_prefix']=prefix+'/frame'
    api['92']['inputs']['filename_prefix']='video/'+prefix
    assert api['131']['class_type']=='MiniMaxH3ReferenceToVideo'
    assert sum(n['class_type']=='LoadImage' for n in api.values())==len(image_nodes)
    assert not any('first_frame' in n['inputs'] or 'last_frame' in n['inputs'] or 'AddGuide' in n['class_type'] for n in api.values())
    settings = api['131']['inputs']
    job = {'output_prefix':prefix,'width':settings['width'],'height':settings['height'],
           'frames':settings['length'],'fps':24,'steps':api['124']['inputs']['steps'],'direction':'cinematic_close_to_wide','action':'rest_to_stand',
           'source':sources[0], 'identity_references':sources,
           'client_id':'cinematic-rest-'+uuid.uuid4().hex, 'prompt':api}
    service.save(BATCH/'job.json',job)
    service.save(BATCH/'workflow.json',visual_workflow(api))
    service.save(BATCH/'source.json',service.read(REVIEW/('references/turnaround-source.json' if toon3d else 'source-manifest.json')))
    service.save(BATCH/'batch.json',{'runtime_root':str(RUNTIME),'status':'prepared','frames':job['frames'],
        'fps':24,'width':job['width'],'height':job['height'],'steps':job['steps'],'seed':42,'action':'rest_to_stand',
        'reference_mode':'Ref2VA','first_frame_image':False,'last_frame_image':False,
        'intermediate_image_guides':False,'video_input':False,'godot_integrated':False,
        'user_approved':False,'generation_authorized':True})
    shutil.copy2(PREVIOUS/'manage_comfy.ps1',BATCH/'manage_comfy.ps1')
    (BATCH/'prompt.txt').write_text(prompt,encoding='utf8')
    print(f"PREPARED: {len(image_nodes)} identity reference image(s), no frame anchors, {job['frames']} frames / 24 fps.",flush=True)


original_manage = service.manage


def manage(root, action):
    if action!='Start':
        return original_manage(root,action)
    subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',
                    str(BATCH/'manage_comfy.ps1'),'-Action','Start','-NoCache'],check=True)
    for _ in range(90):
        if service.alive():
            return
        time.sleep(2)
    raise RuntimeError('ComfyUI did not start; no task submitted.')


def run():
    from download_cinematic_rest_model import MODEL
    model = RUNTIME/MODEL['target']
    if not model.exists() or model.stat().st_size!=MODEL['bytes'] or digest(model)!=MODEL['sha256']:
        raise RuntimeError('Required Ref2VA model missing or checksum mismatch.')
    service.check_runtime(RUNTIME)
    prepare()
    service.manage = manage
    path = BATCH/'batch.json'
    manifest = service.read(path)
    with service.lock(RUNTIME):
        if manifest.get('status') in ['generated','review_exported']:
            print('REUSE existing generated result.',flush=True)
            return
        for reference in service.read(BATCH/'job.json')['identity_references']:
            assert digest(reference['prepared'])==reference['input_sha256']
        manifest['status']='running'
        service.save(path,manifest)
        start=time.monotonic()
        try:
            job=service.submitted_job(BATCH,RUNTIME,manifest,path)
        except Exception as exc:
            manifest.update(status='stopped',error=str(exc))
            service.save(path,manifest)
            # Stop only our idle service. Never cancel another task or ambiguous running work.
            if service.alive() and service.own_server(RUNTIME,manifest):
                service.empty_queue()
                manage(RUNTIME,'Stop')
            raise
        finally:
            for stream in ['stdout','stderr']:
                log=RUNTIME/f'comfy.{stream}.log'
                if log.exists() and service.own_server(RUNTIME,manifest):
                    shutil.copy2(log,BATCH/log.name)
        if service.alive():
            if not service.own_server(RUNTIME,manifest):
                raise RuntimeError('Service ownership changed; refusing shutdown.')
            service.empty_queue()
            manage(RUNTIME,'Stop')
        manifest.update(status='generated',prompt_id=job['prompt_id'],elapsed_seconds=time.monotonic()-start)
        service.save(path,manifest)
        print('GENERATED: original PNG sequence saved; owned model service stopped.',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--wait-for-model',action='store_true')
    parser.add_argument('--compact',action='store_true')
    parser.add_argument('--revision2',action='store_true')
    parser.add_argument('--toon3d',action='store_true')
    args=parser.parse_args()
    if args.toon3d:
        BATCH=RUNTIME/'action-batches/rest-rise-cinematic-ref-20261108-toon3d'
    elif args.revision2:
        BATCH=RUNTIME/'action-batches/rest-rise-cinematic-ref-20261108-compact-v2'
    elif args.compact:
        BATCH=RUNTIME/'action-batches/rest-rise-cinematic-ref-20261108-compact'
    if args.prepare_only:
        prepare()
    else:
        if args.wait_for_model:
            from download_cinematic_rest_model import MODEL
            target=RUNTIME/MODEL['target']
            deadline=time.monotonic()+7200
            while not target.exists():
                if time.monotonic()>deadline:
                    raise RuntimeError('Model download not complete; no generation submitted.')
                print('Waiting for the separately authorized model download.',flush=True)
                time.sleep(30)
        run()
