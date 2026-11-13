"""Import the reviewed green-screen H3 batch into one native-size Godot resource."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch", type=Path)
    args = parser.parse_args()
    project = Path(__file__).resolve().parents[1]
    output = project / "assets/characters/green_three_walk"
    output.mkdir(parents=True, exist_ok=True)
    resource_root = "res://assets/characters/green_three_walk"
    textures, resources, animations = [], [], []
    manifest = {"source_batch": str(args.batch.resolve()), "frame_size": [512, 768],
                "fps": 24, "foot_bottom_edge": 724, "pixel_size": 0.0037,
                "sprite_offset": [0, 340], "directions": {}}
    for direction, suffix in [("right", "right"), ("back", "up"), ("front", "down")]:
        review = args.batch / direction / "review"
        record = json.loads((review / "export.json").read_text(encoding="utf8"))
        job = json.loads((args.batch / direction / "job.json").read_text(encoding="utf8"))
        assert job["result"]["status"]["status_str"] == "success"
        assert record["frame_size"] == [512, 768] and record["fps"] == 24
        sheets, atlas_records = [], []
        for page, name in enumerate(record["atlases"]):
            target_name = f"{suffix}_{page:02}.png"
            target = output / target_name
            shutil.copy2(review / name, target)
            assert sha(target) == sha(review / name)
            sheets.append(Image.open(target).convert("RGBA"))
            textures.append(f'[ext_resource type="Texture2D" path="{resource_root}/{target_name}" id="{suffix}_{page}"]')
            atlas_records.append({"path": target_name, "sha256": sha(target)})
        frame_lines, hashes = [], []
        for index in range(record["frame_count"]):
            source_frame = review / "cycle_png" / f"frame_{index:03}.png"
            frame = Image.open(source_frame).convert("RGBA")
            page, local = divmod(index, 16)
            x, y = local % 4 * 512, local // 4 * 768
            assert frame.size == (512, 768) and frame.getbbox()[3] == 724
            assert sheets[page].crop((x, y, x + 512, y + 768)).tobytes() == frame.tobytes()
            rid = f"{suffix}_{index}"
            resources.append(f'[sub_resource type="AtlasTexture" id="{rid}"]\natlas = ExtResource("{suffix}_{page}")\nregion = Rect2({x}, {y}, 512, 768)\n')
            frame_lines.append(f'{{"duration": 1.0, "texture": SubResource("{rid}")}}')
            hashes.append(sha(source_frame))
        animations.append('{"frames": [' + ',\n'.join(frame_lines) +
                          f'], "loop": true, "name": &"walk_{suffix}", "speed": 24.0}}')
        reference = Image.open(args.batch / direction / "reference-transparent.png").convert("RGBA")
        dy = 724 - reference.getbbox()[3]
        idle = Image.new("RGBA", reference.size)
        idle.paste(reference, (0, dy))
        reverse = Image.new("RGBA", reference.size)
        reverse.paste(idle, (0, -dy))
        assert reference.tobytes() == reverse.tobytes()
        assert idle.getbbox()[3] == 724
        idle_name = f"{suffix}_idle.png"
        idle.save(output / idle_name)
        textures.append(f'[ext_resource type="Texture2D" path="{resource_root}/{idle_name}" id="idle_{suffix}"]')
        animations.append(f'{{"frames": [{{"duration": 1.0, "texture": ExtResource("idle_{suffix}")}}], "loop": false, "name": &"idle_{suffix}", "speed": 1.0}}')
        manifest["directions"][suffix] = {"source_direction": direction, "prompt_id": job["prompt_id"],
            "frame_count": record["frame_count"], "source_indices": record["source_indices"],
            "source_png_sha256": hashes, "atlases": atlas_records, "idle": idle_name, "idle_dy": dy}
    header = f'[gd_resource type="SpriteFrames" load_steps={1 + len(textures) + len(resources)} format=3]\n\n'
    text = header + '\n'.join(textures) + '\n\n' + '\n'.join(resources)
    text += '\n[resource]\nanimations = [' + ',\n'.join(animations) + ']\n'
    (output / "swordsman_walk.tres").write_text(text, encoding="utf8")
    manifest["processing"] = "Walk atlas bytes copied unchanged; standing references translated only. No resizing or retiming."
    (output / "source.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf8")
    # Prevent automatic 3D texture compression/mipmaps from softening sprite pixels.
    for texture in output.glob("*.png"):
        settings = texture.with_suffix(".png.import")
        if not settings.exists():
            settings.write_text('[remap]\n\nimporter="texture"\ntype="CompressedTexture2D"\n\n'
                f'[deps]\n\nsource_file="{resource_root}/{texture.name}"\n\n'
                '[params]\n\ncompress/mode=0\nmipmaps/generate=false\nprocess/fix_alpha_border=true\n'
                'process/premult_alpha=false\nprocess/size_limit=0\ndetect_3d/compress_to=0\n', encoding="utf8")
    print("Imported right/up/down: 26/29/24 frames at 24fps; 79 exact atlas frames, 3 standing references.")


if __name__ == "__main__":
    main()
