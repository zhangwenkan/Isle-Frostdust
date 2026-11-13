"""Interrupt only this batch's owned ComfyUI job to relieve measured RAM pressure."""
from pathlib import Path
import argparse
import sys
import time
import urllib.request

RUNTIME=Path('D:/AI/minimax-h3-minimal')
BATCH=RUNTIME/'action-batches/rest-rise-cinematic-ref-20261108'
parser=argparse.ArgumentParser()
parser.add_argument('--revision2',action='store_true')
args=parser.parse_args()
if args.revision2:
    BATCH=RUNTIME/'action-batches/rest-rise-cinematic-ref-20261108-compact-v2'
sys.path.insert(0,str(RUNTIME/'walk-kit/scripts'))
import h3_walk as service

manifest=service.read(BATCH/'batch.json')
job=service.read(BATCH/'job.json')
assert service.own_server(RUNTIME,manifest),'Server not owned by this batch'
queue=service.api('/queue')
assert not queue['queue_pending'],'Other queued work exists'
running=queue['queue_running']
assert len(running)==1 and running[0][1]==job['prompt_id'],'Unexpected running task'
request=urllib.request.Request(service.URL+'/interrupt',data=b'{}',headers={'Content-Type':'application/json'})
with urllib.request.urlopen(request,timeout=30) as response:
    assert response.status==200
print('Interrupt requested for '+job['prompt_id'],flush=True)
for _ in range(90):
    if not service.alive():
        print('Owned service stopped.',flush=True)
        break
    queue=service.api('/queue')
    if not queue['queue_running'] and not queue['queue_pending']:
        print('Job no longer running; original runner handles service shutdown.',flush=True)
        break
    time.sleep(2)
else:
    raise RuntimeError('Interrupt still pending; do not start a second task.')
