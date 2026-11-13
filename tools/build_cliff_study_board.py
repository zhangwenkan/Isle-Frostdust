"""Present original reference evidence; never label these as our delivered game art."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,collections
R=Path(__file__).resolve().parents[1];O=R/'artifacts/wandering-cliff-study'
S=Path('D:/Y 逸jian风yun决 v1.23.26 全DLC xg器/WanderingSword/analysis/12_followup/20261109-bamboo-scene')
font='C:/Windows/Fonts/msyh.ttc'
def f(n):return ImageFont.truetype(font,n)
def base(w,h,title,sub):
 im=Image.new('RGB',(w,h),(235,237,231));d=ImageDraw.Draw(im);d.text((28,18),title,font=f(28),fill=(34,45,41));d.text((28,60),sub,font=f(17),fill=(72,81,75));return im,d
im,d=base(1440,770,'《逸剑风云决》真实岸岩：体块与色图分别承担什么','原资产 SM_XYNJiangnan017 · Blender 独立研究渲染，光照为近似；不是原游戏实机，也不是本项目新模型')
for x,name,title in [(20,'geometry','去掉贴图：竖向断面、缺口、局部岩肩仍然存在'),(730,'textured','原模型＋原色图：石质、裂隙、苔边补完整')]:
 src=Image.open(O/('original-shore-detail-'+name+'.png')).convert('RGB');src=src.resize((690,552),Image.Resampling.LANCZOS);im.paste(src,(x,140));d.text((x+8,103),title,font=f(21),fill=(42,52,45))
d.text((28,712),'这组材质引用默认平面法线；不能把这里的立体感解释为“再加强法线或粗糙度”。',font=f(21),fill=(43,54,47))
im.save(O/'shore-method-board.jpg',quality=94)
im,d=base(1440,850,'实际差别：岸岩的组织方式，不是横纹换成竖纹','左：官方临水场景局部　右：本项目被用户否定的当前崖壁')
official=Image.open(S/'official/steam-04.jpg').convert('RGB');crop=official.crop((15,386,1350,1000));crop.thumbnail((690,520),Image.Resampling.LANCZOS);im.paste(crop,(20,135))
ours=Image.open(R/'artifacts/coast-unification-review/review-cliff-close.png').convert('RGB');ours=ours.crop((0,280,1280,590));ours.thumbnail((690,400),Image.Resampling.LANCZOS);im.paste(ours,(730,180))
lines=[('原作',20,['宽窄、高低、朝向有变化的岩面相互嵌合。','局部岩台与大岩体连在一起，顶面确实能承托。','草沿沿凹凸断续覆盖，不是一条平整封边。','受光面、背光面和裂缝有不同层级。']),('当前失败点',730,['外轮廓与崖面过于齐整，像整圈围墙。','三四道横线贯穿全段，几乎没有结构主次。','石质只剩大片平色与装饰裂线。','把横条改成重复竖条，也仍然是同一个问题。'])]
for title,x,ls in lines:
 d.text((x+8,525),title,font=f(25),fill=(36,48,41))
 for j,t in enumerate(ls):d.text((x+8,575+j*47),t,font=f(21),fill=(53,63,55))
im.save(O/'official-and-rejected-comparison.jpg',quality=94)
atlas=Image.open(S/'exports/JH/MapEditor/NewCliff/Textures/T_XuanyaNew001.png').convert('RGB');overlay=Image.new('RGBA',atlas.size);od=ImageDraw.Draw(overlay)
for poly in json.loads((O/'shore-detail-uv.json').read_text()):
 pts=[(p[0]*atlas.width,(1-p[1])*atlas.height) for p in poly];od.line(pts+[pts[0]],fill=(236,206,97,70),width=1)
Image.alpha_composite(atlas.convert('RGBA'),overlay).convert('RGB').resize((1200,1200)).save(O/'original-shore-uv-atlas.jpg',quality=94)
placement=json.loads((S/'placements.json').read_text(encoding='utf8'))
e=json.loads((O/'shore-rock-evidence.json').read_text())
for item in e:item['instances_in_LV_34_S2']=sum(r['package'].endswith('/'+item['name']+'.uasset') for r in placement)
(O/'shore-rock-evidence.json').write_text(json.dumps(e,ensure_ascii=False,indent=2),encoding='utf8')
checks=[]
for p in ['assets/island_blender/nameless_island.blend','assets/island_blender/nameless_island.glb','scripts/colored_ink_sample.gd']:
 a=R/p;b=R/'artifacts/shore-facets-review/backup'/a.name
 h=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
 checks.append(dict(path=p,sha256=h(a),same_as_before_trial=h(a)==h(b)))
assert all(c['same_as_before_trial'] for c in checks)
(O/'restored-source-hashes.json').write_text(json.dumps(checks,indent=2),encoding='utf8')
print('BOARDS_AND_ROLLBACK_EVIDENCE_WRITTEN')
