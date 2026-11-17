"""Install the pinned P-H3 image weights into the existing local ComfyUI."""
from pathlib import Path
import contextlib
import hashlib
import json
import os
import shutil
import sys
import threading
import time
import urllib.request

PROJECT = Path(__file__).resolve().parents[1]
TASK = PROJECT / "artifacts/h3-image-install"
RUNTIME = Path("D:/AI/minimax-h3-minimal")
MODEL_ROOT = RUNTIME / "ComfyUI_windows_portable/ComfyUI/models"
FILES = [
    "diffusion_models/p-h3-image_w4a8.safetensors",
    "text_encoders/p-h3-image_text_encoder_int8_convrot.safetensors",
    "vae/p-h3-image_vae_int8_convrot.safetensors",
]


class RateLimit:
    def __init__(self, bytes_per_second):
        self.rate = bytes_per_second
        self.next_time = time.monotonic()
        self.lock = threading.Lock()

    def wait(self, count):
        with self.lock:
            now = time.monotonic()
            start = max(now, self.next_time)
            self.next_time = start + count / self.rate
        time.sleep(max(0, start - now))


def low_impact_transfer(module):
    """Bound network buffers, aggregate rate, hashing and assembly I/O."""
    import psutil
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
    network_limit = RateLimit(2 * 1024 * 1024)
    disk_limit = RateLimit(16 * 1024 * 1024)

    def digest_limited(path):
        digest = hashlib.sha256()
        with Path(path).open("rb") as stream:
            while data := stream.read(256 * 1024):
                disk_limit.wait(len(data))
                digest.update(data)
        return digest.hexdigest()

    def copy_limited(source, destination, length=0):
        while data := source.read(256 * 1024):
            disk_limit.wait(len(data))
            destination.write(data)

    module.network_limit = network_limit
    module.digest = digest_limited
    module.copyfileobj = copy_limited


def existing_bytes(items):
    received = 0
    for item in items:
        target = RUNTIME / item["target"]
        if target.exists():
            received += min(target.stat().st_size, item["bytes"])
            continue
        prefix = target.with_name(target.name + ".partial")
        if prefix.exists():
            received += prefix.stat().st_size
        parts = target.with_name(target.name + ".parts")
        if parts.exists():
            received += sum(part.stat().st_size for part in parts.glob("*.part"))
    return received


def main():
    metadata = json.loads((TASK / "research/PrunaAI--P-H3-Image-Comfy.json").read_text(encoding="utf-8"))
    assert metadata["sha"] == "44a0fb73f299da1bb715bdb5ff59ce3fd3c6f543"
    repo = "PrunaAI/P-H3-Image-Comfy"
    entries = {entry["rfilename"]: entry for entry in metadata["siblings"]}
    items = []
    for name in FILES:
        entry = entries[name]
        target = MODEL_ROOT / name
        assert target.resolve().is_relative_to(MODEL_ROOT.resolve())
        items.append({
            "url": f"https://huggingface.co/{repo}/resolve/{metadata['sha']}/{name}",
            "target": target.relative_to(RUNTIME).as_posix(),
            "bytes": entry["size"], "sha256": entry["lfs"]["sha256"],
        })
    manifest_path = TASK / "install-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    manifest.update({"model": "PrunaAI P-H3-Image (MiniMax-H3 derivative)", "revision": metadata["sha"], "files": items, "total_bytes": sum(item["bytes"] for item in items), "prompt_upsampler": "omitted; first test uses an explicit edit prompt"})
    print(f"INSTALL {manifest['total_bytes'] / 1e9:.2f} GB across {len(items)} files", flush=True)
    print(f"EXISTING {existing_bytes(items) / 1e9:.2f} GB (not yet final-hash verified)", flush=True)
    if "--download" not in sys.argv:
        return
    if shutil.disk_usage(MODEL_ROOT).free < manifest["total_bytes"] - existing_bytes(items) + max(item["bytes"] for item in items) + 2_000_000_000:
        raise RuntimeError("Insufficient free disk for checked downloads plus assembly; no existing models removed")
    import msvcrt
    lock_file = (TASK / "download.lock").open("a+b")
    lock_file.seek(0)
    if not lock_file.read(1):
        lock_file.write(b"0")
        lock_file.flush()
    lock_file.seek(0)
    msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
    sys.path.insert(0, str(RUNTIME))
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import h3_image_transfer as download_parallel
    low_impact_transfer(download_parallel)
    manifest["status"] = "downloading"
    manifest.update(pid=os.getpid(), resumed_by_user="2026-11-14", generation_started=False,
                    transfer_limits={"simultaneous_files": 1, "connections": 2, "aggregate_MiB_per_second": 2, "io_MiB_per_second": 16, "priority": "IDLE", "read_buffer_KiB": 256}, received_at_resume=existing_bytes(items))
    manifest.pop("pause_reason", None)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (TASK / "download.pid").write_text(str(os.getpid()), encoding="ascii")
    print("LOW IMPACT: 1 file, 2 connections, total 2 MiB/s cap, IDLE priority; no image generation", flush=True)
    monitor_stop = threading.Event()

    def monitor():
        while not monitor_stop.is_set():
            try:
                received = existing_bytes(items)
                process = __import__("psutil").Process()
                status = {"pid": os.getpid(), "received_bytes": received,
                          "total_bytes": manifest["total_bytes"],
                          "percent": round(received / manifest["total_bytes"] * 100, 2),
                          "rss_bytes": process.memory_info().rss, "updated_unix": time.time()}
                (TASK / "download-status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
            except (OSError, RuntimeError):
                pass
            monitor_stop.wait(15)

    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()
    try:
        for item in items:
            manifest["current_file"] = Path(item["target"]).name
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            download_parallel.fetch_file(item, workers=2)
        manifest["status"] = "installed-sha256-verified"
    except BaseException as exc:
        manifest.update(status="stopped-with-error", error=str(exc))
        raise
    finally:
        monitor_stop.set()
        monitor_thread.join(timeout=2)
        manifest["received_bytes"] = existing_bytes(items)
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        with contextlib.suppress(OSError):
            lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        lock_file.close()
    print("INSTALLED all 3 files with SHA-256 verification", flush=True)


if __name__ == "__main__":
    main()
