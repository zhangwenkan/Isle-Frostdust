"""Prepare a fresh segmented MiniMax test for a jump/roll/attack action.

The three segments are independent H3 jobs. The only image condition for a
continuation is the previous segment's original final RGB frame; the final
segment also receives the once-prepared user stance as its last-frame target.
"""
from pathlib import Path
import copy
import hashlib
import json
import shutil
import sys

from PIL import Image

ROOT = Path('D:/AI/minimax-h3-minimal')
PROJECT = Path(__file__).resolve().parents[1]
BATCH = ROOT / 'action-batches/gulong-roll-segments-20261109'
REVIEW = PROJECT / 'artifacts/gulong-roll-segments-review'
SOURCE = Path('C:/Users/51440/Downloads/像素武士绿幕姿态对齐版.png')
W, H, N = 576, 896, 22

PROMPTS = {
    '01-takeoff': '''How the reference pictures align with the target video: Picture 1 aligns with the first frame.

integrated_multimodal_description: [Shot 1] A short 0.917-second opening of a complex wuxia movement. Starting from the exact side-facing ready stance, the single fighter bends both knees and drops the hips, turns the waist and shoulders toward screen right, sweeps the relaxed rear hand backward for balance, then drives through the supporting leg into a compact forward leap. The lead knee rises and the coat follows the jump; the body leaves the ground by the end, preparing to tuck and roll. Keep the fighter facing the target on screen right. This segment ends airborne at the beginning of the tuck, without landing.

Use exactly the same character design and body build throughout: unchanged head size, short neck, shoulder breadth, torso thickness, arm and leg lengths, limb thickness, facial features, clothing, belt and sandals. Bending and jumping change pose and position, never anatomy or image scale. Fixed full-body side camera, constant framing and magnification. Preserve the actual vertical airborne displacement and leave generous headroom. Natural connected joints and continuous coat overlap. Crisp illustrated pixel outlines, steady colors and lighting. Keep both eyes with visible dark pupils. Preserve the plain bright green background. All hair, hands and feet remain visible inside the canvas. One character only, empty hands, no scenery, effects, weapon or camera motion.''',
    '02-air-roll-attack': '''How the reference pictures align with the target video: Picture 1 aligns with the first frame.

integrated_multimodal_description: [Shot 1] A short 0.917-second airborne wuxia attack continuation. Begin from the exact airborne tuck shown in Picture 1. Compact the knees toward the chest and rotate the whole body in one clear sideward forward roll, with the coat trailing and the head, hips and legs turning together. Unfold from the roll into a sharp midair attack aimed toward screen right: one arm extends to strike while the other arm opens backward for counterbalance, and one leg reaches through the attack. Keep the torso, shoulders, hips and feet connected; show real airborne displacement and a readable roll, not a standing twist. End just after the airborne strike, still above the ground and beginning to descend.

Use exactly the same character design and body build throughout: unchanged head size, short neck, shoulder breadth, torso thickness, arm and leg lengths, limb thickness, facial features, clothing, belt and sandals. Rotation and folded limbs change pose, never anatomy or image scale. Fixed full-body side camera, constant framing and magnification. Preserve generous headroom and the actual leap. Natural connected joints and continuous coat overlap. Crisp illustrated pixel outlines, steady colors and lighting. Keep both eyes with visible dark pupils. Preserve the plain bright green background. All hair, hands and feet remain visible inside the canvas. One character only, empty hands, no scenery, effects or camera motion.''',
    '03-landing-recover': '''How the reference pictures align with the target video: Picture 1 aligns with the first frame. Picture 2 aligns with the last frame.

integrated_multimodal_description: [Shot 1] A short 0.917-second landing and recovery continuation. Begin from the airborne end of a sideward roll and attack. Finish the descent with the forward foot contacting first, the knee bending deeply to absorb impact, the rear hand reaching down briefly for balance, and the striking arm retracting through the waist. Then rise and turn smoothly back to the exact original side-facing ready stance shown by the final target image. Keep the head looking toward screen right. Show connected landing weight transfer, no teleport, no sliding feet and no sudden body-size change.

Use exactly the same character design and body build throughout: unchanged head size, short neck, shoulder breadth, torso thickness, arm and leg lengths, limb thickness, facial features, clothing, belt and sandals. Landing and bending change pose, never anatomy or image scale. Fixed full-body side camera, constant framing and magnification. Preserve the same character size as the input and keep all hair, hands and feet visible. Natural connected joints and continuous coat overlap. Crisp illustrated pixel outlines, steady colors and lighting. Keep both eyes with visible dark pupils. Preserve the plain bright green background. One character only, empty hands, no scenery, effects or camera motion.''',
}


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_reference():
    source = Image.open(SOURCE).convert('RGB')
    if source.size != (1024, 2048):
        raise ValueError(source.size)
    # One uniform resize, then one fixed placement. The larger canvas leaves
    # room for the jump while the fighter remains the same pixel scale as the
    # earlier anchor.
    resized = source.resize((352, 704), Image.Resampling.LANCZOS)
    canvas = Image.new('RGB', (W, H), (0, 255, 0))
    canvas.paste(resized, (112, 96))
    reference = REVIEW / 'reference/anchor-576x896.png'
    reference.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(reference)
    return reference


