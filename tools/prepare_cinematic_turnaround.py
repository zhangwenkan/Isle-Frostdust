"""Remove only connected checkerboard background and crop the user's turnaround."""
from pathlib import Path
import hashlib
import json

import cv2
import numpy as np
from PIL import Image

SOURCE=Path('C:/Users/51440/Downloads/右侧像素角色对齐透明背景.png')
OUT=Path(__file__).resolve().parents[1]/'artifacts/cinematic-rest-rise-review/references'
OUT.mkdir(exist_ok=True)
source=Image.open(SOURCE).convert('RGB')
rgb=np.array(source)
wide=rgb.astype(np.int16)
candidate=(wide.min(axis=2)>=180)&((wide.max(axis=2)-wide.min(axis=2))<=20)
count,labels,stats,centers=cv2.connectedComponentsWithStats(candidate.astype(np.uint8),8)
border_labels=np.unique(np.concatenate([labels[0],labels[-1],labels[:,0],labels[:,-1]]))
border_labels=border_labels[border_labels!=0]
background=np.isin(labels,border_labels)
alpha=np.where(background,0,255).astype(np.uint8)
rgba=np.dstack([rgb,alpha])
rgba[background,:3]=0
image=Image.fromarray(rgba)
image.save(OUT/'turnaround-transparent.png')
# Uniform 1/2 resize after crop and equal padding; all character pixels retain their relative positions.
cropped=image.crop((0,420,1024,1572))
canvas=Image.new('RGBA',(1088,1216))
canvas.paste(cropped,(32,32))
compact=canvas.resize((544,608),Image.Resampling.NEAREST)
compact.save(OUT/'turnaround-compact-transparent.png')
matte=Image.new('RGBA',compact.size,(160,165,161,255))
matte.alpha_composite(compact)
matte.convert('RGB').save(OUT/'turnaround-compact-reference.png')
full=Image.new('RGBA',canvas.size,(160,165,161,255));full.alpha_composite(canvas)
full.convert('RGB').save(OUT/'turnaround-clean-review.png')
report={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'source_mode':source.mode,'source_size':source.size,'actual_source_alpha':False,
        'background_rule':'near-neutral light pixels connected to image border; enclosed eyes preserved',
        'background_removed_pixels':int(background.sum()),'opaque_rgb_exact':bool(np.array_equal(rgba[~background,:3],rgb[~background])),
        'crop':[0,420,1024,1572],'padding':32,'uniform_reference_scale':0.5,'reference_size':[544,608],
        'identity_views':'left back, middle front, right side; SAME character',
        'reference_latent_tokens':544*608//256,'previous_reference_latent_tokens':3*384*576//256}
(OUT/'turnaround-source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=True))
