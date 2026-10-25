---
name: formula-typesetting
description: |
  把 AI 生成的 Unicode 伪公式（ε、ω_d、A₀、e^(−γt)、√(k/m)、m·ẍ）转成 LaTeX 源码，
  并渲染成 PDF/DOCX/PPTX 里的真公式（真分式、真上下标、可编辑 OMML，不是图片也不是豆腐块）。
  Load this skill when the user says「公式不好看 / 公式排版 / 把公式改成真公式 / 公式渲染」，
  触发表述包括「公式用 Unicode 写的，改成 LaTeX」「讲义里的公式没有分式」「PPT 里的公式想双击编辑」
  「ε ω_d 这类符号看着别扭」「生成讲义/教案/课件后发现公式是伪公式」。
  同时覆盖源头治理：写讲义、教案、课件、报告时先约定公式怎么写，避免下游返工。
  Do NOT use for 纯代码里的数学计算、Matplotlib/Mathematica 出图、公式求解或符号推导，
  也不用于「文档里没有公式」的一般排版任务——那种情况用文档处理类 skill
  （markdown-export / docx / pptx）或直接用 pandoc。
---

# 公式排版（伪公式 → 真公式）

## Inputs to collect

动手之前先确认这四件事，缺哪件就问，别用假设硬上：

- **载体**：最终交付是 Markdown、PPTX、DOCX，还是只改源文件？三者的注入路径不同。
- **目标文件与范围**：改哪几份材料、哪几页。范围越具体越好（"只改第 10、11 页"优于"整个课件"）。
- **源文件能不能动**：默认**只写副本**。要覆盖原文件必须用户明确同意——讲义、课件这类教学材料
  往往有配套的构建脚本，直接改源会让下次构建把改动冲掉。
- **有没有旧的书写约定**：正文里写着「公式一律写成纯文本」「带 · 的是乘号」这类约定时，
  它和 LaTeX 约定直接冲突，改造完必须同步改掉，否则读者（和后续的 AI）会继续写伪公式。

## Procedure

### 1. 先判定问题在源还是在渲染器

这一步决定后面所有动作，值得花 30 秒。

在源文件里 grep `latex|katex|mathml|omml`：

```powershell
Select-String -Path 讲义.md -Pattern 'latex|katex|mathml|omml' -CaseSensitive:$false
```

零命中 ⇒ 源里根本没有 LaTeX，**问题在源**。这时换渲染器、换公式库都没有用，
必须先把源改成 LaTeX。渲染器侧只能处理已经写对的源。

### 2. 扫描：只报告，不改

```powershell
python scripts\formula_norm.py scan 讲义.md
```

