"""Encode and inspect the captured Godot frames at their simulated speed."""
from pathlib import Path
import json,subprocess
import imageio_ffmpeg
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/foreground-space-review'
frames=OUT/'motion-frames';ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
items=sorted(frames.glob('*.jpg'))
assert len(items)==1080 and all(p.name==f'{i:04d}.jpg' for i,p in enumerate(items))
video=OUT/'foreground-space-review.mp4'
subprocess.run([ffmpeg,'-hide_banner','-loglevel','warning','-y','-framerate','30','-i',str(frames/'%04d.jpg'),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
result=subprocess.run([ffmpeg,'-hide_banner','-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True)
assert result.returncode==0 and not result.stderr.strip()
reader=imageio_ffmpeg.read_frames(str(video),pix_fmt='rgb24');meta=next(reader);count=sum(1 for _ in reader)
assert count==1080
board=Image.new('RGB',(1440,882),(28,35,36));draw=ImageDraw.Draw(board)
for i,t in enumerate([0,5,9,13,17,22,27,31,35]):
    x=(i%3)*480;y=(i//3)*294
    pic=Image.open(frames/f'{t*30:04d}.jpg').resize((480,270),Image.Resampling.LANCZOS)
    board.paste(pic,(x,y+24));draw.text((x+8,y+5),f'{t}s',fill='white')
board.save(OUT/'motion-contact.jpg',quality=94)
comparison=Image.new('RGB',(1280,768),(28,35,36));draw=ImageDraw.Draw(comparison)
for i,phase in enumerate(['before','review']):
    for j,view in enumerate(['forest','cliff-detail']):
        x=i*640;y=j*384
        im=Image.open(OUT/f'{phase}-{view}.png').resize((640,360),Image.Resampling.LANCZOS)
        comparison.paste(im,(x,y+24));draw.text((x+8,y+5),f'{phase} / {view}',fill='white')
comparison.save(OUT/'before-after.jpg',quality=94)
report={'frames':count,'fps':meta['fps'],'duration_seconds':meta['duration'],'size':meta['size'],'decode_errors':result.stderr,'video_bytes':video.stat().st_size}
(OUT/'video-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
