# 资产来源与交付范围

最新运行修订（2026-11-20）：用户授权修正脏糊、石阶轻飘和岛角偏小。当前 `tripo_game_assembly.blend/.glb` revision为 `rock-cape-weight-game-4`，海侧水平展开、重新制作实体石阶并调整原岩脚；节点/初形源 `rock_cape_weight_authoring.blend`，烘焙图 `textures_weight/`。独立 `rock_cape_weight.*` 为装配后期细化前的中间源，最终几何以游戏装配为准。旧岩肩不恢复；原Tripo测量重建来源依赖仍在。五机位静态及实际World承托检查见 `artifacts/rock-cape-weight-review/README.md`，未进行完整通行/连续行走验收，效果待评价。

最新运行版更新（2026-11-19）：用户指出粗粝石材与竹林草坡风格分离后，授权统一样区。当前游戏装配为 `tripo_game_assembly.blend` / `.glb`，使用 `rock_forest_wash_authoring.blend` 的彩色薄染与断续结构笔触，烘焙独立样品 `rock_forest_wash.blend` / `.glb`、贴图 `textures_wash/`。岩石与台阶几何UV未改，原参考来源和高面数/侧后问题仍成立；局部连续草坡通过Blender MCP补接，旧岩肩不恢复。已经接入Godot并做四机位静态检查，未做完整通行/连续行走测试。详见 `artifacts/rock-forest-style-review/README.md`。下列“未接入”描述属于早期独立样品的历史状态。

2026-11-19，用户项目内部静态样品。未声称第三方资产具有 CC0 或其他未核实许可。

最新粗粝感修订为 `tripo_replica_grit.blend` / `.glb`，节点源 `tripo_grit_material_authoring.blend`，六张色图/法线/粗糙度图在 `textures_grit/`。沿用上一版几何、UV和材质区域来源，只重写石材表面层次；没有新增Tripo颜色转移。浅剥落为法线受光效果，不是真实位移几何。旧 `tripo_replica_textured.*` 保留作对照，用户已指出其过于光滑，不视为已认可结果。

- 造型参考：用户提供的 `C:/Users/51440/Downloads/bccfc00f-d7ae-4bae-abab-5cc7e8c254e6.glb`，SHA256 `e51a58a5a6d60e8c2c3334d44a0509e16c6475ac73c2bed97051d74d05679bd2`。
- 岩体：上一轮以该参考网格为测量输入的表面重建与贴合，非从零独立雕刻。台阶为实测层高与轴线约束的新网格。当前材质轮次不改变这项来源依赖。
- 纹理：本轮新写 Blender 材质节点、新 UV 和烘焙的 PNG。原纹理仅参与离散材质区域辨认，没有将原 RGB 投射或复制为交付色图。不是未接触原纹理的独立制作。
- `tripo_replica_textured.blend` 和 `.glb` 为当前有贴图的交付版；`tripo_material_authoring.blend` 保留新材质节点和属性，`textures/` 保留四张 PNG。原灰模及旧试作保留为历史记录。
- 侧后薄面、破口、缺体积与部分木件表现仍存在，约 69 万三角形尚未优化；未接入 Godot 游戏、未做通行或运动测试。不能将当前结果称为完整游戏资产、独立建模能力验证或用户已验收结果。

详情及真实渲染见 `artifacts/tripo-replica-review/README.md`。所有三维资产操作经 Blender MCP；无新的模型生成工作流/skill被固化。
