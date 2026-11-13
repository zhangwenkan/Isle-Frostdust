"""Paint auxiliary 2D surface normals for the three existing standing drawings.

This creates textures only, not geometry. Anatomical regions are explicitly
placed on each drawing; source colors, alpha, scale and pose are never changed.
"""
from pathlib import Path
import json
import hashlib
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets/characters/green_three_walk'
DEST = ROOT / 'assets/characters/standing_surface'
REVIEW = ROOT / 'artifacts/hero-standing-light-review'

# Each tuple: name, center x/y, radius x/y, curvature x/y, forward-facing bias.
# These describe painted surface directions on a 2D reference, not 3D meshes.
REGIONS = {
    'down': [
        ('robe',255,460,105,164,.80,.27,0),
        ('chest',255,294,69,72,.88,.48,0),
        ('left_shoulder',188,263,31,32,.83,.90,0),
        ('right_shoulder',322,263,31,32,.83,.90,0),
        ('left_arm',171,318,24,45,.87,.28,0),
        ('right_arm',336,318,24,45,.87,.28,0),
        ('left_forearm',161,393,23,48,.84,.23,0),
        ('right_forearm',348,393,23,48,.84,.23,0),
        ('left_hand',165,449,23,25,.76,.51,0),
        ('right_hand',347,449,23,25,.76,.51,0),
        ('left_thigh',213,566,29,48,.86,.30,0),
        ('right_thigh',296,566,29,48,.86,.30,0),
        ('left_calf',207,642,25,51,.88,.25,0),
        ('right_calf',304,642,25,51,.88,.25,0),
        ('left_foot',198,697,34,25,.72,.73,.24),
        ('right_foot',314,697,34,25,.72,.73,.24),
        ('hair_back',255,211,77,83,.73,.46,0),
        ('head',255,129,79,82,.83,.92,0),
        ('neck',255,230,23,29,.70,.32,0),
        ('face',255,174,49,44,.58,.48,0),
    ],
    'right': [
        ('robe',270,462,79,160,.74,.25,0),
        ('far_leg',287,579,24,47,.81,.30,0),
        ('far_calf',289,638,23,46,.83,.25,0),
        ('far_foot',308,686,33,22,.72,.68,.25),
        ('chest',291,294,50,71,.84,.49,0),
        ('far_arm',333,402,17,51,.76,.22,0),
        ('far_hand',337,439,16,22,.72,.48,0),
        ('hair_back',225,252,56,117,.80,.35,0),
        ('head',270,127,75,81,.84,.94,0),
        ('neck',283,219,25,27,.77,.35,0),
        ('face',304,183,34,42,.62,.42,0),
        ('shoulder',243,274,33,34,.89,.91,0),
        ('arm',242,321,26,43,.89,.27,0),
        ('forearm',250,395,24,47,.86,.25,0),
        ('hand',257,449,24,23,.76,.52,0),
        ('thigh',250,565,32,42,.88,.30,0),
        ('calf',246,636,27,47,.89,.23,0),
        ('foot',269,699,47,24,.76,.69,.26),
    ],
    'up': [
        ('robe',255,464,104,161,.81,.26,0),
        ('back',255,294,73,78,.88,.52,0),
        ('left_shoulder',187,264,32,34,.86,.91,0),
        ('right_shoulder',324,264,32,34,.86,.91,0),
        ('left_arm',172,319,24,46,.88,.27,0),
        ('right_arm',338,319,24,46,.88,.27,0),
        ('left_forearm',162,392,24,48,.85,.23,0),
        ('right_forearm',349,392,24,48,.85,.23,0),
        ('left_hand',168,451,24,25,.75,.50,0),
        ('right_hand',345,451,24,25,.75,.50,0),
        ('left_thigh',213,571,29,47,.86,.28,0),
        ('right_thigh',294,571,29,47,.86,.28,0),
        ('left_calf',208,644,25,49,.88,.23,0),
        ('right_calf',301,644,25,49,.88,.23,0),
        ('left_foot',201,701,32,22,.70,.72,.22),
        ('right_foot',308,701,32,22,.70,.72,.22),
        ('hair_back',255,231,61,100,.81,.48,0),
        ('head',255,132,80,84,.84,.93,0),
        ('pouch',290,395,26,31,.83,.66,0),
    ],
}


