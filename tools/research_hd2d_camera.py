"""Read public sources for the character/camera study, without changing game files."""
import json,sys,requests
from pathlib import Path
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]/'artifacts/hd2d-character-camera-study'

def search(args):
    key,query=args
    r=requests.get('https://www.baidu.com/s',params={'wd':query},timeout=30)
    s=BeautifulSoup(r.content,'html.parser')
    results=[]
    for node in s.select('div.result, div.c-container'):
        a=node.select_one('h3 a')
        if a:results.append({'title':a.get_text(' ',strip=True),'url':a.get('href'),'text':node.get_text(' ',strip=True)})
    (ROOT/'sources'/f'{key}.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
    return key,results

def main():
    terms=[('octopath-unreal','八方旅人 虚幻 引擎 摄像机 透视 开发'),
           ('octopath-tech','Octopath Traveler Unreal Engine camera perspective developer interview'),
           ('sword-camera','逸剑风云决 制作人 摄像机 镜头 3D 像素'),
           ('sword-ciga','逸剑风云决 吴迪 CiGA 开发者大会 2024')]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for key,result in pool.map(search,terms):
            print(key,json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
