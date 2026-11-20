# 换电脑续接：先读这里

整理日期：2026-11-16；最新续接补充：2026-11-18（北京时间）。本文件是入口，详细约定仍以项目根目录 `AGENTS.md` 的后续补充为准。

## 最新工作

**11月19日最新补充：先草图，再建模。** 用户要求先比较竹林与岩石岛角自然融合的平面方案。本轮只制作 `artifacts/forest-cape-fusion-sketches/three-options.png` 及A/B/C单方案图，包含横向构图和俯视布局。尚未选定，没有修改模型；上一轮停止状态仍成立。具体提案和范围见该目录README，草图长度与构件安排不能作为已获授权的建模参数。

**11月19日最新状态：用户要求停止。** 续接 `01a1ee04-78e5-7913-9e22-7ef0ec779514`。独立接坡已被否定，用户要求岛角自然长在原竹林尽头；当前单网格延伸试作又被明确否定为“草地和岩石太生硬，这一段又长又突兀”。已停止模型、材质修改与录制，未擅自回退。最新保存revision为 `left-finish-forest-tip-stair-rock-settled`；本轮完整检查和往返录像未完成。先读 `artifacts/forest-tip-extension-review/README.md`，不要重跑已有作者脚本，不把下方旧轮次通行通过或旧建议当作当前结果认可。

**11月18日最新工作及待处理反馈：** 会话 `01a1edab-d2f0-7e03-86ba-c7391bcddea9` 授权按用户单层海边岛角参考接到横向竹林左端。新 `49_Reference_Cape` 已经Blender MCP制作并接入，包括单层岩台、22级下行石阶、沙滩、篝火与木凳；本次续接完成崖体/连接坡封底、沙地与草根接触，32.25秒往返通过。记录 `artifacts/reference-cape-review/README.md`，录像 `latest-review-motion.mp4`。**用户最新仍不满意林坡接缝的材质、高度及整体差异，希望无缝走入竹林，目前在讨论连续缓坡林口方案，未实施新方案。** 只读诊断已确认新接头混用了旧地表图，且UV范围外被边界色夹取；还需整体坡肩及森林受光连续处理，不能把毫米级几何接触检查当作视觉接缝已解决。旧竹林、光场及中段开场/7.0米移速保持；作者脚本有已执行保护。

当前正在推进**独立分层孤岛试玩场景**，不是继续旧岛的崖壁修补。入口是 `scenes/layered_island.tscn`，运行根目录 `试玩分层孤岛.cmd`。项目默认 F5 主场景仍是旧岛 `scenes/island.tscn`，不要因此误认为迁移丢了最新场景。

最新已执行工作来自会话 `01a1e309-8bcd-7bd1-a1f6-13998072c3f5`：从原场景左上竹径终点 `forest_end` **继续向左延伸约30米**，连接到 `forest_west_end`；同步降低有效俯角、调整旧竹林冠层和前后林地、斜向树影、局部光雾及实际景深。新段已经接入原场景，可连续往返，没有场景切换。

- 可编辑源：`assets/layered_island/layered_island.blend`。
- 运行资产：同目录 `layered_island.glb`、`layout.json` 和贴图子目录。
- 控制器：`scripts/layered_island.gd`，支撑采样：`scripts/layered_surface.gd`。
- 最近记录：`artifacts/bamboo-west-extension-review/README.md`。
- 最近实机录像：同目录 `review-motion.mp4`，约74秒，含行走、停留、回头和接头。
- 通行与承托：同目录 `movement-check.json`、`blender-audit.json`、`geometry-preservation.json`。

11月17日最新续接已修正用户指出的后林虚化“假、刻意”：保留远景景深、拉长过渡，减轻整排提灰并调整局部柔边雾；另修正海面覆盖下落内陆林谷造成的蓝灰横带。模型和UV未在本轮修改，海面覆盖数据由现有GLB只读生成。最新静态前后图与六机位检查见 `artifacts/forest-air-review/README.md`，效果待用户评价。原11月16日录像不代表这次调整后的效果。

**11月17日最新实施：** 用户否定密排实体后林后，已以“按这个推进把”授权按纠正后的分工实施。当前 `45_Forest_Layer_Roles` 是窄横向主竹竿带、透明叶簇与三个不同距离的森林绘景，薄局部雾、树影、景深和真实镜头平移配合；横向段不露海天，海岸仍保留海景。原密排 `44_Valley_Forest_Backdrop` 和横向段旧密集竹丛已归档至 `90_Rejected_Dense_Valley_Forest`，不导出。最新记录为 `artifacts/forest-layer-role-review/README.md`，有八机位图和38秒往返停留采样，通行/F5与保护对象核对完成。效果待用户评价，不恢复被否定版；原错误诊断仍见 `artifacts/forest-valley-enclosure-review/feedback-20261117.md`。

**11月17日进一步实施：** 用户认为整体尚可，要求前排竹林随机随风摆动、后景有层叠雾林，并强调复查旧《逸剑》分析。优先读 `artifacts/bamboo-atmosphere-source-study/README.md`，核心是局部受光、亮雾和雾后暗林共同建立空间。当前每株竹竿与对应叶簇共用独立阵风，根部固定；后林保留三张有实际纵深的绘景，并经MCP修正取景、加入三个独立薄雾载体和细竿/暗冠层。林内关闭会软化透明后林的近景DOF，远景DOF保留；海岸恢复近景DOF。最新记录已更新为 `artifacts/forest-wind-mist-review/README.md`，成功视频 `review-motion.mp4` 为22秒/12fps采样，含12秒锁镜停留与走/停/回头，成功检查 `retry-motion-check.json` 无失败。`final-motion-*`是已终止的不完整采样。保护对象、叶片位置/法线/主UV和原UV2 X保持；两个模型修改脚本带防重复保护，勿重跑。仍待外观评价，不把本轮称为达到逸剑。