def import_settings(path):
    res='res://'+path.relative_to(ROOT).as_posix()
    path.with_suffix('.png.import').write_text('[remap]\nimporter="texture"\ntype="CompressedTexture2D"\n\n[deps]\nsource_file="'+res+'"\n\n[params]\ncompress/mode=0\ncompress/normal_map=2\nmipmaps/generate=false\nprocess/fix_alpha_border=false\ndetect_3d/compress_to=0\n',encoding='utf8')


def paint(direction):
    path=SOURCE/f'{direction}_idle.png'
    im=Image.open(path).convert('RGBA')
    pixels=np.asarray(im)
    mask=(pixels[...,3]>90).astype(np.uint8)
    yy,xx=np.mgrid[:im.height,:im.width].astype(float)
    distance=cv2.distanceTransform(mask,cv2.DIST_L2,5)
    # Retain only a faint outer rim from the old silhouette field.
    height=7*(1-np.exp(-distance/18))
    height=cv2.GaussianBlur(height,(0,0),3)
    dy,dx=np.gradient(height)
    n=np.stack([-dx,dy,np.ones_like(dx)],axis=-1)
    n/=np.linalg.norm(n,axis=-1,keepdims=True)
    for name,cx,cy,rx,ry,sx,sy,top_bias in REGIONS[direction]:
        u=(xx-cx)/rx; v=(yy-cy)/ry
        radius=np.sqrt(u*u+v*v)
        weight=np.clip((1.12-radius)/.23,0,1)
        weight=weight*weight*(3-2*weight)
        nx=u*sx; ny=-v*sy+top_bias
        length=np.sqrt(nx*nx+ny*ny)
        safety=np.minimum(1,.96/np.maximum(length,.001))
        nx*=safety; ny*=safety
        nz=np.sqrt(np.maximum(.07,1-nx*nx-ny*ny))
        local=np.stack([nx,ny,nz],axis=-1)
        n=n*(1-weight[...,None])+local*weight[...,None]
    n=cv2.GaussianBlur(n.astype(np.float32),(0,0),1.25)
    n/=np.maximum(np.linalg.norm(n,axis=-1,keepdims=True),.001)
    n[mask==0]=[0,0,1]
    normal=Image.fromarray(np.rint((n*.5+.5)*255).clip(0,255).astype(np.uint8),'RGB')
    normal_path=DEST/f'{direction}_idle_normal.png'
    normal.save(normal_path);import_settings(normal_path)
    # Red marks only the opaque outer ink band; interior eye/hair lines stay intact.
    edge=np.clip((3.5-distance)/2.5,0,1)*mask
    support=np.stack([edge,mask.astype(float),np.zeros_like(edge)],axis=-1)
    support_path=DEST/f'{direction}_idle_surface.png'
    Image.fromarray(np.rint(support*255).astype(np.uint8),'RGB').save(support_path)
    import_settings(support_path)
    # Reference-only relighting strip visualizes the direction fields on solid grey.
    views=[]
    for light in [np.array([-.65,.6,.45]),np.array([.65,.6,.45]),np.array([-.32,.67,-.67])]:
        light/=np.linalg.norm(light)
        diffuse=np.maximum(n@light,0)
        shade=.28+.67*diffuse
        rgb=np.repeat((shade*255).astype(np.uint8)[...,None],3,axis=-1)
        rgb[mask==0]=[220,226,220]
        views.append(Image.fromarray(rgb,'RGB'))
    return im,normal,views,{'source':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'regions':REGIONS[direction]}


def main():
    DEST.mkdir(parents=True,exist_ok=True)
    sheet=Image.new('RGB',(5*256,3*384),(220,226,220));manifest=[]
    for row,direction in enumerate(['down','right','up']):
        im,normal,views,info=paint(direction);manifest.append(info)
        images=[im,normal]+views
        for col,img in enumerate(images):
            thumb=img.resize((256,384),Image.Resampling.NEAREST)
            sheet.paste(thumb,(col*256,row*384),thumb if thumb.mode=='RGBA' else None)
    sheet.save(REVIEW/'standing-surface-fields.png')
    (DEST/'source.json').write_text(json.dumps({'purpose':'2D authored body surface directions, not geometry or reconstructed anatomical depth','source_pixels_changed':False,'poses':manifest},ensure_ascii=False,indent=2),encoding='utf8')
    print('Painted three standing surface normal maps; source images unchanged.')


if __name__=='__main__':main()
