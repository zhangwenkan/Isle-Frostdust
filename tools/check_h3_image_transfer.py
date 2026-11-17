"""Check byte-exact resume and reject an incorrect HTTP range, offline."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import hashlib
import io
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h3_image_transfer as transfer

workspace = Path(__file__).resolve().parents[1]
payload = bytes(range(256)) * 1024


class NoDelay:
    def wait(self, count):
        pass


class Response:
    def __init__(self, start, end, wrong=False):
        self.status_code = 206
        self.headers = {"Content-Range": f"bytes {0 if wrong else start}-{end}/{len(payload)}"}
        self.raw = io.BytesIO(payload[start:end + 1])

    def raise_for_status(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


with TemporaryDirectory(prefix="transfer-check-", dir=workspace / "artifacts/h3-image-install") as folder:
    root = Path(folder).resolve()
    assert root.is_relative_to(workspace.resolve())
    transfer.ROOT = transfer.MODEL_ROOT = root
    transfer.network_limit = NoDelay()
    transfer.digest = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
    transfer.copyfileobj = shutil.copyfileobj
    for wrong in (False, True):
        name = "wrong.bin" if wrong else "resume.bin"
        item = {"target": name, "url": "https://offline.invalid/model", "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
        parts = root / (name + ".parts")
        parts.mkdir()
        part = parts / f"0-{len(payload) - 1}.part"
        part.write_bytes(payload[:12345])
        requests = []

        def get(url, headers, **kwargs):
            start, end = map(int, headers["Range"].removeprefix("bytes=").split("-"))
            requests.append((start, end))
            return Response(start, end, wrong)

        with patch.object(transfer.requests, "get", get):
            if wrong:
                try:
                    transfer.fetch_file(item, workers=2)
                    raise AssertionError("Wrong Content-Range was accepted")
                except RuntimeError as exc:
                    assert "exact requested byte range" in str(exc)
                assert part.read_bytes() == payload[:12345]
                assert not (root / name).exists()
            else:
                transfer.fetch_file(item, workers=2)
                assert (root / name).read_bytes() == payload
                assert requests == [(12345, len(payload) - 1)]
print("PASS: exact-byte resume, final checksum, and invalid-range rejection preserving original fragment")
