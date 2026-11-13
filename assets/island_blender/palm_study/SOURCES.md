# 棕榈海岸研究素材来源

2026-11-07 用户要求把阔叶树换成参考游戏中的椰子树/棕榈树，并对照实机重新调整草地、草丛、岩石、阳光及阴影。

参考游戏为《I Just Wanted to Fish Demo》，本机资料位于 `D:/steam/steamapps/common/I Just Wanted to Fish Demo/analysis/exported_all`。本轮使用的 Palm_Bent、Palm_Tall、Palm_Short、Palm_Young 模型与 T_Palm 配套图集，以及已有 Rock A–D 模型与材质均来自这些提取资源，属于参考游戏资产，并非本项目原创。未改变其原有权利或许可。

视觉对照来自 [官方 Steam 页面](https://store.steampowered.com/app/5351000/)，9 张公开截图的地址记录在 `artifacts/palm-style-review/official-steam-reference.json`。本轮未控制或运行参考游戏。

`source_manifest.json` 记录图像来源与变换。Unity 的 AG 打包法线不能直接作 RGB 法线使用，本轮按 `X = A * R, Y = G` 解包并重建 Z，输出 OpenGL RGB 法线供 Blender/glTF/Godot 使用。草地图从参考区域图中选取一块纯草地色块区域，按现有海岛尺寸映射一次并衔接既有道路，没有铺设 Jeff 噪声或裂纹贴图。

棕榈在 Blender MCP 内导入、旋转、缩放和接地。低矮宽叶草簇与连续崖壁的层次调整在 Blender MCP 内制作。Godot 仅接入天空环境光、太阳、材质、风动和镜头验证。

原始 Unity 棕榈包含 7–8 级 Mesh LOD，而所给 OBJ 混合导出了全部级别。`reference-lod-metadata.json` 保存实际索引范围；Blender 内按 LOD0 的范围过滤原 OBJ 后导入，防止不同精度网格重叠造成条纹。Rock A–D 没有有效的额外 LOD，保留原始面列表。

Blender 操作脚本：`tools/blender/palm_coast_refine.py`。图像转换脚本：`tools/prepare_palm_materials.py`。保留旧版本在 `artifacts/palm-style-review/backup/`。
