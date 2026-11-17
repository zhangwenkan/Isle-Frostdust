"""Prepare one native P-H3 still-image pose transfer; does not submit it."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/h3-image-install/probe"
SIZE = (1024, 1024)
PROMPT = """Edit <Picture 1>. Change only the full-body martial artist's pose to the acupoint-strike pose shown in <Picture 2>. The result is one single full-body character sprite, on the same flat green background as Picture 1. Preserve the identity, age, dark spiky long hair, gray cloth headband, face design, large head-to-body ratio, stocky youthful proportions, limb thickness, muted brown-gray ragged sleeveless robe, gray waist sash, brown diagonal strap and belt, forearm and shin wraps, fingerless gloves and open-toed sandals from Picture 1. Preserve its crisp dark contour lines, flat illustrated shading and pixel-art character style.

Picture 2 specifies only the body pose and viewing direction: the chest, waist and hips turn together so the character's back is partly visible; the right leg bends in front toward screen right while the left leg extends diagonally backward; the torso leans forward with balanced support. The right arm reaches horizontally toward screen right, with the index and middle fingers together in an acupoint gesture. The left arm opens naturally backward toward screen left, with its hand open. The head turns toward the pointing fingertips on the right, with the face and gaze still readable in profile. Match the joint directions and front-back overlap in Picture 2, adapted to the shorter, larger-headed body proportions of Picture 1. Keep both complete arms, both legs, both feet and the tips of both hands inside the frame. The robe remains attached to the waist and hangs naturally behind and beside the hips. Retain the original character's own outfit; do not transfer the realistic character, black long coat, boots or hairstyle from Picture 2. Keep the character at approximately the same body scale as Picture 1, with room around the extended hands. No second character, no duplicate limbs, no motion blur, no energy effects, no text or panels."""


def main():
    inputs = OUT / "input"
    for folder in (inputs, OUT / "output", OUT / "user", OUT / "temp", OUT / "logs"):
        folder.mkdir(parents=True, exist_ok=True)
    original = ROOT / "artifacts/acupoint-microsegments-review/reference/user-original.png"
    pose = ROOT / "artifacts/gulong-acupoint-preview/original-render/side/frame_012.png"
    shutil.copy2(original, OUT / "hero-original.png")
    shutil.copy2(pose, inputs / "pose-frame-012.png")
    # One fixed uniform preparation transform; no per-frame body normalization.
    with Image.open(original) as hero:
        hero = hero.convert("RGB")
        background = hero.getpixel((0, 0))
        prepared = hero.resize((448, 896), Image.Resampling.NEAREST)
        canvas = Image.new("RGB", SIZE, background)
        canvas.paste(prepared, (288, 64))
        canvas.save(inputs / "hero-anchor.png")
    (OUT / "prompt.txt").write_text(PROMPT, encoding="utf-8")
    graph = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "p-h3-image_w4a8.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "MiniMaxH3SigmaShift", "inputs": {"model": ["1", 0], "shift_video": 1.0, "shift_audio": 1.0}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "p-h3-image_text_encoder_int8_convrot.safetensors", "type": "minimax", "device": "cpu"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "p-h3-image_vae_int8_convrot.safetensors"}},
        "5": {"class_type": "LoadImage", "inputs": {"image": "hero-anchor.png"}},
        "6": {"class_type": "LoadImage", "inputs": {"image": "pose-frame-012.png"}},
        "7": {"class_type": "PH3ImageConditioning", "inputs": {"clip": ["3", 0], "vae": ["4", 0], "prompt": PROMPT, "width": 1024, "height": 1024, "images.image_1": ["5", 0], "images.image_2": ["6", 0]}},
        "8": {"class_type": "ManualSigmas", "inputs": {"sigmas": "1.0, 0.984753, 0.967905, 0.951688, 0.925372, 0.881923, 0.810083, 0.528718, 0.0"}},
        "9": {"class_type": "BasicGuider", "inputs": {"model": ["2", 0], "conditioning": ["7", 0]}},
        "10": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "11": {"class_type": "RandomNoise", "inputs": {"noise_seed": 42}},
        "12": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["11", 0], "guider": ["9", 0], "sampler": ["10", 0], "sigmas": ["8", 0], "latent_image": ["7", 1]}},
        "13": {"class_type": "VAEDecode", "inputs": {"samples": ["12", 0], "vae": ["4", 0]}},
        "14": {"class_type": "SaveImage", "inputs": {"images": ["13", 0], "filename_prefix": "p_h3_acupoint_frame012"}},
    }
    (OUT / "workflow-api.json").write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    # An editable native Comfy workflow, stripped of the optional upsampler.
    template = json.loads((OUT.parent / "research/p-h3-image_edit.json").read_text(encoding="utf-8"))
    active = {4, 5, 7, 8, 9, 10, 11, 12, 13, 26, 27, 28, 29, 30}
    template["nodes"] = [node for node in template["nodes"] if node["id"] in active]
    template["links"] = [link for link in template["links"] if link[1] in active and link[3] in active]
    template["links"].append([100, 4, 0, 30, 2, "IMAGE"])
    valid_links = {link[0] for link in template["links"]}
    for node in template["nodes"]:
        for port in node.get("inputs", []):
            if port.get("link") not in valid_links:
                port["link"] = None
        for port in node.get("outputs", []):
            port["links"] = [link for link in port.get("links") or [] if link in valid_links]
        values = {
            4: ["hero-anchor.png", "image"], 5: ["pose-frame-012.png", "image"],
            10: [42, "fixed"], 13: ["p_h3_acupoint_frame012"],
            26: ["p-h3-image_w4a8.safetensors", "default"],
            28: ["p-h3-image_text_encoder_int8_convrot.safetensors", "minimax", "cpu"],
            29: ["p-h3-image_vae_int8_convrot.safetensors"], 30: [PROMPT, 1024, 1024],
        }
        if node["id"] in values:
            node["widgets_values"] = values[node["id"]]
        if node["id"] == 4:
            node["outputs"][0]["links"] = [100]
        if node["id"] == 30:
            node["inputs"][2]["link"] = 100
    template["groups"] = []
    template["last_link_id"] = 100
    (OUT / "workflow-ui.json").write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
    record = {"status": "prepared-not-submitted", "model_family": "PrunaAI P-H3-Image, a MiniMax-H3 derivative", "output": [1024, 1024], "frames": 1, "steps": 8, "seed": 42, "original_hero_sha256": hashlib.sha256(original.read_bytes()).hexdigest(), "hero_preparation": {"source_size": [1024, 2048], "uniform_scale": 0.4375, "resized_size": [448, 896], "offset": [288, 64], "resampling": "nearest", "canvas": list(SIZE)}, "pose": str(pose), "limitations": "1024-square is a hardware smoke test below recommended 4/8MP edit sizes; no transparency claim; no prompt upsampler; inspect identity and pose after generation"}
    (OUT / "preparation.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Prepared one 1024x1024 still-image edit; no job submitted.")


if __name__ == "__main__":
    main()
