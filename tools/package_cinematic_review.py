"""Encode actual Godot captures and build contact sheets for visual review."""
from pathlib import Path
import json, subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/cinematic-coast-review'
frames=OUT/'review-frames'
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
images=sorted(frames.glob('*.jpg'))
assert len(images)==1410, len(images)
assert all(p.name==f'{i:04d}.jpg' for i,p in enumerate(images))
assert Image.open(images[0]).size==(1280,720)
video=OUT/'cinematic-coast-review.mp4'
subprocess.run([ffmpeg,'-hide_banner','-loglevel','warning','-y','-framerate','30','-i',str(frames/'%04d.jpg'),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
decoded=subprocess.run([ffmpeg,'-hide_banner','-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True)
(OUT/'video-decode.log').write_text(decoded.stderr,encoding='utf-8')
assert decoded.returncode==0 and not decoded.stderr.strip(),decoded.stderr
reader=imageio_ffmpeg.read_frames(str(video),pix_fmt='rgb24')
metadata=next(reader)
decoded_frames=sum(1 for _ in reader)
assert decoded_frames==1410,decoded_frames

def sheet(name,seconds,cols=3):
    w,h=480,270
    rows=(len(seconds)+cols-1)//cols
    board=Image.new('RGB',(cols*w,rows*(h+24)),(26,34,35))
    draw=ImageDraw.Draw(board)
    for i,t in enumerate(seconds):
        pic=Image.open(frames/f'{round(t*30):04d}.jpg').resize((w,h),Image.Resampling.LANCZOS)
        x=i%cols*w;y=i//cols*(h+24)
        board.paste(pic,(x,y+24));draw.text((x+8,y+5),f'{t:g}s',fill='white')
    board.save(OUT/name,quality=93)
sheet('motion-contact.jpg',[0,4,7,10,15,20,24,29,35,38,41,46])
sheet('water-contact.jpg',[39,40.5,42,43.5,45,46.5])
sheet('bridge-idle-contact.jpg',[7,8,9,10,11,12])
report={'video':str(video),'frames':decoded_frames,'fps':metadata['fps'],'duration_seconds':metadata['duration'],'size':metadata['size'],'decode_errors':decoded.stderr,'bytes':video.stat().st_size}
(OUT/'video-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
