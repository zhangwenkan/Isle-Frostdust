# H3 右行循环测试

在 Godot 打开 `walk_test.tscn`，按 F6。原游戏的主场景没有改动。

- 空格暂停/播放，左右方向键逐帧，M 切换向右移动，+/- 调速度，R 从头开始。
- 接入：把 `walk_right.tres` 赋给 AnimatedSprite2D.sprite_frames；centered=false，offset=(-128,-362)。
- 所有帧 256×384、24fps、同一个脚底基点。只整体平移，无逐帧缩放/网格变形。
- 动画是原地行走；实际游戏移动速度必须与步频匹配。M 模式的速度仅用于检查，不代表已严格消除水平滑步。
- 这是一轮候选小样。结合附带的 animation.json 查看已完成的像素校验与视觉检查状态。