🔴 上面的 `scripts\` 是**相对 skill 目录**的路径。工作目录不在 skill 目录时要用绝对路径，
否则脚本找不到：

```powershell
python <skill-dir>\scripts\formula_norm.py scan 讲义.md
```

`scan` 按规则分类报出命中（裸希腊字母、Unicode 上标、中文里夹裸变量等），
并给出每条的 suggested 写法。它的作用是**建立基线**：知道有多少处、分布在哪。

`python scripts\formula_norm.py rules` 列出全部规则类别。

### 3. 改造：产出副本 + 逐条对照报告

```powershell
python scripts\formula_norm.py fix 讲义.md --out 讲义_规范化.md --report 讲义_对照报告.md
```

`fix` 把改造结果写进 `--out` 指定的**副本**，原文件不动；`--report` 给出逐条对照
（原文本 → 新文本 → 改写理由），改了什么、为什么改、哪条需要人工看。

改造分三层置信度：

- **A 类（整行公式）**：整段都是公式结构 → 直接改写，高置信度。
- **B 类（正文内带结构信号的行内公式）**：句子里含 `=`、`√(`、希腊字母组合等结构信号 → 改写。
- **C 类（单个裸变量）**：正文里夹的一个字母 → **只报告，不改**。误伤风险太高。

报告里带「需复核」的条目必须逐条看过再采纳。实测 227 处命中只需复核 1 处，
但那 1 处正是公式里夹了中文常量——机器改不了，只能人写。

🔴 **源里已有一部分是真 LaTeX 时，要区别对待**。工具会保留已有的 `$...$` / `$$...$$` 围栏，
只规范化内部内容，不再套第二层分隔符。但**围栏内的多行结构**（`\begin{pmatrix}`、
`\begin{aligned}`）会原样保留，不做内部改写——这类结构里的下标不会被补成 `_{...}`，
需要自己检查。

三条曾经踩过的坑（现已在脚本里修掉并设了文档级回归，但**改脚本后要跑 `selftest` 确认**）：

- 已有 `$$` 围栏被二次包裹 ⇒ 嵌套 display math ⇒ 渲染时整段公式消失；
- 已有 `$...$` 被写成 `$$...$$` ⇒ pandoc 判为字面文本 ⇒ PDF 里直接出现 `$$`；
- 代码块围栏被吞 ⇒ 代码块变成正文 ⇒ 变量名的 `_`、`*` 被转义 ⇒ 代码被改坏。

### 4. 落地验证：证明排版管线真的能渲染

改对了源，还要证明下游能出图，否则只是把问题推后。

```powershell
python scripts\formula_norm.py validate 讲义_规范化.md
```

`validate` 实测跑通：pandoc → typst 编译 PDF、pandoc → DOCX 后检查 OMML 公式数量。
这一步会真实调用外部工具；缺 typst 时该项会如实标 `skipped` 而不是假装通过。

🔴 **`validate` 返回 `ok: true` ≠ 公式是对的。** 它只验管线跑不跑得通，不验内容对不对：
一份把 `Jones 矢量` 整个吃掉、把马吕斯定律渲染成 `I = I_{0} ^2` 的坏文档，同样能 `ok: true`。

所以必须再做一次**内容级检查**——查渲染产物里有没有字面量残留：

```powershell
# typst 中间产物里的字面量残留（出现即说明公式没被识别）
Select-String -Path probe.typ -Pattern '\$\$|\\frac|\\theta|\\delta|\\cos|\_|\*' -Encoding UTF8
```

期望是 **0 处命中**。有命中就是公式没被识别（常见于嵌套 `$$`、双 `$`、代码围栏被吞）。
更稳妥的做法是把渲染出来的 PDF 转成 PNG **用眼睛看一遍**——分式有没有分数线、
上下标位置对不对，只有肉眼能判。

渲染成 PDF / DOCX。**优先用本机已有的排版 skill**（如 `markdown-export`），
它处理中文字体与版式更完整：

```powershell
node <markdown-export>/scripts/mdx.mjs convert 讲义_规范化.md --to pdf --out 讲义_规范化.pdf
node <markdown-export>/scripts/mdx.mjs convert 讲义_规范化.md --to docx --out 讲义_规范化.docx
```

没有排版 skill 时，用 pandoc + typst 直接走（本 skill 的 `validate` 就是这么跑的）：

```powershell
pandoc -f markdown -t typst 讲义_规范化.md -o 讲义_规范化.typ
typst compile 讲义_规范化.typ 讲义_规范化.pdf
pandoc -f markdown -t docx 讲义_规范化.md -o 讲义_规范化.docx
```

⚠️ pandoc 的 typst writer 对**个别命令有损**（实测 `\begin{pmatrix}` 会被压成 `vec(...)`、
`\Delta` 可能变成 `Delta`）。矩阵/对齐环境多的文档，先转 PNG 核对一下再用。

### 5. PPTX：注入原生可编辑公式

PPTX 的公式要能双击进公式编辑器，必须注入 OMML（`<a14:m>`），不能贴图片。

```powershell
# ① 先看 deck 里有哪些文本，用来写 spec
python scripts\pptx_omml_inject.py --scan 课件.pptx

# ② 按 spec 注入
python scripts\pptx_omml_inject.py 课件.pptx 课件_公式版.pptx --spec spec.json
```

spec 格式：

```json
{
  "parts": [
    {"part": "ppt/slides/slide10.xml",
     "target": "c = B²L²/R",
     "latex": "\\frac{B^{2}L^{2}}{R}",
     "prefix": "阻尼系数 "},

    {"part": "ppt/slides/slide11.xml", "auto": true}
  ]
}
```

- `target` + `latex`：把承载该文字的那个 run 换掉；`prefix`/`suffix` 保留公式前后的文字，
  这样「阻尼比 ζ = γ/ω₀」会变成「阻尼比」+ 真公式，而不是整句变公式。
- `auto: true`：自动检测该 part 里的公式片段并**行内**注入，位置由 `formula_norm.find_spans` 给出。
  备注页（`ppt/notesSlides/notesSlideN.xml`）用这个最省事。

注入器自带两道守卫，注入后形状数或 XML 良构性一变就报错、不写文件：
形状被吞掉是 PowerPoint「修复」后无声删形状的前兆，坏了的文件比没有文件更糟。

### 6. 交付前把话说清楚

- **报告必须带数字**：改了多少处、复核几处、误报几处。
- **代价要说出来**：LaTeX 源在 PDF 里不再是可复制的纯文本（分式会变成排版结构），
  需要纯文本的场景从 `.md` 源或 DOCX 取。
- **视觉证据**：公式排版是视觉问题，交付对比图（改造前 / 改造后）比交付文字描述有说服力。

## Output contract

产出物应当包含：

| 产出物 | 说明 |
|---|---|
| `<原名>_规范化.md` | 改造后的**副本**，原文件不动 |
| `<原名>_对照报告.md` | 逐条对照：原文本 → 新文本 → 理由；标注需复核项 |
| `<原名>_规范化.pdf` / `.docx` | 验证过能出真公式的成品 |
| `*_公式版.pptx` | 注入 OMML 后的课件（如涉及） |
| 验收数字 | 命中数 / 需复核数 / 误报数 / OMML 公式数 / 字面量残留数 |

**字面量残留数**是必报项：渲染产物里若出现 `$$`、`\frac`、`\theta`、`\_` 等字面量，
说明公式没被识别（常见于嵌套 `$$`、双 `$`、代码围栏被吞）。期望 0。
只报 `validate` 的 `ok: true` 是不够的——它不验内容。

源文件被修改时，要在报告里列出**改了哪几行**，并说明为什么这次破例不覆盖。

## Failure handling

- **pandoc 或 typst 缺失**：`validate` 会把对应项标成 `skipped`。如实报告"该项未验证"，
  不要把未跑过说成通过。typst 可用环境变量 `TYPST` 指定路径。
- **`fix` 后 `validate` 失败**：多半是 LaTeX 语法不对（常见于 `\sqrt{k/m}` 这类，
  根号只盖住一半）。查报告里标「需复核」和「公式夹中文」的条目。
- **注入后 PowerPoint 提示修复文件**：说明 OOXML 结构被破坏。按 `references/omml-injection.md`
  的三条铁律逐条对照，重点查 `a:p` 子元素顺序。脚本的守卫能挡住形状丢失，
  但挡不住所有顺序问题——必须真开一次 PowerPoint 看。
- **公式里夹中文常量**：检测器会标出来但不会自动改（需要 `\text{}`，且要判断是否该改写）。
  这一类交回用户，不要自行猜测改写。
- **源文件里没有任何公式**：不是本 skill 的场景，转文档处理类 skill 或直接用 pandoc。

## Examples

**Example 1 — 讲义里的伪公式**

输入：`讲义.md` 里写着 `ε/R`、`ω_d`、`e^(−γt)`，用户说"公式看着不像公式"。

```
python scripts\formula_norm.py scan 讲义.md
→ 命中 416 处，涉及 13 类规则（其中代码块内的命中不计）

python scripts\formula_norm.py fix 讲义.md --out 讲义_规范化.md --report 讲义_对照报告.md
→ 讲义 91 处 / 1 需复核 / 47 裸变量 / 1 约定冲突

python scripts\formula_norm.py validate 讲义_规范化.md
→ PDF 编译 OK；DOCX OMML 160 公式 / 36 分式 / 6 根式
```

产出副本 + 对照报告 + PDF/DOCX；并指出正文第 9 行「公式一律写成纯文本」的旧约定
与新约定冲突，给出建议措辞，等用户确认再落。

**Example 2 — 课件里嵌公式**

输入：`课件.pptx` 第 10 页有 `c = B²L²/R`，用户说"想让它双击能编辑"。

```
python scripts\pptx_omml_inject.py --scan 课件.pptx
→ ppt/slides/slide10.xml   c = B²L²/R

spec.json: {"parts":[{"part":"ppt/slides/slide10.xml","target":"c = B²L²/R",
                       "latex":"\\frac{B^{2}L^{2}}{R}","prefix":"阻尼系数 "}]}

python scripts\pptx_omml_inject.py 课件.pptx 课件_公式版.pptx --spec spec.json
→ 替换 'c = B²L²/R' → \frac{B^{2}L^{2}}{R}
→ 已写出 课件_公式版.pptx（1 处公式）
```

再用 PowerPoint 打开确认不提示修复、形状数不变（注入前后各 12 个形状）。

## Windows (win32) platform notes

本 skill 的全部脚本用 `python` 或 `py` 调用，命令在 PowerShell 里执行：

```powershell
# 用 python（Windows 上更常见）
python scripts\formula_norm.py scan 讲义.md

# 或用 py 启动器
py scripts\formula_norm.py scan 讲义.md
```

注意这几点：

- 脚本路径用相对路径或反斜杠均可，PowerShell 里建议加引号包住含空格的路径。
  工作目录不在 skill 目录时用绝对路径：`<skill-dir>\scripts\formula_norm.py`。
- 读写文本文件显式带 `-Encoding UTF8`（`Get-Content`/`Set-Content`），
  否则中文在 PS 5.1 下会按 ANSI/GBK 解释而乱码。
- 读 `.ps1` 脚本时同样按 ANSI/GBK 处理，所以脚本内容尽量保持 ASCII，
  中文路径通过环境变量传进去。
- 删临时产物优先用**可恢复**的删除（能进回收站/可还原）；
  不可恢复的 `Remove-Item -Force` 只在明确知道自己在删什么时用。
- `scripts\formula_norm.py` 被调用后会在 `scripts\` 下生成 `__pycache__\`。
  它不该留在 skill 目录里（skill 只放 LLM 执行需要的文件），交付前删掉。
- 本 skill 不依赖 `python3`、`bash`、`/tmp`；Windows 上不需要额外的 shell 适配。

### 跨平台说明

脚本本身是跨平台的 Python，Windows / macOS / Linux 都能跑。差异只在两处：

- **typst / pandoc 的查找**：先找 PATH，再看环境变量 `TYPST`（typst），
  再找常见安装位置。找不到时 `validate` 会如实标 `skipped`——
  **这不是失败，是没验证**，退出码为 2（区别于「跑过但失败」的 1）。
- **shell 语法**：本节给的是 PowerShell 写法；macOS / Linux 用等价的
  `python3 scripts/formula_norm.py scan 讲义.md` 即可，脚本无需改动。

## References

- `references/writing-convention.md` — LaTeX 公式书写规范：分式/上下标/变音符/乘号的 Do/Don't 对照表，
  以及可直接粘给 AI 的约定片段。**写新内容时先读它，从源头把公式写对。**
- `references/omml-injection.md` — PPTX 注入 OMML 的配方与三条铁律、偏移陷阱、验收判据。
  **做 PPTX 注入前读它。**
