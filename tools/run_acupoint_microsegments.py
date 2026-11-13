"""Run exactly the prepared 5/22-frame probes with owned-service cleanup."""
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path('D:/AI/minimax-h3-minimal')
BATCH = ROOT / 'action-batches/acupoint-microsegments-20261109'
sys.path.insert(0, str(ROOT / 'walk-kit/scripts'))
import h3_walk as h3


def manage(root, action):
    subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                    str(BATCH / 'manage_comfy.ps1'), '-Action', action, '-NoCache'], check=True)
    deadline = time.monotonic() + (180 if action == 'Start' else 30)
    while time.monotonic() < deadline:
        if h3.alive() == (action == 'Start'):
            return
        time.sleep(2)
    raise RuntimeError('Service did not reach requested state: ' + action)


def main():
    h3.manage = manage
    manifest_path = BATCH / 'batch.json'
    manifest = h3.read(manifest_path)
    with h3.lock(ROOT):
        try:
            for count in (5, 22):
                manifest.update(status=f'running-probe-{count:02d}')
                h3.save(manifest_path, manifest)
                start = time.monotonic()
                job = h3.submitted_job(BATCH / f'probe-{count:02d}', ROOT, manifest, manifest_path)
                manifest[f'probe_{count:02d}'] = dict(prompt_id=job['prompt_id'], status='generated',
                     wall_seconds=time.monotonic() - start)
                h3.save(manifest_path, manifest)
                print(f'GENERATED {count} frames; original outputs ready', flush=True)
            manifest['status'] = 'generated-awaiting-review'
        except Exception as exc:
            manifest.update(status='stopped', error=str(exc))
            raise
        finally:
            if h3.alive() and h3.own_server(ROOT, manifest):
                h3.empty_queue()
                manage(ROOT, 'Stop')
            for stream in ('stdout', 'stderr'):
                log = ROOT / f'comfy.{stream}.log'
                if log.exists():
                    shutil.copy2(log, BATCH / log.name)
            h3.save(manifest_path, manifest)


if __name__ == '__main__':
    main()
