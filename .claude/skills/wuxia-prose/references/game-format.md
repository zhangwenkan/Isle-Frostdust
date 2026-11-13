# 游戏场景稿格式

转化结果用 Markdown，一篇一场，日后可再导进引擎。现在不绑死 Godot 对话系统。

文件名：`narrative/scenes/<卷>-<回>-<场>.md`  
例：`nameless-01-shore-fisher.md`

## 文首

```markdown
---
id: nameless-01-shore-fisher
title: 岸边
volume: 无名屿
chapter: 1
location: 棕榈海岸 / 断桥西
cast:
  - 主角
  - 渔翁
status: draft
source: narrative/inbox/20261107-岸边老头.md
register:
  dialogue: gulong
  narration: jinyong-liang
hook: 渔翁的钩上没有鱼，却有一截白线
---
```

`status`：`draft` 仅转化 · `canon` 用户认可进圣经 · `cut` 作废。

## 正文结构

严格按这个顺序，方便以后拆表：

### 1. 整理（给作者看，进游戏可剥掉）

短，用列表。含信息差、钩子、待确认。

### 2. 场（给游戏看）

用这些标记：

```
[旁白]
……

[名：情绪或动作]
……
……

[指令：表情 / 走位 / 天气 / 可走]
……

[选项]
A. ……
B. ……
C. ……（可空、可沉默）
```

规则：

- `[名：…]` 的名字用游戏显示名，不用解释号
- 对白一句一行
- `[指令]` 只写能被演出的：转身、收竿、潮声变大。不写心理
- 选项字母稳定，分支用 `> 若 A` 写在后面，不要把分支缠进主对话

### 3. 名物（若本场新出现）

表：名、类别、谁起的、可否给玩家看、禁忌（勿撞原著）。

### 4. 未用的口头原句

把用户原话摘几句放这里，防止改拧。

## 长度

- 过场旁白：一般 2–6 行
- 对白场：玩家一次阅读不超过约 20 个气泡，更长就拆场
- 文书：另做 `[文书]` 块，可再分页

## 示范骨架

见 `narrative/_example/converted.md`。
