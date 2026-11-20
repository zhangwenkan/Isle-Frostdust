"""Package already-rendered game screenshots; no geometry or retouching."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,json
import imageio_ffmpeg
root=Path(__file__).resolve().parents[1]
out=root/'artifacts/pixel-cape-polish-review'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
canvas=Image.new('RGB',(1280,780),'#1d2b30');draw=ImageDraw.Draw(canvas)
for i,(label,path) in enumerate([
 ('修改前 · 同机位',out/'before/game-color-overview.png'),
 ('本轮 · 岩面、草缘、竹叶与受光调整',out/'game-color-overview.png')]):
    im=Image.open(path).convert('RGB').resize((640,360),Image.Resampling.NEAREST)
    canvas.paste(im,(i*640,40));draw.text((i*640+16,8),label,font=font,fill='#e1e6de')
detail=Image.open(out/'game-character-detail.png').convert('RGB').resize((640,360),Image.Resampling.NEAREST)
stairs=Image.open(out/'game-stairs-detail.png').convert('RGB').resize((640,360),Image.Resampling.NEAREST)
canvas.paste(detail,(0,420));canvas.paste(stairs,(640,420))
draw.text((16,393),'本轮 · 人物附近',font=font,fill='#e1e6de')
draw.text((656,393),'本轮 · 台阶近景',font=font,fill='#e1e6de')
canvas.save(out/'comparison.png')
frames=sorted((out/'motion').glob('*.png'))
if len(frames)==48:
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff,'-y','-loglevel','error','-framerate','12','-i',str(out/'motion/%03d.png'),'-c:v','libx264','-crf','17','-pix_fmt','yuv420p',str(out/'camera-motion.mp4')],check=True)
    ims=[Image.open(p).convert('RGB') for p in frames]
    ims[0].save(out/'camera-motion.gif',save_all=True,append_images=ims[1:],duration=83,loop=0)
    strip=Image.new('RGB',(960,540))
    for i,idx in enumerate([0,8,16,24,32,40]):
        strip.paste(ims[idx].resize((320,180),Image.Resampling.NEAREST),((i%3)*320,(i//3)*180))
    strip.crop((0,0,960,360)).save(out/'motion-contact-sheet.png')
print(json.dumps({'comparison':str(out/'comparison.png'),'motion_frames':len(frames)}))
