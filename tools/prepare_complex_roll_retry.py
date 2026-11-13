"""A single narrower roll retry, preserving the rejected roll+attack segment."""
import copy
import json
from prepare_complex_action_segments import BATCH, ROOT, W, H, N, save

NAME='02-air-roll-only-v2'
PROMPT='''How the reference pictures align with the target video: Picture 1 aligns with the first frame.

integrated_multimodal_description: [Shot 1] A 0.917-second continuous forward somersault, already airborne. Begin with the same crouched airborne man in Picture 1. He tucks his chin tightly toward his chest, pulls BOTH knees close to his chest, and rolls head-over-heels FORWARD in the plane of the screen. His shoulders dive downward, his pelvis rises ABOVE his head, and both tucked feet pass over the top of his head. Clearly show the middle inverted pose with the head BELOW the hips, then complete the forward rotation and open slightly into a low falling crouch with the head upright again. One compact aerial somersault only. Keep both arms bent close to the body during the turn. The roll remains near the center of the frame with almost no horizontal travel. End descending in a compact crouch, with both legs still bent. No kick, no punch, no extended leg and no second jump in this fragment.

The single same illustrated fighter keeps the reference's head size, short neck, shoulder breadth, torso thickness, leg length, thigh thickness, clothing, belt and sandals. Rotation changes orientation and limb overlap, never anatomy or image scale. Camera stays locked, full body, constant magnification. His body really rotates upside down; the camera does not rotate. Hair and clothing follow the turn, attached continuously at scalp and waist. Preserve two arms, two legs and connected joints throughout the somersault. Crisp illustrated pixel outlines, steady colors and lighting, plain bright green background. Keep all hands and feet inside the canvas, compactly folded. Empty hands, no effects or scenery.'''


def main():
    folder=BATCH/NAME
    if folder.exists():raise FileExistsError(folder)
    folder.mkdir()
    previous=BATCH/'02-air-roll-attack'
    wf=json.loads((previous/'workflow.json').read_text(encoding='utf8'))
    prefix='H3_gulong_roll_20261109_'+NAME.replace('-','_')
    for node in wf['nodes']:
        if node['id']==131:
            node['widgets_values']=[PROMPT,W,H,N]
            node['widgets_values_named']=dict(prompt=PROMPT,width=W,height=H,length=N)
            node['title']='One compact forward somersault only; no attack'
        elif node['id']==142:node['widgets_values']=[prefix+'_first.png','image']
        elif node['id']==143:node['widgets_values']=[prefix+'/frame']
        elif node['id']==92:
            node['widgets_values']=['video/'+prefix,'mp4','h264']
            node['widgets_values_named']={'filename_prefix':'video/'+prefix,'format':'mp4','format.codec':'h264'}
    import sys
    sys.path.insert(0,str(ROOT))
    from run_pixel import make_prompt
    api=make_prompt(wf,W,N,8,prefix,H)
    job=json.loads((previous/'job.json').read_text(encoding='utf8'))
    for key in ('prompt_id','result','submitted_at','finished_at','submission_attempted','number','node_errors'):job.pop(key,None)
    job.update(output_prefix=prefix,direction=NAME,action='compact_forward_somersault_only',
        client_id=prefix,prompt=api,previous_segment='01-takeoff',segment_index=2,
        retry_of='02-air-roll-attack',retry_reason='No inversion and right boundary clipping; split roll from attack')
    # The runner supplies fresh ownership/source records before submission.
    save(folder/'workflow.json',wf);save(folder/'job.json',job)
    (folder/'prompt.txt').write_text(PROMPT,encoding='utf8')
    print(folder)


if __name__=='__main__':main()
