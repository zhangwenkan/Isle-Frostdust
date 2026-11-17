"""Bounded HTTP range requests, compatible with the existing 256 MiB parts."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import os
import threading
import time
import requests
import urllib3

ROOT = Path("D:/AI/minimax-h3-minimal")
MODEL_ROOT = (ROOT / "ComfyUI_windows_portable/ComfyUI/models").resolve()
network_limit = None
digest = None
copyfileobj = None


def fetch_file(item, workers=2):
    target = (ROOT / item["target"]).resolve()
    if not target.is_relative_to(MODEL_ROOT):
        raise ValueError("Model destination is outside the allowed model directory")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if target.stat().st_size != item["bytes"] or digest(target) != item["sha256"]:
            raise RuntimeError("Existing model failed verification; preserving it")
        print("VERIFIED " + target.name, flush=True)
        return
    prefix = target.with_name(target.name + ".partial")
    prefix_size = prefix.stat().st_size if prefix.exists() else 0
    if prefix_size > item["bytes"]:
        raise RuntimeError("Oversized partial prefix")
    parts_dir = target.with_name(target.name + ".parts")
    parts_dir.mkdir(exist_ok=True)
    ranges = [(start, min(start + 256 * 1024 * 1024, item["bytes"]) - 1)
              for start in range(prefix_size, item["bytes"], 256 * 1024 * 1024)]
    sizes = {start: (parts_dir / f"{start}-{end}.part").stat().st_size
             if (parts_dir / f"{start}-{end}.part").exists() else 0 for start, end in ranges}
    progress = target.with_name(target.name + ".progress.json")
    log_lock = threading.Lock()
    last_log = [0.0]
    stop = threading.Event()

    def record(start, size, force=False):
        with log_lock:
            sizes[start] = size
            if force or time.monotonic() - last_log[0] > 20:
                received = prefix_size + sum(sizes.values())
                progress.write_text(json.dumps({"file": target.name, "received": received,
                    "total": item["bytes"], "mode": "small-http-ranges", "connections": workers}), encoding="utf-8")
                print(f"{target.name}: {received / 1e9:.3f}/{item['bytes'] / 1e9:.3f} GB", flush=True)
                last_log[0] = time.monotonic()

    def fetch_range(pair):
        start, end = pair
        part = parts_dir / f"{start}-{end}.part"
        expected = end - start + 1
        failures = 0
        try:
            while True:
                if stop.is_set():
                    raise RuntimeError("Transfer stopped after another connection failed")
                size = part.stat().st_size if part.exists() else 0
                if size == expected:
                    return part
                if size > expected:
                    raise RuntimeError("Oversized existing fragment; preserving it")
                offset = start + size
                request_end = min(offset + 4 * 1024 * 1024 - 1, end)
                url = item["url"] + f"?part={offset}&v={time.time_ns()}"
                try:
                    with requests.get(url, headers={"Range": f"bytes={offset}-{request_end}",
                                      "Accept-Encoding": "identity"}, timeout=(10, 20), stream=True) as response:
                        response.raise_for_status()
                        expected_range = f"bytes {offset}-{request_end}/{item['bytes']}"
                        if response.status_code != 206 or response.headers.get("Content-Range") != expected_range:
                            raise RuntimeError("Server did not return the exact requested byte range")
                        remaining = request_end - offset + 1
                        with part.open("ab", buffering=0) as output:
                            while remaining:
                                if stop.is_set():
                                    raise RuntimeError("Transfer stopped")
                                amount = min(64 * 1024, remaining)
                                network_limit.wait(amount)
                                data = response.raw.read(amount)
                                if not data:
                                    raise OSError("Incomplete HTTP range")
                                output.write(data)
                                remaining -= len(data)
                                size += len(data)
                                record(start, size)
                    failures = 0
                except (OSError, requests.RequestException, urllib3.exceptions.HTTPError) as exc:
                    failures += 1
                    print(f"RETRY {target.name} offset {offset}: {type(exc).__name__} ({failures}/12)", flush=True)
                    if failures >= 12:
                        raise
                    stop.wait(min(2 * failures, 20))
        except BaseException:
            stop.set()
            raise

    if ranges:
        record(ranges[0][0], sizes[ranges[0][0]], True)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        parts = list(executor.map(fetch_range, ranges))
    assembled = target.with_name(target.name + ".assembling")
    print("ASSEMBLING " + target.name + " (I/O limited)", flush=True)
    with assembled.open("wb") as output:
        if prefix_size:
            with prefix.open("rb") as source:
                copyfileobj(source, output)
        for part in parts:
            with part.open("rb") as source:
                copyfileobj(source, output)
    print("VERIFYING SHA256 " + target.name + " (I/O limited)", flush=True)
    if assembled.stat().st_size != item["bytes"] or digest(assembled) != item["sha256"]:
        raise RuntimeError("Assembled model failed SHA256; fragments preserved")
    os.replace(assembled, target)
    progress.write_text(json.dumps({"file": target.name, "status": "verified", "bytes": item["bytes"]}), encoding="utf-8")
    for part in parts + ([prefix] if prefix_size else []):
        if not part.resolve().is_relative_to(MODEL_ROOT):
            raise RuntimeError("Unexpected fragment path; refusing cleanup")
        part.unlink()
    if not any(parts_dir.iterdir()):
        parts_dir.rmdir()
    print("VERIFIED " + target.name, flush=True)
