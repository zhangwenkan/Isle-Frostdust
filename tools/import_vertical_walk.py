"""Pack the reviewed H3 up/down walks for Godot without resizing any frame."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_root", type=Path, help="Local minimax-h3-minimal directory")
    args = parser.parse_args()
    project = Path(__file__).resolve().parents[1]
    output = project / "assets/characters"
    reviews = args.source_root / "results/walk_front_back_q4_20261107"
    inputs = args.source_root / "walk-tests/front_back_q4_20261107"
    resources, animations, manifest = [], [], {}
    for texture_id, (direction, animation) in enumerate((("back", "up"), ("front", "down")), 1):
        folder = reviews / direction
        review = json.loads((folder / "review.json").read_text(encoding="utf8"))
        cycle = review["cycle"]
        indices = range(cycle["start"], cycle["end_exclusive"])
        paths = [folder / "aligned_png" / f"frame_{i:03}.png" for i in indices]
        frames = [Image.open(path).convert("RGBA") for path in paths]
        reference = Image.open(inputs / direction / "reference-transparent.png").convert("RGBA")
        idle = Image.new("RGBA", (512, 768))
        idle.paste(reference, (0, 724 - reference.getbbox()[3]))
        frames.append(idle)
        rows = (len(frames) + 3) // 4
        atlas = Image.new("RGBA", (2048, rows * 768))
        for index, frame in enumerate(frames):
            assert frame.size == (512, 768) and frame.getbbox()[3] == 724
            x, y = index % 4 * 512, index // 4 * 768
            atlas.paste(frame, (x, y))
            assert atlas.crop((x, y, x + 512, y + 768)).tobytes() == frame.tobytes()
            resources.append(
                f'[sub_resource type="AtlasTexture" id="{animation}_{index}"]\n'
                f'atlas = ExtResource("{texture_id}")\n'
                f'region = Rect2({x}, {y}, 512, 768)\n'
            )
        name = f"swordsman_walk_{animation}.png"
        atlas.save(output / name)
        frame_lines = [f'{{"duration": 1.0, "texture": SubResource("{animation}_{i}")}}' for i in range(len(paths))]
        animations.append('{"frames": [' + ',\n'.join(frame_lines) +
                          f'], "loop": true, "name": &"walk_{animation}", "speed": 24.0}}')
        animations.append('{"frames": [{"duration": 1.0, "texture": SubResource("' +
                          f'{animation}_{len(paths)}' + '")}], "loop": false, "name": &' +
                          f'"idle_{animation}", "speed": 1.0}}')
        manifest[animation] = {
            "source_job": review["prompt_id"], "source_frames": list(indices),
            "frame_size": [512, 768], "frames": len(paths), "fps": 24,
            "atlas": name, "atlas_sha256": hashlib.sha256((output / name).read_bytes()).hexdigest(),
            "source_png_sha256": [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths],
            "processing": "Exact RGBA atlas packing; no resizing, stretching or interpolation.",
            "idle": "Prepared reference, whole-image integer translation to sole bottom edge y=724.",
        }
    text = f'[gd_resource type="SpriteFrames" load_steps={len(resources) + 3} format=3]\n\n'
    text += '[ext_resource type="Texture2D" path="res://assets/characters/swordsman_walk_up.png" id="1"]\n'
    text += '[ext_resource type="Texture2D" path="res://assets/characters/swordsman_walk_down.png" id="2"]\n\n'
    text += '\n'.join(resources) + '\n[resource]\nanimations = [' + ',\n'.join(animations) + ']\n'
    (output / "swordsman_walk_vertical.tres").write_text(text, encoding="utf8")
    (output / "swordsman_walk_vertical.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf8")
    print("Packed walk_up: 26 frames; walk_down: 25 frames; two standing references; 512 x 768, 24 fps.")


if __name__ == "__main__":
    main()
