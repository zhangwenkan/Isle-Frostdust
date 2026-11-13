"""Build local research evidence from inspected cooked assets; no game edits."""
from pathlib import Path
import json
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1] / "artifacts/wandering-sword-local-study"
FONT = "C:/Windows/Fonts/msyh.ttc"


def font(size):
    return ImageFont.truetype(FONT, size)


def dump(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf8")


def simple(value):
    if isinstance(value, list):
        return [simple(x) for x in value]
    if not isinstance(value, dict):
        return value
    if "Name" in value and ("Value" in value or "EnumValue" in value):
        data = value.get("Value", value.get("EnumValue"))
        if isinstance(data, list) and "ArrayPropertyData" not in value.get("$type", ""):
            return {p["Name"]: simple(p) for p in data}
        return simple(data)
    return {k: simple(v) for k, v in value.items() if k != "$type"}


def properties(export):
    return {p["Name"]: simple(p) for p in export.get("Data", [])}


def contact_sheet():
    atlas = Image.open(ROOT / "texture-preview/JH/Characters/TongYong/Hero/Sprite/role01.png").convert("RGBA")
    summary = json.loads((ROOT / "animation-summary.json").read_text(encoding="utf8"))
    sheet = Image.new("RGB", (1060, 904), "#edf0ed")
    draw = ImageDraw.Draw(sheet)
    draw.text((28, 18), "《逸剑风云决》主角移动：四方向，每方向 6 帧", font=font(28), fill="#233e3b")
    draw.text((28, 62), "实际 PaperFlipbook 资源 · 默认 10 fps · 原像素最近邻放大 4 倍", font=font(19), fill="#526661")
    for row, (key, label) in enumerate([("L", "向左"), ("D", "向下"), ("U", "向上"), ("R", "向右")]):
        animation = next(x for x in summary if x["asset"] == f"PFB_TY_Hero_R_{key}.uasset.json")
        assert animation["keys"] == 6 and animation["fps"] == 10
        top = 108 + row * 184
        draw.text((28, top + 62), label, font=font(24), fill="#233e3b")
        for col, frame in enumerate(animation["frames"]):
            sprite = int(frame["sprite"].rsplit("_", 1)[1])
            sx, sy = sprite % 6 * 26, sprite // 6 * 38
            tile = atlas.crop((sx, sy, sx + 26, sy + 38)).resize((104, 152), Image.Resampling.NEAREST)
            left = 126 + col * 150
            draw.rounded_rectangle((left, top, left + 136, top + 176), radius=5, fill="#dce2de")
            sheet.paste(tile, (left + 16, top + 4), tile)
            draw.text((left + 61, top + 150), str(col + 1), font=font(17), fill="#526661")
    draw.text((28, 859), "帧数 ≠ 方向数；默认资源速度不等于所有情境下的运行时速度。仅供本地研究。", font=font(18), fill="#526661")
    sheet.save(ROOT / "hero-walk-six-frames.png")


def compact_evidence():
    maps = json.loads((ROOT / "map-camera-summary.json").read_text(encoding="utf8"))
    selected = []
    names = {"LV_34_S2.umap.json": "竹海", "LV_32_S2.umap.json": "姑苏城", "LV_32_SN.umap.json": "姑苏城夜景", "LV_52THL_S1.umap.json": "桃花林", "Map_58Zizhuling_S1.umap.json": "紫竹林", "LV_WuDang_S.umap.json": "武当"}
    for item in maps:
        if item["map"] not in names:
            continue
        record = {"map": item["map"], "name": names[item["map"]], "camera_bounds": [], "postprocess": []}
        for obj in item["objects"]:
            data = obj["data"]
            if obj["class"] == "JHCameraBlockingVolume":
                record["camera_bounds"].append({"object": obj["name"], "direction": data.get("LockDirection", "inherited/default; not explicitly serialized")})
            if obj["class"] == "JHPostProcessVolume":
                record["postprocess"].append({"object": obj["name"], "unbound": data.get("bUnbound"), "settings": {k: v for k, v in data.get("Settings", {}).items() if "DepthOfField" in k}})
        selected.append(record)
    dump("map-evidence-compact.json", selected)
    geometry = []
    for source in json.loads((ROOT / "geometry-selection.json").read_text(encoding="utf8")):
        path = ROOT / "json" / (source + ".json")
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf8"))
        for export in data["Exports"]:
            if "BodySetup" not in str(export.get("ObjectName")):
                continue
            props = properties(export)
            ag = props.get("AggGeom", {})
            entry = {"source": source, "collision_trace_flag": props.get("CollisionTraceFlag", "inherited/default"), "primitive_counts": {k: len(v) for k, v in ag.items() if isinstance(v, list)}}
            if "SM_muqiao001" in source:
                entry["boxes"] = ag.get("BoxElems", [])
            geometry.append(entry)
    dump("geometry-evidence-compact.json", geometry)
    cameras = []
    for name in ["BP_SceneHero.uasset.json", "BP_StartMapHero.uasset.json"]:
        path = next((ROOT / "json").rglob(name))
        data = json.loads(path.read_text(encoding="utf8"))
        for export in data["Exports"]:
            if export.get("ObjectName") in ["TopDownCamera", "CameraBoom", "CharMoveComp", "Sprite0"]:
                cameras.append({"source": str(path.relative_to(ROOT)), "object": export["ObjectName"], "properties": properties(export)})
    dump("hero-camera-evidence-compact.json", cameras)


def load_gltf(path):
    data = json.loads(path.read_text(encoding="utf8"))
    buffers = [(path.parent / b["uri"]).read_bytes() for b in data["buffers"]]
    def accessor(index):
        a = data["accessors"][index]
        b = data["bufferViews"][a["bufferView"]]
        dtype = {5126: "<f4", 5123: "<u2", 5125: "<u4"}[a["componentType"]]
        width = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[a["type"]]
        stride = b.get("byteStride", np.dtype(dtype).itemsize * width)
        return np.ndarray((a["count"], width), dtype=dtype, buffer=buffers[b["buffer"]], offset=b.get("byteOffset", 0) + a.get("byteOffset", 0), strides=(stride, np.dtype(dtype).itemsize)).copy()
    chunks = []
    for mesh in data["meshes"]:
        for primitive in mesh["primitives"]:
            p = accessor(primitive["attributes"]["POSITION"])
            i = accessor(primitive["indices"]).reshape(-1, 3)
            chunks.append(p[i])
    return np.concatenate(chunks)


def mesh_sheet():
    canvas = Image.new("RGB", (1280, 1060), "#edf0ed")
    draw = ImageDraw.Draw(canvas)
    draw.text((28, 20), "实际桥梁网格检查", font=font(29), fill="#233e3b")
    draw.text((28, 66), "仅展示原网格结构；灰模为分析预览，不是游戏材质、灯光或实机镜头。", font=font(20), fill="#526661")
    names = ["SM_muqiao001", "SM_gsc_qiao001", "SM_gsc_qiao002", "SM_JN_Xiaoqiao001"]
    labels = ["木桥：3 个盒体（桥面及两侧）", "姑苏桥 001：复杂网格碰撞", "姑苏桥 002：1 个凸碰撞体", "江南小桥：复杂网格碰撞"]
    yaw, pitch = math.radians(38), math.radians(24)
    right = np.array([math.cos(yaw), 0, -math.sin(yaw)])
    toward = np.array([math.sin(yaw)*math.cos(pitch), math.sin(pitch), math.cos(yaw)*math.cos(pitch)])
    up = np.cross(toward, right)
    light = np.array([-0.4, 0.85, 0.35]); light /= np.linalg.norm(light)
    for idx, name in enumerate(names):
        triangles = load_gltf(next((ROOT / "mesh-preview").rglob(name + ".gltf")))
        normal = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
        normal /= np.maximum(np.linalg.norm(normal, axis=1, keepdims=True), 1e-9)
        shade = 0.52 + 0.43 * np.maximum(normal @ light, 0)
        coordinates = np.stack([triangles @ right, -(triangles @ up)], axis=-1)
        bounds_min, bounds_max = coordinates.reshape(-1, 2).min(0), coordinates.reshape(-1, 2).max(0)
        scale = min(554 / (bounds_max[0]-bounds_min[0]), 318 / (bounds_max[1]-bounds_min[1]))
        left, top = 24 + idx % 2 * 630, 116 + idx // 2 * 452
        draw.rounded_rectangle((left, top, left + 602, top + 432), radius=9, fill="#dce2de")
        draw.text((left+16,top+13), labels[idx], font=font(22), fill="#233e3b")
        coordinates = (coordinates - (bounds_max + bounds_min) / 2) * scale + [left + 301, top + 218]
        order = np.argsort((triangles @ toward).mean(1))
        for ti in order:
            shade_color = tuple(int(v*shade[ti]) for v in (159,181,179))
            draw.polygon([tuple(p) for p in coordinates[ti]], fill=shade_color)
        draw.text((left+16,top+398), name, font=font(17), fill="#526661")
    draw.text((28, 1031), "只用于核对桥面、阶梯与拱形结构，不纳入本项目游戏资产。", font=font(17), fill="#526661")
    canvas.save(ROOT / "bridge-geometry-inspection.png")


if __name__ == "__main__":
    compact_evidence()
    contact_sheet()
    mesh_sheet()
    print("Wrote compact evidence, hero contact sheet, bridge mesh inspection.")
