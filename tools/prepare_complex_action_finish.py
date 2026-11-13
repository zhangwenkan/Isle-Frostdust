"""Prepare landing-strike and recovery after the successful inversion trial."""
import copy
import json
import shutil
import sys
from prepare_complex_action_segments import BATCH, ROOT, REVIEW, W, H, N, save, add_last_frame

STAGES = [
    ('03-land-strike-v2', '02-air-roll-only-v2', '''How the reference pictures align with the target video: Picture 1 aligns with the first frame.

integrated_multimodal_description: [Shot 1] A 0.917-second wuxia landing and strike. The same man starts in the compact airborne crouch shown in Picture 1, having just completed a somersault. Unfold the lower legs downward while descending. The forward foot meets the ground, followed by the rear foot; both knees bend to absorb the fall. As his weight settles onto his feet, the hips and shoulders turn together and the forward hand delivers one crisp short palm strike toward screen right. The other open hand extends backward for balance. Finish in a low stable stance facing the target at screen right, with the striking arm extended and both feet supporting his weight. One landing followed by one short palm strike, smoothly connected. The floor level is near y=770 in this 896-pixel image, and the whole fighter remains near the center with only a small forward step. Do not jump again. No somersault in this segment.

Keep exactly the same character build: same head size, short neck, shoulder width, torso thickness, arm and leg lengths, thigh and calf thickness. The thighs and waist must stay the same size as he unfolds. The knees bend naturally without shortening bones. Arms remain attached at the shoulders, hands attached at wrists, and feet attached at ankles. Preserve the outfit, wrapped limbs, belt, sandals and waist-attached ragged coat. Fixed full-body camera, constant size and lighting, no zoom or camera movement. Crisp illustrated pixel lines. Pure bright green background. All hands and feet stay inside the canvas with margin. One character, empty hands, no magic, shadows, props or scenery.'''),
    ('04-recover-v2', '03-land-strike-v2', '''How the reference pictures align with the target video: Picture 1 aligns with the first frame. Picture 2 aligns with the last frame.

integrated_multimodal_description: [Shot 1] A 0.917-second recovery from a landed palm strike to the original ready stance. Begin from the exact low grounded pose in Picture 1. Relax and retract the striking hand, bring the counterbalancing arm back down, and straighten the knees gradually as the pelvis rises. Make one small natural foot adjustment to return to the original stance in Picture 2. Coordinate hips, waist, chest and shoulders during the return. Finish facing screen right with the exact original outfit and build. Feet support the body throughout; no jumping, floating, abrupt pose changes or sliding. The same character must remain the same size during the return: no thinner torso, no narrowed thighs, no longer neck, no stretched legs. Let the coat settle as the body returns, without growing into a new front panel.

Keep the head size, shoulder width, torso thickness, limb lengths, thigh and calf thickness unchanged from the reference, respecting natural pose perspective. Connected joints and continuous overlapping clothing. Fixed full-body camera, constant framing and magnification. Crisp illustrated pixel outlines, stable facial features, visible dark pupils, same belt and sandals. Plain bright green background. All hair, hands and feet remain visible, one empty-handed character, no effects or scenery.''')
]


def main():
    sys.path.insert(0,str(ROOT))
    from run_pixel import make_prompt
    base=json.loads((BATCH/'01-takeoff/workflow.json').read_text(encoding='utf8'))
    inputs=ROOT/'ComfyUI_windows_portable/ComfyUI/input'
    for index,(name,previous,prompt) in enumerate(STAGES,3):
        folder=BATCH/name
        if folder.exists():raise FileExistsError(folder)
        folder.mkdir()
        prefix='H3_gulong_roll_20261109_'+name.replace('-','_')
        wf=copy.deepcopy(base);nodes={node['id']:node for node in wf['nodes']}
        nodes[131]['widgets_values']=[prompt,W,H,N]
        nodes[131]['widgets_values_named']=dict(prompt=prompt,width=W,height=H,length=N)
        nodes[131]['title']=name
        nodes[142]['widgets_values']=[prefix+'_first.png','image']
        nodes[143]['widgets_values']=[prefix+'/frame']
        nodes[92]['widgets_values']=['video/'+prefix,'mp4','h264']
        nodes[92]['widgets_values_named']={'filename_prefix':'video/'+prefix,'format':'mp4','format.codec':'h264'}
        last=None
        if index==4:
            last=inputs/(prefix+'_last.png')
            shutil.copy2(REVIEW/'reference/anchor-576x896.png',last)
            shutil.copy2(last,folder/'last-target.png')
            add_last_frame(wf,nodes,last)
        api=make_prompt(wf,W,N,8,prefix,H)
        save(folder/'workflow.json',wf)
        save(folder/'job.json',dict(output_prefix=prefix,width=W,height=H,frames=N,fps=24,steps=8,seed=42,
            direction=name,action=name,client_id=prefix,prompt=api,segment_index=index,
            previous_segment=previous,final_target=str(last) if last else None))
        (folder/'prompt.txt').write_text(prompt,encoding='utf8')
        print(folder)


if __name__=='__main__':main()
