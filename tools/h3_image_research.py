"""Read public H3 image model metadata; save provenance for local installation."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import requests

OUT = Path(__file__).resolve().parents[1] / "artifacts/h3-image-install/research"
REPOS = ["PrunaAI/P-H3-Image-Comfy", "Comfy-Org/MiniMax-H3-Image", "Abiray/MiniMax-H3-Image-GGUF"]


def inspect(repo):
    response = requests.get(f"https://huggingface.co/api/models/{repo}", params={"blobs": "true"}, timeout=25)
    response.raise_for_status()
    metadata = response.json()
    revision = metadata["sha"]
    stem = repo.replace("/", "--")
    (OUT / f"{stem}.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    readme = requests.get(f"https://huggingface.co/{repo}/resolve/{revision}/README.md", timeout=25)
    readme.raise_for_status()
    (OUT / f"{stem}.md").write_text(readme.text, encoding="utf-8")
    files = [{"path": f["rfilename"], "size": f.get("size"), "sha256": f.get("lfs", {}).get("sha256")} for f in metadata["siblings"] if f["rfilename"].endswith((".gguf", ".safetensors", ".json"))]
    return {"repo": repo, "revision": revision, "files": files}


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    response = requests.get("https://huggingface.co/api/models", params={"search": "h3-image", "limit": 60}, timeout=25)
    response.raise_for_status()
    search = response.json()
    (OUT / "search.json").write_text(json.dumps(search, indent=2), encoding="utf-8")
    print(json.dumps({"models": [m["id"] for m in search]}))
    with ThreadPoolExecutor(3) as executor:
        for result in executor.map(inspect, REPOS):
            print(json.dumps(result), flush=True)
