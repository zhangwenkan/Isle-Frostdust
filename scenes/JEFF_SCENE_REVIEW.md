# Jeff Studio Scene 仓库评估

检查日期：2026-11-07。仓库：<https://github.com/jeffstudio-dev/jeff-studio-scene>。
检查提交：`ef5a3b58ead036e464f82d2c42def6264d4b3b9f`，插件版本 0.4.7.1。

本次检查了完整文件树、README、公开分发说明、中文手册、许可证、建筑/地形生成源码、材质源码、GLB 导出代码及作者提供的建筑截图。没有安装或运行插件，没有将其资源导入游戏。参考文件保存在 `artifacts/jeff-scene-review/`，由 artifacts/.gdignore 隔离。

## 定位与实际内容

它是 Godot HD-2D 场景制作插件，加上内置贴图与参数预设。包含九种建筑风格、10 类 46 种建筑功能条目、35 张地表纹理、14 套地表方案、天气/UI 图集和场景编辑功能。不是现成可玩的游戏，也不是包含全部模型、人物和案例的素材包。

完整公开文件树没有 .blend、.glb、.gltf、.fbx、.obj 或 .tscn；建筑模型由插件生成。共享素材库、提取角色/模型、案例、测试森林和生成缓存均被公开分发说明明确排除。个别旧手册段落仍描述历史三包交付与学习角色，应以当前 README、DISTRIBUTION.md 和实际文件树为准。

## 如何制作新模型

- `editor/building_mesh.gd`、`building_generator.gd`、`building_architecture_v5.gd` 通过 GDScript SurfaceTool 创建顶点、法线、UV 和三角面，再按角色合并为 ArrayMesh。
- 宽深、楼层、屋顶坡度、出檐、窗列和外形/细节种子驱动规则生成。可产生既有建筑类型的新组合；不是输入任意描述就生成任意类别模型的 AI 3D 服务。
- `runtime/terrain.gd` 使用 ArrayMesh 构造地形网格。
- `editor/building_export.gd` 使用 GLTFDocument 导出单栋建筑 GLB，含模型、UV、材质和 PNG，可在 Blender 编辑。导出是外观快照，不含 Godot 脚本、碰撞与可再次生成的参数。
- 自动小镇功能明确不跨水、不生成桥梁。自然海岛的主景松树、海蚀岩壁等不能凭其建筑生成器直接获得。

## 值得借鉴的美术方法

1. 几何和纹理分工：屋檐、梁柱、窗框保留几何，细瓦缝、木纹、墙裙、磨损使用材质。截图中的丰富细节不能全部当作模型几何。
2. 独立材质图集：v5/v6 索引注明 `Original imagegen artwork`，由图像生成提供图集源稿；这与几何生成是两条独立流程。没有提供全部原始生成提示词，不能声称能够精确复现作者生成过程。
3. 明确的纹理尺度：重复材质约 40 像素/米；v5 源码屋面切为 64×64、其他材质 128×128，UV 分别按 1.6m 与 3.2m 重复。门窗等构件采用专门映射。
4. 采样处理：各图集区域独立切出、各自生成 mipmap，使用 NEAREST_WITH_MIPMAPS，减轻远处闪烁及图集串色。
5. 不宜照搬全部渲染：其 presentation.gdshader 的远近模糊按 SCREEN_UV.y 分区，属于屏幕区域模拟。我们已有真正基于深度的景深，应保留。

## 对本项目的建议

优先借鉴其材质分工、图集组织、世界尺度与远近采样方法，在岩石、树皮、叶簇、木桥上建立同样清晰的材质规则；通过 blender-mcp 在 Blender 中设计几何与 UV，再导入 Godot。

直接使用其 Godot 建筑/地形生成器会触及本项目已约定的“不得使用 GDScript 生成三维模型”。因此，当前默认路线是参考规则并在 Blender 落实，不把“先在 Godot 生成、再导入 Blender”作为绕过约定的路径。以后若有城镇场景，其建筑模块规则比当前自然海岛更直接适用。

代码采用 MIT，保留版权和许可声明。Sky3D、银河/月球纹理等各有说明，不能把插件代码的 MIT 当作所有外部共享素材的许可。作者声称验证环境为 Godot 4.7.2 的 Compatibility/Forward+；本项目目前 4.6.1，尚未验证插件在本项目版本中的兼容性。

## 核心来源

- [README](https://github.com/jeffstudio-dev/jeff-studio-scene/blob/main/README.md)
- [公开分发范围](https://github.com/jeffstudio-dev/jeff-studio-scene/blob/main/manual/DISTRIBUTION.md)
- [建筑和 GLB 导出手册](https://github.com/jeffstudio-dev/jeff-studio-scene/blob/main/manual/zh/reference/assets.md)
- [建筑几何实现](https://github.com/jeffstudio-dev/jeff-studio-scene/blob/main/addons/hd2d_scene_tools/editor/building_architecture_v5.gd)
- [材质实现](https://github.com/jeffstudio-dev/jeff-studio-scene/blob/main/addons/hd2d_scene_tools/runtime/building_materials_v5.gd)
- [图集来源索引](https://github.com/jeffstudio-dev/jeff-studio-scene/blob/main/addons/hd2d_scene_tools/assets/buildings/v5/atlas-index.json)
- [第三方声明](https://github.com/jeffstudio-dev/jeff-studio-scene/blob/main/THIRD_PARTY_NOTICES.md)
