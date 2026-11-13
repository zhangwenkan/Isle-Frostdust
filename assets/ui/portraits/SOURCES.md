# 对话头像

`an_lixing.webp` 来自用户于 2026-11-08 提供的安戾行头像：
`C:/Users/51440/Desktop/图片资源/孤屿霜尘/安戾行/6ae993ebc0d630f789a9368b.webp`。

直接复制原文件，未修改像素、裁切、抠像或生成替代图。仅在对话组件中按原比例缩放显示。

## 当前使用：新版透明头像

用户后来改用 `C:/Users/51440/Desktop/图片资源/孤屿霜尘/安戾行/背景透明.png`。该源文件实际为 1536×2048 的 RGB 图片，没有 Alpha，灰白棋盘格已写入像素。

`tools/prepare_dialogue_portrait.py` 清除背景及头发空隙中的棋盘格，保留眼睛区域、所有不透明前景 RGB 和原尺寸，导出真正 RGBA 的 `an_lixing_transparent.png`。未重新生成、改画面部或裁切。深浅底对照及验证在 `artifacts/wuxia-dialogue-review/portrait-alpha-review.png` 与 `portrait-alpha-verification.json`。
