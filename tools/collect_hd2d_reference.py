"""Inspect publisher-provided Steam screenshots and trailer frames locally."""
import json,requests,subprocess,sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageDraw,ImageFont
from bs4 import BeautifulSoup
import imageio_ffmpeg
from urllib.parse import urljoin
import re
sys.stdout.reconfigure(encoding='utf8')
ROOT=Path(__file__).resolve().parents[1]/'artifacts/hd2d-character-camera-study'

def get_game(item):
    name,appid=item
    j=requests.get(f'https://store.steampowered.com/api/appdetails?appids={appid}&l=english',timeout=30).json()[str(appid)]['data']
    (ROOT/'sources'/f'{name}-steam.json').write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf8')
    print(name,BeautifulSoup(j['detailed_description'],'html.parser').get_text(' ',strip=True))
    return name,j

def download_screens(item):
    name,j=item
    folder=ROOT/'reference'/name;folder.mkdir(exist_ok=True)
    for i,s in enumerate(j['screenshots'][:8]):
        p=folder/f'screenshot-{i:02}.jpg'
        if not p.exists():p.write_bytes(requests.get(s['path_full'],timeout=30).content)
    sheet=Image.new('RGB',(1280,4*390),(30,34,37));d=ImageDraw.Draw(sheet)
    for i,p in enumerate(sorted(folder.glob('screenshot-*.jpg'))):
        im=Image.open(p).convert('RGB');im.thumbnail((640,360))
        x=(i%2)*640;y=(i//2)*390
        sheet.paste(im,(x,y+24));d.text((x+10,y+3),f'{name} official screenshot {i}',fill='white')
    sheet.save(ROOT/'reference'/f'{name}-screens.jpg')

def main():
    with ThreadPoolExecutor(max_workers=2) as pool:games=list(pool.map(get_game,[('sword',1876890),('octopath2',1971650)]))
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(download_screens,games))
    for name,j in games:
        movies=j.get('movies',[])
        print(name,'MOVIES',[(x['id'],x['name']) for x in movies])
        movie=next((x for x in movies if x['id']==256933436),movies[0])
        folder=ROOT/'reference'/f'{name}-trailer';folder.mkdir(exist_ok=True)
        (folder/'source.json').write_text(json.dumps(movie,ensure_ascii=False,indent=2),encoding='utf8')
        url=movie.get('hls_h264') or movie.get('mp4',{}).get('480')
        playlist_url=urljoin(url,'hls_264_1_video.m3u8')
        playlist=requests.get(playlist_url,timeout=30).text
        init=re.search(r'#EXT-X-MAP:URI="([^"]+)"',playlist).group(1)
        segments=[line for line in playlist.splitlines() if line and not line.startswith('#')][:20]
        urls=[urljoin(playlist_url,s) for s in [init]+segments]
        def part(u):
            r=requests.get(u,timeout=35);r.raise_for_status();return r.content
        with ThreadPoolExecutor(max_workers=4) as pool:parts=list(pool.map(part,urls))
        clip=folder/'official-excerpt.mp4';clip.write_bytes(b''.join(parts))
        cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(clip),'-t','60','-vf','fps=1/2,scale=800:-1',str(folder/'%03d.jpg')]
        subprocess.run(cmd,check=True,timeout=180)
        frames=sorted(folder.glob('*.jpg'))
        sheet=Image.new('RGB',(1200,((len(frames)+2)//3)*250),(25,30,34));d=ImageDraw.Draw(sheet)
        for i,p in enumerate(frames):
            im=Image.open(p);im.thumbnail((400,225));x=i%3*400;y=i//3*250
            sheet.paste(im,(x,y+22));d.text((x+8,y+3),f'~{i*2:02d}s',fill='white')
        sheet.save(ROOT/'reference'/f'{name}-trailer-contact.jpg')
        print(name,'frames',len(frames))

if __name__=='__main__':main()