**11月17日动态入光实施：** 用户在确认上轮尚未有动态光影照入深林后，授权继续补齐。当前 `forest_sun_field.gdshaderinc` 让主景受光、远林明暗、3层薄雾、3团体积雾和6个MCP斜光载体共用冠层透光变化，太阳方向稳定，保留暗林、随机阵风及原构图。所有体积雾按节点类型绑定，315个实际材质、三团体积雾方向核查通过。最新记录 `artifacts/forest-light-depth-review/README.md`，视频 `review-motion.mp4` 为28秒/12fps采样，含18秒锁镜停留和走/停/回头；234个原模型及UV/矩阵、路线/相机/风动元数据保持。新增模型作者 `build_forest_sunray_layers.py` 带防重复保护，勿重跑。此为受控视觉模拟，效果仍待评价。

此前同日已完成左区精修与沙滩冲退浪。桥、右侧洞区仍保留此前实现，尚未按左区质量全面精修；新段的地表/岩石笔触、竹叶疏密、光雾与整体HD-2D观感仍需用户评价。**已执行、技术通过与用户认可分别记录，当前不属于全场景正式验收。**

**11月17日人物入光实施：** 用户认为后林环境光影尚可，询问行走人物能否参与；已在分层场景接入 `hero_forest_light.gdshader` / `hero_forest_lighting.gd`。人物各部位按实际位置读取原冠层透光场，并复用已有行走/站姿法线，接收正常灯光与阴影；原图、比例、billboard、脚底和洞内颜色保持，未移植旧岛腿部形变。人物独立注册后，共享材质总数为316，历史315记录对应仅环境。最新记录 `artifacts/hero-forest-light-review/README.md`，录像 `review-motion.mp4` 为24秒/12fps采样，含8秒锁镜停留与走/停/回头。82帧、九个图集及30组透明/镜像隔离对照完成，67个保护文件保持。静态以 `pass2-*` 为准；此次只改Godot材质和逻辑，人物受光外观待评价。

## 必须保持的方向

**最新实施与续接（11月17–18日）：** 用户认为光照和背景远林暂时差不多，优先改善透视、立体感，并随后授权推进；无需完全照逸剑或其人物大小。诊断在 `artifacts/hd2d-camera-diagnosis/README.md`，现已落实到横向林段：相机实际距焦点24米、垂直FOV约30.9616°，保持原人物大小与方向，在接头恢复原取景；连续近侧路坎/草坡、四块斜顶立面岩石及三根原近侧竹子经Blender MCP调整。原二维远林、光场、路线、World、风动、中段开场和7.0米/秒保持。最后地表UV修复后原会话413中断；11月18日只读核对源、重新完成八机位与28秒连续运动交付，没有重跑建模。最新入口 `artifacts/near-mid-depth-review/README.md`，录像 `latest-review-motion.mp4`；旧无前缀录像拍于UV修复前。源/GLB仍为现有分层资产，作者三脚本有防重复保护。当前已可试玩，效果待用户评价，不把技术通过当作全部二维感已解决。

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
6. 双击 `试玩分层孤岛.cmd` 验证最新场景。11月17日用户要求后，开场直接位于横向竹林中段 `forest_west_mid`，移速由2.15提高至7.0米/秒，便于来回评价。WASD/方向键行走，R回沙滩，Tab显隐界面，F5锁定/恢复局部镜头。首次导入需要等待。
7. 建模前安装/连接Blender MCP；迁移目录 `setup/` 带本机插件副本及项目相关个人skill。原机使用Blender 5.1插件目录、MCP端口19887。新机应验证连接后再修改资产。

## 给新聊天的启动语

> 继续《孤屿霜尘》。请先读项目 `AGENTS.md` 和 `handoff/START_HERE.md`，再读 `artifacts/bamboo-west-extension-review/README.md`。当前是独立分层孤岛场景 `scenes/layered_island.tscn`，最新已从左上竹径向左延伸约30米，同时调整原场景镜头、林地、光影与景深；尚待我评价，不要宣称全岛完成，也不要重跑旧初建脚本。建模必须通过Blender MCP，保留固定横向HD-2D、真实视差、人物受光、World变换和UV2风权重。先核对当前资产与进度，等我的下一条具体反馈继续。需要追溯讨论时按迁移包 `codex-chats/INDEX.md` 查单个聊天，不要一次读入全部聊天或大图。

## 聊天导出的边界

迁移包保存本机可找回的项目聊天及其工具事件；原始JSONL不在原路径的旧聊天，从Codex本地聊天数据库提取，不伪称原始日志。逐会话覆盖情况见 `codex-chats/coverage.json`。已删除且本地任何来源都没有的内容无法补造；附件缺失也单列记录。

这些是可独立阅读的Markdown、JSONL和SQLite档案，**不是已验证的Codex桌面一键聊天导入格式**。新电脑的新聊天可以读档案接着工作，但旧聊天是否自动出现在侧栏不能仅靠解压保证。账号/供应商重新登录，密钥不作为迁移配置复制。运行中的服务、采样、进程和模型内部临时上下文不随文件迁移。

官方依据：[项目与聊天](https://learn.chatgpt.com/docs/projects)、[配置和状态位置](https://learn.chatgpt.com/docs/config-file/config-advanced#config-and-state-locations)、[环境变量](https://learn.chatgpt.com/docs/config-file/environment-variables)。聊天记录、项目文件与本机工具是分别需要保存/配置的部分。
