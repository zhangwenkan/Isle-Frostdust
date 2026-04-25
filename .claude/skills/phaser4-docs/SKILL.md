---
name: phaser4-docs
description: >-
  When Phaser 4 API usage, config syntax, or class names are uncertain, verify them against the official Phaser 4 docs on docs.phaser.io via Dokobot before answering or coding.
read_when:
  - Working on Phaser 4 code and unsure about API names, config fields, lifecycle hooks, or plugin availability
  - Comparing Phaser 3 habits or templates against Phaser 4 official usage
  - Verifying GameConfig, Scene, Camera, Scale, Input, Loader, Physics, Tilemap, Tween, or GameObject syntax
  - Resolving uncertainty about whether a Phaser 4 property belongs at the top level, inside scale, render, physics, or another config section
emoji: "📘"
allowed-tools: Bash
---

# Phaser 4 Official Docs Lookup

Use this skill whenever Phaser 4 syntax or API usage is uncertain. Do not guess from memory when the question is about exact Phaser 4 names, config placement, lifecycle methods, or feature availability.

## Goal

Check the official Phaser 4 documentation on `docs.phaser.io` through Dokobot, then return the smallest correct answer needed for the current task.

## Rules

- Prefer the official Phaser 4 docs over memory.
- Do not assume Phaser 3 patterns still apply to Phaser 4.
- If unsure whether a config key belongs in top-level `GameConfig`, `scale`, `render`, `physics`, or somewhere else, check the docs first.
- Base the answer on what the docs actually say, not on common template habits.
- Keep the final answer focused on the current coding decision.

## Required workflow

1. Confirm Dokobot is available and a local device exists:
   ```bash
   dokobot doko list
   ```
2. Prefer local mode when available.
3. Choose the most specific docs page possible:
   - API index: `https://docs.phaser.io/api-documentation/api-documentation`
   - Class page: `https://docs.phaser.io/api-documentation/class/<slug>`
   - Typedef page: `https://docs.phaser.io/api-documentation/typedef/<slug>`
4. Read the page with Dokobot:
   ```bash
   dokobot doko read --local --device <DEVICE_ID> --timeout 90 --format text "<URL>"
   ```
5. Extract the exact API names, config semantics, lifecycle notes, or constraints needed for the task.
6. If the first page is too broad, follow linked class / typedef pages and narrow the lookup.
7. If docs lookup fails, clearly say what failed and only then fall back to a best-effort answer.

## Common lookups

- `Phaser.Game` initialization
- `Phaser.Types.Core.GameConfig`
- `Phaser.Scene` lifecycle (`init`, `preload`, `create`, `update`)
- `Phaser.Scale.ScaleManager` and scale config
- `Phaser.Input.*`
- `Phaser.Loader.*`
- `Phaser.Physics.Arcade.*`
- `Phaser.Physics.Matter.*`
- `Phaser.Tilemaps.*`
- `Phaser.GameObjects.*`

## Output style

Return:
1. The doc page(s) checked
2. The relevant Phaser 4 conclusion
3. The practical recommendation for the current code

Be concise. Quote exact property or class names when it matters.
