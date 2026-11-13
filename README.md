# 孤屿霜尘

## 工程源码与运行资源（2026-11-13）

本仓库保存当前 Godot 工程的核心源码与完整场景运行所需资源：`project.godot`、`scripts/`、`shaders/`、`scenes/`、`tools/`、`tests/`、剧情与对白数据，以及模型、贴图、人物动画图集、界面图片、字体、导入参数和来源说明。`AGENTS.md` 记录项目约定与后续方向；各轮美术试作不代表最终验收。

`artifacts/` **整个目录不上传**，其中的分析图片、录像、实验和验证备份均保留在本地。`.godot/` 缓存、Blender 制作源文件及备份、不被现有代码或资源引用的研究素材也不上传。是否提交美术资源以运行依赖为准，不按“二进制文件”或体积一概排除；`.gitignore` 列出当前未使用素材，新运行资源默认允许跟踪。

克隆后使用 **Godot 4.7.2 / Forward Plus** 导入 `project.godot`，等待首次资源导入完成后按 F5。主入口是 `scenes/island.tscn`；主岛、泉水、两档背景、行走与起身动画、对白界面均包含运行资源，动画测试场使用的图集也已包含，不需要复制本机 `.godot/` 缓存。运行游戏不需要 Blender；继续修改模型时仍须使用 Blender MCP 和本地制作源文件。资源并非全部原创，具体来源见各目录中的来源与许可说明。

远端原有 Phaser/Vite 初始化代码与历史保留在 `src/`、`package.json` 等文件中；当前 Godot 工程使用上述入口。下方为早期项目说明，其中旧场景名称、控制方式和分辨率仅供历史参考，当前状态以 `project.godot`、运行代码及 `AGENTS.md` 为准。

## 早期工程说明

这是一个面向 Godot 4.x 的武侠像素风游戏初始工程。剧情口头稿与转化场景见 [narrative/](narrative/README.md)。

当前默认启动场景为 **无名屿 · 棕榈海岸**：通过 blender-mcp 调整的三维草坡、海蚀岩岸、棕榈、低矮草簇、跨海木桥、礁石与海鸟，配合天空环境光、可调日光/云量、动态海水和主角中景跟随镜头。自然资产参考《I Just Wanted to Fish Demo》，使用的参考素材及转换记录见 `assets/island_blender/palm_study/SOURCES.md`。按 F5 预览，WASD / 方向键在道路范围内四向行走，Tab 隐藏界面，F 切换景深，R 归位。建模源文件为 `assets/island_blender/nameless_island.blend`，游戏导入对应 GLB，Godot 不生成场景模型。详细说明见 [海岛场景说明](scenes/ISLAND.md)。下文保留原二维验证场的说明。

## 当前内容

- 640×360 的像素风基础逻辑分辨率，电脑预览窗口默认 1280×720。
- 面向 vivo X Fold5 横屏运行，内外屏按比例扩展视野，地图、HUD 和角色活动范围随视口变化。
- `scenes/main.tscn` 作为项目入口，包含占位夜景地图和 HUD。
- `scenes/player.tscn` 使用 `CharacterBody2D`，已经带有碰撞体和基础移动脚本。
- `W/A/S/D` 映射到 `move_left/right/up/down`，后续可以在输入映射里追加方向键、手柄或移动端控件。
- 使用代码绘制临时角色与地图，接入正式 TileMapLayer、SpriteFrames 和动画时可以直接替换绘制部分。

## 打开与运行

1. 安装 Godot 4.x 稳定版（建议使用 4.x 的最新稳定小版本）。
2. 在 Godot 项目管理器中导入本目录，打开 `project.godot`。
3. 点击运行项目，使用 `W/A/S/D` 移动场景中的侠客占位角色。

## 后续接入建议

1. 把 `main.gd` 的占位绘制替换成 `TileMapLayer` 场景。
2. 为 `Player` 添加 Sprite2D/AnimatedSprite2D 和待机、行走动画。
3. 为场景边界、障碍物补充 StaticBody2D 碰撞体，再移除脚本里的临时位置限制。
4. 接入触屏摇杆和操作按钮；当前输入仍是桌面 WASD，手机触控待后续实现。

## vivo X Fold5 分辨率适配

官方屏幕规格：内屏 2480×2200、外屏 2748×1172，见 [vivo 参数页](https://www.vivo.com.cn/vivo/param/xfold5)。

- 基础画布：640×360；该尺寸用于场景和 UI 布局，不是手机的输出分辨率。
- 拉伸模式：`viewport`；长宽比策略：`expand`。宽屏增加横向视野，内屏增加纵向视野，保持角色比例。
- 缩放策略：`integer`，配合最近邻纹理采样，保持像素边缘清晰。整数倍缩放可能留下边框，不强制拉满屏幕。
- 方向：`sensor_landscape`，支持左右两个横屏方向。
- HUD 使用锚点和容器布局，并在 Android 上读取系统安全区，为挖孔和系统保留区域留出空间。
- 占位角色尺寸和速度同步放大到原先两倍，保持在基础画布中的视觉比例与移动节奏。

电脑可通过 Godot 的自定义运行参数 `--resolution 2480x2200` 或 `--resolution 2748x1172` 检查两种屏幕比例。手机系统栏、折叠时的 Activity 生命周期及真实触控仍需导出 Android 后在实机确认。
