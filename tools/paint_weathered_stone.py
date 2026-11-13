"""Quiet stone pigment; localized relief is authored in Blender, not painted as scratches."""
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/colored_ink_sample'
S=512;y,x=np.mgrid[0:S,0:S].astype(float)/S
wash=1.1*np.exp(-((x-.34)**2/.22+(y-.38)**2/.28))-.8*np.exp(-((x-.76)**2/.25+(y-.70)**2/.24))
rgb=np.uint8(np.clip(np.array([142,153,146])+wash[:,:,None],0,255))
tile=Image.fromarray(rgb);atlas=Image.new('RGB',(S*4,S*4))
for i in range(16):atlas.paste(tile,((i%4)*S,(i//4)*S))
atlas.save(OUT/'rock_weathered_base.png')
print(OUT/'rock_weathered_base.png')
