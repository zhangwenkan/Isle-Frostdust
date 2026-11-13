"""Static-only preview, before user approval for video checks."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[1]/'artifacts/bamboo-valley-review'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24)
canvas=Image.new('RGB',(960,1152),'#203331');draw=ImageDraw.Draw(canvas)
for i,(label,name) in enumerate([('竹林段：后方谷坡与层叠竹林','final-x-6.8.png'),('走到桥上：远山视野展开','final-x07.8.png')]):
    y=i*576;draw.text((14,y+4),label,font=font,fill='#ece8d8')
    canvas.paste(Image.open(root/name).convert('RGB').resize((960,540),Image.Resampling.LANCZOS),(0,y+36))
canvas.save(root/'static-preview.jpg',quality=96)
agents=Path(__file__).resolve().parents[1]/'AGENTS.md'
section='''

### 竹林后方山谷与桥头远山展开（用户要求，2026-11-08）

- 用户要求竹林段背后填成山谷，不再空透远景群山，走到桥附近才展开远山。当前通过 Blender MCP 新增连续谷坡、凹谷、局部露岩和后层竹林，集合 `30_West_Bamboo_Valley`；作者 `tools/blender/bamboo_valley.py`。
- 保留现有彩色水墨方向、开场道路和篝火。原有 141 个网格未改；新竹林保留 UV2 风动且逐株贴实际谷坡。林中镜头略抬高、桥头平滑恢复，原开场近镜头保留。
- 静态预览、两档背景和资产检查见 `artifacts/bamboo-valley-review/README.md`。当前仍待用户评价，不把 final 文件名视作认可。

### 美术改动先静态预览、认可后再录像（用户明确要求，2026-11-08）

- 后续先展示静态实机预览，等用户明确满意后，再录制视频检查。不要在尚未认可外观时自动做长时间录像验证。
- 可先完成制作、导入、必要的静态和资产检查；展示后等待用户反馈。记录完成或技术检查通过不能代替用户满意。
'''
text=agents.read_text(encoding='utf-8')
if '### 美术改动先静态预览、认可后再录像' not in text:
    with agents.open('a',encoding='utf-8') as f:f.write(section)
print(root/'static-preview.jpg')
