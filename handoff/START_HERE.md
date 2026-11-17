# 换电脑续接：先读这里

整理日期：2026-11-16（北京时间）。本文件是入口，详细约定仍以项目根目录 `AGENTS.md` 的后续补充为准。

## 最新工作

当前正在推进**独立分层孤岛试玩场景**，不是继续旧岛的崖壁修补。入口是 `scenes/layered_island.tscn`，运行根目录 `试玩分层孤岛.cmd`。项目默认 F5 主场景仍是旧岛 `scenes/island.tscn`，不要因此误认为迁移丢了最新场景。

最新已执行工作来自会话 `01a1e309-8bcd-7bd1-a1f6-13998072c3f5`：从原场景左上竹径终点 `forest_end` **继续向左延伸约30米**，连接到 `forest_west_end`；同步降低有效俯角、调整旧竹林冠层和前后林地、斜向树影、局部光雾及实际景深。新段已经接入原场景，可连续往返，没有场景切换。

- 可编辑源：`assets/layered_island/layered_island.blend`。
- 运行资产：同目录 `layered_island.glb`、`layout.json` 和贴图子目录。
- 控制器：`scripts/layered_island.gd`，支撑采样：`scripts/layered_surface.gd`。
- 最近记录：`artifacts/bamboo-west-extension-review/README.md`。
- 最近实机录像：同目录 `review-motion.mp4`，约74秒，含行走、停留、回头和接头。
- 通行与承托：同目录 `movement-check.json`、`blender-audit.json`、`geometry-preservation.json`。

此前同日已完成左区精修与沙滩冲退浪。桥、右侧洞区仍保留此前实现，尚未按左区质量全面精修；新段的地表/岩石笔触、竹叶疏密、光雾与整体HD-2D观感仍需用户评价。**已执行、技术通过与用户认可分别记录，当前不属于全场景正式验收。**

## 必须保持的方向

1. 三维几何、模型、UV及植物风力权重必须通过 **Blender MCP 操作 Blender**。Godot负责装配、材质、Shader、灯光、镜头、动画和逻辑，不能用其他几何生成脚本绕过要求。
2. 固定横向HD-2D、局部取景、真实相机平移与前中后景。参考还原度不能压过空间、受光和游玩效果；人物保留二维帧图，不默认重做三维角色。
3. 保留彩色关系与克制的水彩/水墨结构笔触；不恢复全岛灰米水墨、不铺满噪声、不恢复巨大独立前景岩柱。
4. `World` 已有旋转和平移；计算布局、岸线、风和相机时尊重该变换，不能直接清零，也不能把作者局部坐标当全局坐标。
5. 竹林和草的UV2含风权重。停止人物输入不能暂停环境。模型归档集合 `90_*` 不参与导出，不能默认恢复被否定版本。
6. 用户“沙滩先这样”表示先保留；海洋最终方案（像素水纹/2D water shader等）还没锁定。
7. 不盲目重跑已执行的初建脚本；部分MCP超时回包后Blender实际已完成并保存。先审计当前资产，再做针对性修改。
8. 新反馈优先于早期约定。涉及美术改动，沿用用户先静态评价的流程，后续是否录像按最新授权判断。已有录像不代表认可。

## 其他工作线

- 旧岛完整工程仍保留：`assets/island_blender/nameless_island.blend` / GLB，旧岛的群山、两档背景、程序云、海水、竹林、桥下生物和开场历史均在 `AGENTS.md` 与 `artifacts/`。
- 角色使用用户选回的原版人物，Q版是对照试作，不能自动换回。现有两个人物SpriteFrames资源有工作区修改，迁移必须带上。
- 起身动作经历第二版前段接第一版后段、尾部下巴局部修正；旧岛已推进过开场集成。以实际 `scripts/opening_rest.gd` 及运行资源为准，不把早期“未集成”记录套用到后来状态。
- 点穴、分段翻滚等武学试作保留在 `artifacts/` 和外部 MiniMax 批次。最新分段复杂动作虽做出倒转，仍有肢体、体格连续性与落地问题，未正式验收，不能自动接入游戏或重新提交旧批次。
- 剧情用项目 `.claude/skills/wuxia-prose/`，内容进 `narrative/`；主人公现名萧野（界面蕭野），岛名無人岛，暂定“大雍 · 景宁十七年”。`_example` 不是正史，未口述主线不要代写进 bible。

