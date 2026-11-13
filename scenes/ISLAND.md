# 无名屿 · 棕榈海岸

按 F5 启动 `island.tscn`。三维资产通过 blender-mcp 在 Blender 5.1 中制作或导入参考模型、调整、检查并导出 GLB，由 Godot 4.6.1 Forward+ 加载。Godot 不生成场景模型几何。参考资源及来源记录见 `assets/island_blender/palm_study/SOURCES.md`。

## 场景

- 真实三维地形：左侧草坡尽头为断崖，山路向右下行，经过木索桥抵达另一块海蚀岩岸。
- 10:30 日光为默认状态，天空提供环境光，太阳有软阴影，使用 ACES 色调映射。时刻和云量共同控制太阳角度、亮度、阴影、天光及水面环境色；未实现雨粒、天气排程或完整昼夜循环。
- 8 棵高低、弯干不同的参考棕榈替换原阔叶树，清理了 Unity OBJ 中重复叠加的多个 LOD；仅导入 LOD0。低矮宽叶草簇在 Blender 中制作，颜色采样地表，植被随风微动。
- 木桥包含独立倒角桥板、木钉、木纹沟槽、桥柱、交叉支撑、下垂绳索、螺旋纤维和绑扎。
- 岩岸为连续草坡、分层崖壁和埋入地面的岩石组合。岩石使用参考配套材质，Unity AG 打包法线已转换为 RGB 切线法线。地表使用参考草地区域和匹配法线，保留原行走道路。
- 动态海面、局部闪光、礁石周围的白沫、远海薄雾和海鸟。
- 聚焦主角周围的侧视中景镜头，轻微俯角，平滑跟随移动并向行进方向略微前看。角色约占画面高度的五分之一；窄屏保持角色比例，缩小横向视野。界面设计尺寸为 1280×720，默认窗口 2560×1440（QHD，常称 2K），3D 按实际窗口尺寸渲染；像素质感由材质与最近邻纹理采样保留。
- 使用 CameraAttributesPractical 的深度景深，原屏幕分区虚化面保持关闭；当前不启用 glow。
- 复用已有的武侠行走图集，将角色作为像素精灵放进三维场景。

## 操作

| 按键 | 行为 |
| --- | --- |
| A / D、左右方向键 | 沿山路和桥左右行走，向左镜像 |
| W / S、上下方向键 | 在道路宽度内前后移动，向上显示背面、向下显示正面 |
| Tab | 显示 / 隐藏文字界面 |
| F | 切换景深 |
| R | 回到初始位置 |

这是一版可行走的场景预览。角色在道路中心线前后最多各0.55米的范围内移动，桥头提前收窄前后范围以避开绳栏，在左侧崖边和右岸停下。斜向移动不会加速，动画按输入的主要方向选择，完全对角时使用侧面；前后行走松键后使用同朝向的站立图。尚未配置全岛自由行走的物理碰撞、触屏控制、战斗或声音。桥梁是静态模型。移动端性能尚未实机验证。

三方向已替换为新绿幕参考生成的Q4循环：右侧26帧、背面29帧、正面24帧，均24fps。统一资源为`assets/characters/green_three_walk/swordsman_walk.tres`，六张行走图集保留512×768原帧；左侧使用右侧镜像。三张站立图来自同批透明参考，松键后保持对应朝向。全部方向使用pixel_size=0.0037、offset=(0,340)，脚底边缘y=724，移动速度为3.6（在3.0基础上提高20%）。来源与逐帧哈希记录在同目录`source.json`；可用`tools/import_three_direction_walk.py`从`D:/AI/minimax-h3-minimal/walk-batches/green-three-20261107`重新导入。旧行走资源保留备查，当前场景不再引用。`tools/verify_four_direction_walk.gd`检查实际场景的输入、帧数、播放、脚底锚点、停止、边界与过桥；加`-- --capture-walk`保存四方向截图到`artifacts/green-walk-integration/`。

## 编辑

`assets/island_blender/nameless_island.blend` 是完整可编辑源文件，包含地形、木桥、礁石、海面、海鸟与 `15_Palm_Coast` 棕榈/草簇集合，以及参考检查场景。游戏使用同目录的 `nameless_island.glb`，含 UV、材质和贴图；Godot 开启自动 LOD 导入。

`island_world.tscn` 是导入模型的包装，可在 Godot 中直接查看。`island.tscn` 加入角色、灯光、镜头和界面。角色仍使用已有二维武侠像素动画；海水与白沫在 Blender 制作的网格上使用 Godot 动态材质。

- `scripts/island.gd`：导入后的材质设置、角色路线、镜头、海鸟运动和界面，不含模型生成代码。
- 选中 `island.tscn` 的根节点，可在检查器的 Gameplay Camera 中调整镜头距离、视野、前看距离和跟随速度。
- 根节点的 Coastal Daylight 提供 `daylight_hour` 和 `cloud_cover`，运行时通过 `scripts/island_atmosphere.gd` 配置环境。命令行可追加 `-- --day-hour=10.5 --cloud-cover=0.9` 检查多云状态。
- `shaders/coast_palm.gdshader` / `coast_grass.gdshader`：棕榈和矮草的材质与微风；`fish_water.gdshader`：水面。
- `assets/island_blender/textures/`：在 Blender 中制作的岩石、草地、木材、树皮和山路色彩纹理。
- `assets/island_blender/asset_manifest.json`：资产分类、对象数与原始三角面数。

后续修改必须通过 blender-mcp 编辑 Blender 源文件，再导出 GLB，不得恢复 GDScript 模型生成方式。`tools/blender/` 保留本次通过 MCP 执行的制作步骤供审阅；它们依赖当次会话，不应在已手工修改的源文件上重复整批执行。

项目关闭自动 `.blend` 导入，只导入 GLB，运行游戏不需要安装 Blender。

重建前的场景、脚本和原始 Blender 会话保存在 `artifacts/blender/`，由 `.gdignore` 排除，不会混入游戏资源。旧 `--bake-world` 流程已移除。原先二维验证场仍可打开 `main.tscn` 并按 F6 运行。

本次核对记录与截图位于 `artifacts/palm-style-review/`，旧版备份位于其中的 `backup/`。`tools/capture_palm_island.gd` 检查四个原机位、近景、多云状态，并通过实际移动输入走过桥梁；`tools/blender/palm_contact_audit.py` 通过 Blender MCP 检查路径接地、棕榈根部及 LOD0 面数。旧记录保存在 `artifacts/blender/` 和 `artifacts/fish-style-review/`。