def add_last_frame(wf, nodes, last_path):
    image_node = copy.deepcopy(nodes[142])
    new_id = max(node['id'] for node in wf['nodes']) + 1
    link_id = max(link[0] for link in wf['links']) + 1
    image_node.update(id=new_id, title='Original user stance; final recovery target', pos=[0, 1250])
    image_node['widgets_values'] = [last_path.name, 'image']
    image_node['outputs'][0]['links'] = [link_id]
    image_node['outputs'][1]['links'] = []
    wf['nodes'].append(image_node)
    slot = next(i for i, value in enumerate(nodes[131]['inputs']) if value['name'] == 'last_frame')
    nodes[131]['inputs'][slot]['link'] = link_id
    wf['links'].append([link_id, new_id, 0, 131, slot, 'IMAGE'])
    wf.update(last_node_id=new_id, last_link_id=link_id)


def main():
    if (BATCH / 'batch.json').exists():
        raise FileExistsError('Preserve existing batch: ' + str(BATCH))
    BATCH.mkdir(parents=True)
    reference = make_reference()
    inputs = ROOT / 'ComfyUI_windows_portable/ComfyUI/input'
    prepared = inputs / 'H3_gulong_roll_20261109_anchor.png'
    shutil.copy2(reference, prepared)
    source_record = dict(source=str(SOURCE), source_sha256=sha(SOURCE), prepared=str(prepared),
        input_sha256=sha(prepared), source_size=[1024, 2048], uniform_scale=11/32,
        resized_size=[352, 704], paste_offset=[112, 96], canvas=[W, H], crop=False,
        stretch=False, per_frame_alignment=False, original_game_images_or_video_input=False,
        intermediate_poses='Generated by H3; no hand-authored intermediate pose images',
        final_full_action_target='Same prepared user image on segment 03 last-frame condition')
    save(REVIEW / 'reference/source.json', source_record)
    sys.path.insert(0, str(ROOT))
    from run_pixel import make_prompt
    base = json.loads((ROOT / 'action-batches/acupoint-microsegments-20261109/probe-22/workflow.json').read_text(encoding='utf8'))
    for index, (name, prompt) in enumerate(PROMPTS.items(), 1):
        folder = BATCH / name
        folder.mkdir()
        prefix = 'H3_gulong_roll_20261109_' + name.replace('-', '_')
        first = prepared if index == 1 else inputs / f'{prefix}_first.png'
        if index > 1:
            # The actual preceding last frame is copied by the runner after
            # the preceding job is reviewed, before this job is submitted.
            first = inputs / f'{prefix}_first.png'
        shutil.copy2(prepared, folder / 'first-source.png') if index == 1 else None
        (folder / 'prompt.txt').write_text(prompt, encoding='utf8')
        wf = copy.deepcopy(base)
        # Remove the old probe's optional last-frame link before configuring.
        removed = {link[0] for link in wf['links'] if link[3] == 131 and link[4] == 3}
        wf['links'] = [link for link in wf['links'] if link[0] not in removed]
        nodes = {node['id']: node for node in wf['nodes']}
        for node in wf['nodes']:
            for inp in node.get('inputs', []):
                if inp.get('link') in removed:
                    inp['link'] = None
            for out in node.get('outputs', []):
                out['links'] = [v for v in (out.get('links') or []) if v not in removed]
            if node['id'] == 131:
                node['widgets_values'] = [prompt, W, H, N]
                node['widgets_values_named'] = dict(prompt=prompt, width=W, height=H, length=N)
                node['title'] = f'22-frame segmented complex action: {name}'
            elif node['id'] == 142:
                node['widgets_values'] = [first.name, 'image']
                node['title'] = 'Previous segment original last frame; fixed canvas'
            elif node['id'] == 143:
                node['widgets_values'] = [prefix + '/frame']
                node['title'] = 'Preserve every original output frame'
            elif node['id'] == 92:
                node['widgets_values'] = ['video/' + prefix, 'mp4', 'h264']
                node['widgets_values_named'] = {'filename_prefix': 'video/' + prefix, 'format': 'mp4', 'format.codec': 'h264'}
        last_target = None
        if index == 3:
            last_target = inputs / f'{prefix}_last.png'
            shutil.copy2(prepared, last_target)
            add_last_frame(wf, nodes, last_target)
        api = make_prompt(wf, W, N, 8, prefix, H)
        assert api['131']['inputs']['first_frame'] == ['142', 0]
        save(folder / 'workflow.json', wf)
        save(folder / 'source.json', source_record)
        save(folder / 'job.json', dict(output_prefix=prefix, width=W, height=H, frames=N, fps=24,
            steps=8, seed=42, direction=name, action='jump_side_roll_attack', source=source_record,
            client_id=prefix, prompt=api, segment_index=index, final_target=str(last_target) if last_target else None))
    save(BATCH / 'batch.json', dict(status='prepared', runtime_root=str(ROOT), segments=list(PROMPTS),
        source=source_record, user_approved=False, godot_integrated=False,
        reference_motion='gl_skill_single_083 / 摸爬滚打剑; original body-only diagnostic rendered separately'))
    shutil.copy2(ROOT / 'action-batches/rest-rise-right-20261108-v2-vram11/manage_comfy.ps1', BATCH / 'manage_comfy.ps1')
    print(BATCH)
    print(reference)


if __name__ == '__main__':
    main()
