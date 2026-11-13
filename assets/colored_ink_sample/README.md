# 西岸彩色笔触素材

本目录是 2026-11-08 西岸样区的新画稿。色块、笔触和布局由 `tools/paint_colored_ink_sample.py` 中可编辑的颜色、路径及分布规则绘制；不是从参考截图抠取的纹理，也没有使用图像生成 API。

- `ground_brush_color.png`：新的草地/道路颜色画稿，3072×1536，对应 Godot 世界 X -20 到 6、Z -7 到 7。运行时只在西岸样区核心及过渡范围使用。
- `ground_brush_strokes.png`：独立透明笔触层。
- `ground_path_mask.png`：道路与草地过渡的源遮罩。
- `rock_brush_0.png`、`rock_brush_1.png`：两个石头变体的灰青染色及结构笔触。
- `rock_lines_0.png`、`rock_lines_1.png`：透明结构线层。
- `palette-and-layout.json`：颜色、世界范围、石头路径及笔触数量。

线条跟随 Blender 的 `StructurePainting` UV，草地使用固定世界投影。竹叶通过 Blender 写入 UV0 边缘坐标并保留 UV2 风权重。石头模型由现有钓鱼参考阶段资产在 Blender MCP 内改形；模型的既有来源记录继续保留，新的笔触图不改变原模型的来源。

样区仍待美术评价。预览、动态录像和验证见 `artifacts/colored-ink-sample-review/README.md`。
