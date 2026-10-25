# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [Unreleased]

## [0.1.0] - 2026-10-25

首个公开版本。

### Added

- `skills/formula-typesetting/SKILL.md`
  - 四步流程：判定问题在源还是在渲染器 → `scan` → `fix` → `validate`
  - 三层置信度（A 整行公式 / B 正文内带结构信号 / C 单个裸变量只报告）
  - 明确的失败处理与内容级验收要求
- `scripts/formula_norm.py`
  - `scan` / `fix` / `rules` / `selftest` / `validate` 五个子命令
  - 8 条误报防线（量纲、代码块、模块名、变量列表、标题行等）
  - 18 条单元级回归 + 8 条文档级回归
- `scripts/pptx_omml_inject.py`
  - LaTeX → OMML → `<a14:m>` 注入，支持整条替换 / 行内 / 自动检测
  - 写文件前校验 XML 良构性与形状数，防 PowerPoint 静默删形状
- `references/writing-convention.md` — LaTeX 书写规范与可粘贴的约定片段
- `references/omml-injection.md` — PPTX 注入配方、三条铁律与验收判据
- CI：win / mac / linux 三平台跑回归自测 + 跨平台卫生检查

### Fixed

- `validate` 在缺 pandoc 时不再抛 traceback，改为如实标 `skipped`（退出码 2）
- 全部验证步骤跳过时不再误报 `ok: true`（新增 `not_verified` 字段）
- 已有 `$$` 围栏不再被二次包裹（曾导致渲染时整段公式消失）
- 已有 `$...$` 不再被写成 `$$...$$`（曾导致 pandoc 判为字面文本）
- 代码块围栏不再被吞（曾导致代码变正文、`_` 与 `*` 被转义）
- LaTeX 命令不再被斜杠分式切开（`\pi/2` → `\frac{\pi}{2}`）
- 多字符下标整体收组并转正体（`δ_rel` → `\delta_{\mathrm{rel}}`）
- 量纲不再被误当公式（`3.2 W/m²`）

[Unreleased]: https://github.com/242742532Celestia/formula-typesetting/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/242742532Celestia/formula-typesetting/releases/tag/v0.1.0
