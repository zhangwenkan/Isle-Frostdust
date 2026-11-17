"""Package the existing original-character pose samples, without resampling."""
from pathlib import Path
import csv
import hashlib
import io
import json
import zipfile

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artifacts/gulong-acupoint-preview"
OUT = ROOT / "artifacts/acupoint-image-route-study"


def main():
    OUT.mkdir(exist_ok=True)
    old = json.loads((SOURCE / "review/original-verification.json").read_text(encoding="utf-8"))
    for record in old["records"]:
        assert hashlib.sha256(Path(record["file"]).read_bytes()).hexdigest() == record["sha256"]
    rows = []
    members = []
    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 17)
    for view in ("side", "three-quarter"):
        board = Image.new("RGB", (1280, 2272), "#202a35")
        draw = ImageDraw.Draw(board)
        for index in range(32):
            src = SOURCE / "original-render" / view / f"frame_{index:03d}.png"
            data = src.read_bytes()
            name = f"{view}/{src.name}"
            members.append((name, data))
            with Image.open(src) as im:
                assert im.size == (960, 768)
                im.load()
                board.paste(im.convert("RGB").resize((320, 256), Image.Resampling.LANCZOS), ((index % 4) * 320, (index // 4) * 284 + 28))
            draw.text(((index % 4) * 320 + 8, (index // 4) * 284 + 5), f"{index:03d}   t={index}/30 s", font=font, fill="white")
            rows.append({"view": view, "frame": index, "time_seconds": f"{index / 30:.9f}", "file": name, "sha256": hashlib.sha256(data).hexdigest()})
        board_path = OUT / f"{view}-all-32-frames.jpg"
        board.save(board_path, quality=94)
        members.append((board_path.name, board_path.read_bytes()))
        # The renderer's extra sample resets to the initial pose. Keep it outside
        # the ordered action sequence so it cannot silently change the timing.
        extra = SOURCE / "original-render" / view / "frame_032.png"
        assert extra.read_bytes() == (SOURCE / "original-render" / view / "frame_000.png").read_bytes()
        members.append((f"extra-reset-frame/{view}-frame_032.png", extra.read_bytes()))
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    members.append(("frame-times-and-hashes.csv", stream.getvalue().encode("utf-8-sig")))
    readme = """# 点穴原角色逐帧参考与图片路线核查

2026-11-13。原对比与无损原图仍在，复核64张采样图与既有记录的SHA-256全部一致。

## 原图

- 原角色：ba026 / 辰雨；原动画：gl_skill_empty_067 / 点穴。
- side/与three-quarter/各32张960×768 PNG，编号000–031，对应0至31/30秒，含两个端点；原动画约1.033秒、采样率30fps。
- 这些图由原模型与原骨骼动画直接定时渲染，不是从压缩视频二次抽取。固定画布与机位，原始像素不改。
- 两个视角是同一动作的不同观察角度，不应混成一条动画。辅助总览是缩略图，生图请使用独立PNG。
- 原渲染另有frame_032.png，与frame_000.png逐字节相同，放在extra-reset-frame/，不算新的动作姿势。
- PNG有深色背景，不是透明图。预览关闭原作物理/布料模拟，不含战斗特效、受击者和镜头。
- 播放应使用30fps。把32张都各显示1/30秒会得到约1.067秒，较端点之间的原动画多一个显示间隔；旧GIF还另加过尾停顿，不能照搬其时长。

## 本机H3生图能力

- 当前ComfyUI源码确有PH3ImageConditioning（p-h3-image）单张生成与多图编辑接口。
- 本机models目录实际为FL2VA/Ref2VA Turbo Q4等视频权重；未发现p-h3-image配套权重。节点存在不等于模型已部署或本机已跑通。
- 视频接口最低5帧并按17k+5格点取长度；不能把设为1帧或生成短视频取一张称为纯生图。
- 本次未下载新模型、未启动生成；纯图片姿态迁移与本机资源需求尚待配置和实测。

## 建议的图片路线

先用原角色的对应姿态帧与用户主角固定参考，分别约束动作和身份；姿态迁移需保留主角自身头身比、肢段长度、服饰和配件，而非照搬原角色体型。

圆柱/方块人体可辅助说明胸腔与骨盆朝向、关节、前后遮挡；但会丢失手指、头脸朝向和衣摆信息，不能保证比原帧更好。若制作，应来自同一套原骨骼动画，保持几何比例与镜头固定，模型制作须遵守Blender MCP要求，不能逐张猜姿势。

先验证6至8张连续的快速转身/点出帧，再做完整32帧；每张继续参照同一主角原图，并核对相邻已通过帧，避免只接上一张导致误差累积。保持全局固定画布与尺度，不逐帧缩放或贴地。逐帧生成便于单独修错，但独立图片仍可能发生脸、衣服、体型和边缘闪烁；手绘动画的连贯性还来自统一造型、运动轨迹和时间分配，并非仅因逐张画。
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    members.append(("README.md", readme.encode("utf-8")))
    archive = OUT / "点穴原角色逐帧参考.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, data in members:
            z.writestr(name, data)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for row in rows:
            assert hashlib.sha256(z.read(row["file"])).hexdigest() == row["sha256"]
    (OUT / "verification.json").write_text(json.dumps({"source_hashes_match": 64, "ordered_samples": 64, "extra_reset_frames": 2, "zip_bytes": archive.stat().st_size, "rows": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"archive": str(archive), "ordered_samples": 64, "extra_reset_frames": 2, "source_hashes_match": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
