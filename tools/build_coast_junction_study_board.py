"""Annotate existing evidence images; no generated reference art or geometry."""
from pathlib import Path
import json, hashlib
from PIL import Image, ImageDraw, ImageFont

R=Path(__file__).resolve().parents[1]
O=R/'artifacts/coast-junction-study-20261111'
S=Path('D:/Y 逸jian风yun决 v1.23.26 全DLC xg器/WanderingSword/analysis/12_followup/20261109-bamboo-scene')
FONT='C:/Windows/Fonts/msyh.ttc'
def font(size): return ImageFont.truetype(FONT,size)
def text(draw,xy,value,size=23,fill='#283634'): draw.text(xy,value,font=font(size),fill=fill,spacing=10)
def fitted(path,size,crop=None):
    im=Image.open(path).convert('RGB')
    if crop: im=im.crop(crop)
    im.thumbnail(size,Image.Resampling.LANCZOS)
    return im

board=Image.new('RGB',(1420,1060),'#f0eee5');d=ImageDraw.Draw(board)
text(d,(28,18),'《逸剑》草地—岩顶—断面：保留体积，组织接合',32)
text(d,(28,66),'上：官方画面局部。下：原关卡网格与摆放的 Blender 检查；受光和材质近似，非原游戏实机。',19)
official=fitted(S/'official/steam-04.jpg',(930,385),(470,310,1430,690));board.paste(official,(28,108))
for box,label in [((310,75,600,175),'1'),((190,180,430,280),'2'),((680,155,895,265),'3')]:
    x0,y0,x1,y1=box;x0+=28;x1+=28;y0+=108;y1+=108
    d.rectangle((x0,y0,x1,y1),outline='#f1cf75',width=3)
    d.rounded_rectangle((x0,y0,x0+33,y0+34),radius=4,fill='#253b3a')
    text(d,(x0+9,y0+1),label,21,'#fff3cb')
text(d,(990,125),'1  草地并不封满岩顶',25)
text(d,(990,169),'有的地方退后，露出石面；\n有的沿低处接入凹口。',22)
text(d,(990,258),'2  凸起要接回主体',25)
text(d,(990,302),'岩肩有承托与遮挡关系，\n主断面仍清楚可读。',22)
text(d,(990,390),'3  明暗和线条有主次',25)
text(d,(990,434),'少数深断口定结构，\n小裂缝随岩面局部结束。',22)
text(d,(28,530),'原关卡局部｜去掉植物后查看接合',25)
text(d,(730,530),'同一局部｜去掉色图后查看真实体积',25)
board.paste(fitted(O/'original-layout-ground-rock.png',(660,450)),(28,576))
board.paste(fitted(O/'original-layout-clay.png',(660,450)),(730,576))
text(d,(28,1024),'原作同样使用独立模块；连贯感来自摆放、共同走向和接触关系，不以全并成一张网格为前提。',21)
board.save(O/'reference-junction-board.jpg',quality=94)

src=Image.open(R/'artifacts/coast-integration-review/before-after.png').convert('RGB')
diag=Image.new('RGB',(1340,1110),'#f0eee5');dd=ImageDraw.Draw(diag)
text(dd,(30,18),'本项目退步在哪：形体被填浅，线条未跟着结构走',31)
text(dd,(30,72),'修改前｜主断面和岩肩清楚，但拼块与草皮盖板感明显',24)
diag.paste(src.crop((0,49,1280,423)),(30,116))
text(dd,(30,515),'被否定的融合版｜接缝变浅，同时损失了原来可读的层次',24)
diag.paste(src.crop((0,481,1280,855)),(30,558))
for box,label in [((40,647,1285,674),'A'),((680,687,990,838),'B'),((470,730,625,849),'C')]:
    dd.rectangle(box,outline='#f1cf75',width=3)
    dd.rounded_rectangle((box[0],box[1],box[0]+34,box[1]+34),radius=3,fill='#253b3a')
    text(dd,(box[0]+8,box[1]+1),label,20,'#fff3cb')
text(dd,(30,957),'A  草岩关系仍集中成窄长边带，缺少宽窄变化的岩顶与露土。',23)
text(dd,(30,1000),'B  外壳填入原断口，部分岩肩被吞；材质又削弱接触明暗。',23)
text(dd,(30,1043),'C  旧局部笔触被裁取、拉成沿岸长图；裂线没有逐面对应新几何。',23)
diag.save(O/'regression-diagnosis.jpg',quality=94)

manifest=json.loads((S/'scene-manifest.json').read_text(encoding='utf8'))
placements=json.loads((S/'placements.json').read_text(encoding='utf8'))
refs=['/Game/JH/Maps/WuDang/Materails/M_Cliff_Base_WuDang_Inst.M_Cliff_Base_WuDang_Inst',
      '/Game/JH/Maps/JiangNan/Common/Material/MI_Ground_JiangNan.MI_Ground_JiangNan',
      '/Game/JH/MapEditor/NewCliff/Materials/MI_Jiangnan/XuanyaNew_jiangnan001.XuanyaNew_jiangnan001']
evidence={'reference_map':manifest['map'], 'materials':{k:manifest['materials'][k] for k in refs},
          'shared_grass_texture':'/Game/JH/Maps/JiangNan/Common/Texture/T_Cao_JN.T_Cao_JN',
          'formula_limit':'Texture references verified; cooked material graph equations not reconstructed.',
          'original_shore_instances':sum('SM_XYNJiangnan017' in p['package'] for p in placements),
          'files_reviewed':['tools/blender/integrate_coastal_mass.py','tools/paint_integrated_coast.py',
                           'shaders/integrated_coastal_rock.gdshader','shaders/ink_sample_ground.gdshader',
                           'shaders/original_coastal_rock.gdshader']}
(O/'material-evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf8')
before=json.loads((O/'formal-baseline-hashes.json').read_text(encoding='utf8'))
after={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in before}
assert before==after,'Formal asset changed during read-only study; investigate.'
(O/'formal-verification.json').write_text(json.dumps({'unchanged':True,'files':after},indent=2),encoding='utf8')
print('Wrote two evidence boards and material evidence; seven formal files unchanged.')