## 在新电脑上开始

1. 解压迁移包 `01-project-and-chats.zip`。其中 `project/` 是最新完整工程，含未提交资源、Blender源、项目skill及便携Godot。
2. 推荐将 `project/` 的内容放到 `D:\自己做着玩的\孤屿霜尘`。大量历史Blender作者脚本写死了该路径；若换位置，先改副本中的路径并检查Blender贴图引用，不能直接重跑旧脚本。
3. 解压 `02-project-history.zip` 到同一迁移目录，合并 `project/artifacts/`，恢复其余历史研究、录像、生成审阅与制作备份。先续最新场景只需第一包；完整档案还需第二包。
4. 若继续角色动作制作，再解压 `03-animation-workfiles.zip`；其中 `animation/minimax-h3-minimal/` 是已保存的批次与流程档案。生成模型、ComfyUI运行环境、显卡依赖需在新机配置，见迁移目录 `setup/ENVIRONMENT.md`。
5. 登录新机Codex，添加工程文件夹，开一个新聊天，贴下方启动语。无需把所有旧聊天一次塞进上下文。
6. 双击 `试玩分层孤岛.cmd` 验证最新场景。WASD/方向键行走，岔路向上进竹径，R回沙滩，Tab显隐界面，F5锁定/恢复局部镜头。首次导入需要等待。
7. 建模前安装/连接Blender MCP；迁移目录 `setup/` 带本机插件副本及项目相关个人skill。原机使用Blender 5.1插件目录、MCP端口19887。新机应验证连接后再修改资产。

## 给新聊天的启动语

> 继续《孤屿霜尘》。请先读项目 `AGENTS.md` 和 `handoff/START_HERE.md`，再读 `artifacts/bamboo-west-extension-review/README.md`。当前是独立分层孤岛场景 `scenes/layered_island.tscn`，最新已从左上竹径向左延伸约30米，同时调整原场景镜头、林地、光影与景深；尚待我评价，不要宣称全岛完成，也不要重跑旧初建脚本。建模必须通过Blender MCP，保留固定横向HD-2D、真实视差、人物受光、World变换和UV2风权重。先核对当前资产与进度，等我的下一条具体反馈继续。需要追溯讨论时按迁移包 `codex-chats/INDEX.md` 查单个聊天，不要一次读入全部聊天或大图。

## 聊天导出的边界

迁移包保存本机可找回的项目聊天及其工具事件；原始JSONL不在原路径的旧聊天，从Codex本地聊天数据库提取，不伪称原始日志。逐会话覆盖情况见 `codex-chats/coverage.json`。已删除且本地任何来源都没有的内容无法补造；附件缺失也单列记录。

这些是可独立阅读的Markdown、JSONL和SQLite档案，**不是已验证的Codex桌面一键聊天导入格式**。新电脑的新聊天可以读档案接着工作，但旧聊天是否自动出现在侧栏不能仅靠解压保证。账号/供应商重新登录，密钥不作为迁移配置复制。运行中的服务、采样、进程和模型内部临时上下文不随文件迁移。

官方依据：[项目与聊天](https://learn.chatgpt.com/docs/projects)、[配置和状态位置](https://learn.chatgpt.com/docs/config-file/config-advanced#config-and-state-locations)、[环境变量](https://learn.chatgpt.com/docs/config-file/environment-variables)。聊天记录、项目文件与本机工具是分别需要保存/配置的部分。
