"""Compose actual camera/model comparisons and validate the captured review."""
import json,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/near-mid-depth-review'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19)
prefix=sys.argv[1] if len(sys.argv)>1 else ''
static_prefix=prefix or 'current'
output_prefix=prefix+'-' if prefix else ''
frame_dir=OUT/(output_prefix+'motion-frames')
before=json.loads((OUT/'before-static-check.json').read_text(encoding='utf-8'))
after=json.loads((OUT/(static_prefix+'-static-check.json')).read_text(encoding='utf-8'))
assert all(s['supported'] for s in after)
assert max(abs(a['hero_height_px']-b['hero_height_px']) for a,b in zip(before,after))<.05
assert all(s['sea_opacity']==0 for s in after[:6])
assert after[6]['fov']==before[6]['fov'] and after[7]['fov']==before[7]['fov']
motion=json.loads((OUT/(output_prefix+'motion-check.json')).read_text(encoding='utf-8'))
assert not motion['failures'];assert motion['bindings']==320
assert len(list(frame_dir.glob('frame-*.jpg')))==336
assert min(motion['near_far_movement_ratios'])>2.0
audit=json.loads((OUT/'blender-audit.json').read_text(encoding='utf-8'));assert not audit['failures']
protected=json.loads((OUT/'geometry-preservation.json').read_text(encoding='utf-8'))
assert not protected['unexpected_geometry_changes'] and not protected['protected_file_changes']
board=Image.new('RGB',(1280,390*3),'#202924');draw=ImageDraw.Draw(board)
for row,(shot,label) in enumerate([('middle','林中'),('clearing','透光段'),('connection','接头')]):
    for column,(shot_prefix,title) in enumerate([('before','此前'),(static_prefix,'本轮')]):
        x=column*640;y=row*390;draw.text((x+10,y+4),title+' · '+label,font=font,fill='white')
        board.paste(Image.open(OUT/(shot_prefix+'-'+shot+'.png')).resize((640,360),Image.Resampling.LANCZOS),(x,y+30))
board.save(OUT/(output_prefix+'before-after.jpg'),quality=95)
board=Image.new('RGB',(960,296*4),'#202924');draw=ImageDraw.Draw(board)
for index,second in enumerate([0,4,6,9,12,16,21,26]):
    x=index%2*480;y=index//2*296;draw.text((x+10,y+3),f'{second}秒',font=font,fill='white')
    board.paste(Image.open(frame_dir/f'frame-{second*12:04d}.jpg').resize((480,270),Image.Resampling.LANCZOS),(x,y+26))
board.save(OUT/(output_prefix+'motion-contact.jpg'),quality=95)
summary={'static_views':len(after),'max_hero_size_difference_px':max(abs(a['hero_height_px']-b['hero_height_px']) for a,b in zip(before,after)),
         'duration_seconds':28,'capture_fps':12,'frames':336,'shared_bindings':320,
         'near_far_motion_ratio_range':[min(motion['near_far_movement_ratios']),max(motion['near_far_movement_ratios'])],
         'protected_geometry_objects':protected['protected_objects'],'protected_files':protected['protected_files'],'failures':[]}
(OUT/(output_prefix+'review-summary.json')).write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary))
