# PDF-compressor-skill

**A simple Claude skill for compressing PDFs.**

[English](#english) · [中文](#中文)

---

## English

### Motivation

Academic papers keep getting bigger. It's now routine to encounter 8–9 MB PDFs packed with figures, plots, and screenshots. When you want to discuss a paper in full with an AI, that size becomes a real problem — many interfaces impose file size limits, and large files eat through context budgets fast.

I kept reaching for online PDF compressors and kept running into the same frustrations: paywalls for anything beyond basic compression, mandatory sign-ups, and no way to adapt the tool to my own workflow. So I built this: a small, hackable Claude skill that wraps Ghostscript (with a pikepdf fallback) and lets you compress any PDF just by telling Claude to do it.

### What it does

- Compresses PDFs using **Ghostscript** (primary) or **pikepdf** (automatic fallback if GS isn't installed)
- Control quality by named preset, 1–5 level shorthand, or explicit DPI value
- Claude shows you a DPI menu before compressing — no guessing, no unreliable size estimates
- Auto-names output as `filename_compressed.pdf` in the same directory
- Works as a **standalone CLI tool** or as a **Claude skill** (Claude Code / compatible agents)
- Responds in whatever language you use

### Backends

| Backend | Install | Image downsampling | Best for |
|---------|---------|-------------------|----------|
| Ghostscript | System package | ✅ Yes | Maximum compression, image-heavy PDFs |
| pikepdf | `pip install pikepdf` | ❌ No | Stream/font compression, no system permissions needed |

The script tries Ghostscript first and falls back to pikepdf automatically.

### Installation

**1. Get the files**
```bash
git clone https://github.com/gaoxin492/pdf-compressor
cd pdf-compressor
```

**2. Install Ghostscript**

Ghostscript is strongly recommended — it's the only backend that can downsample images, which is where most of the size savings come from in image-heavy PDFs.

The easiest way: run the included installer script and it will detect your OS automatically.

```bash
bash install_gs.sh
```

Or install manually:

```bash
# macOS (requires Homebrew — https://brew.sh if you don't have it)
brew install ghostscript

# Ubuntu / Debian
sudo apt install ghostscript

# Fedora
sudo dnf install ghostscript

# Arch
sudo pacman -S ghostscript

# Windows — one-liner if you have winget (Windows 10+):
winget install ArtifexSoftware.GhostScript
# Or download the installer: https://www.ghostscript.com/download/gsdnld.html
```

> **No system-level install permissions?** The script falls back to pikepdf (`pip install pikepdf`), which handles stream and font compression but cannot downsample images.

**3. Add as a Claude skill**

Claude Code reads skills from a directory you configure. Here's how to set it up:

```bash
mkdir -p ~/.claude/skills
mv pdf-compressor ~/.claude/skills/
```

Then open (or create) `~/.claude/CLAUDE.md` and add:

```markdown
## Skills
@~/.claude/skills/pdf-compressor/SKILL.md
```

The next time you start a Claude Code session, the skill is active.

> **Verify it's loaded**: ask Claude "what skills do you have?" and it should mention the PDF compressor.

### Usage

**As a Claude skill** — just talk naturally:
> "Compress this paper."
> "Help me shrink this PDF, I need to upload it."
> "把这个 PDF 压缩一下。"

Claude will show you a DPI menu, let you choose, then run and report the actual result.

**As a standalone CLI tool:**
```bash
# Interactive mode — guided prompts
python pdf_compress.py

# Named preset
python pdf_compress.py paper.pdf -q screen     # 72 dpi, smallest
python pdf_compress.py paper.pdf -q ebook      # 150 dpi
python pdf_compress.py paper.pdf -q printer    # 300 dpi

# Level shorthand (1–5)
python pdf_compress.py paper.pdf -l 1          # 72 dpi
python pdf_compress.py paper.pdf -l 3          # 150 dpi
python pdf_compress.py paper.pdf -l 5          # 300 dpi

# Explicit DPI
python pdf_compress.py paper.pdf --dpi 200

# Custom output directory
python pdf_compress.py paper.pdf --dpi 200 -o ~/Desktop
```

### Quality options

For typical academic papers, **200 dpi is a good starting point** — it cuts file size significantly while keeping figures readable on screen and in print.

| Option | DPI | Image quality | Good for |
|--------|-----|--------------|----------|
| `-q screen` / `-l 1` | 72 | Low — visibly softer | Quick sharing, uploading to AI |
| `-l 2` | 120 | Medium-low | Email attachments, casual reading |
| `-q ebook` / `-l 3` | 150 | Medium | Everyday screen reading |
| `-l 4` / `--dpi 200` | 200 | Medium-high | **Recommended for papers** — good balance |
| `-q printer` / `-l 5` | 300 | High | Archiving, professional printing |
| `--dpi N` | any | — | Precise control |

> Actual output size varies by PDF content and cannot be predicted in advance. Claude reports the real numbers after compression.

### Customizing

The script is intentionally simple. Edit `pdf_compress.py` to add presets or change defaults. Edit `SKILL.md` to change how Claude interprets requests or formats its responses. That's the point of keeping it as a local skill.

---

## 中文

### 动机

因为现在的论文越来越大。8、9 MB 的 PDF 已经很常见，里面塞满了图表、截图和实验结果。想把整篇论文扔给 AI 讨论，文件经常太大了，要么超过上传限制，要么把 context 耗得很快。

我找了很多在线的 PDF 压缩工具，都不太满意：要么让我付费，要么老让我注册试用，而且完全不能定制。于是写了这个简单的 Claude skill，用 Ghostscript 压缩（装不了也可以用 pikepdf 兜底），直接跟 Claude 说"帮我压缩这个 PDF"就行。

### 功能

- 使用 **Ghostscript**（首选）或 **pikepdf**（自动兜底）压缩 PDF
- 三种控制方式：命名预设、1–5 档快捷选择、或直接指定 DPI
- Claude 压缩前会给你一个 DPI 菜单让你选，压缩后只汇报真实结果，不瞎猜大小
- 自动命名输出文件为 `原文件名_compressed.pdf`，保存在同目录
- 可以作为**独立 CLI 工具**使用，也可以作为 **Claude skill** 集成
- 根据你使用的语言回复

### 两种后端

| 后端 | 安装方式 | 图片降采样 | 适合场景 |
|------|---------|-----------|---------|
| Ghostscript | 系统包管理器 | ✅ 支持 | 最大压缩率，图片多的 PDF |
| pikepdf | `pip install pikepdf` | ❌ 不支持 | 流/字体压缩，无需系统权限 |

脚本自动检测，优先用 Ghostscript，找不到再用 pikepdf。

### 安装

**1. 获取代码**
```bash
git clone https://github.com/gaoxin492/pdf-compressor
cd pdf-compressor
```

**2. 安装 Ghostscript**

强烈推荐 Ghostscript。最省事的方式是运行附带的安装脚本，会自动识别操作系统：

```bash
bash install_gs.sh
```

也可以手动安装：

```bash
# macOS（需要 Homebrew — 没有的话先装：https://brew.sh）
brew install ghostscript

# Ubuntu / Debian
sudo apt install ghostscript

# Fedora
sudo dnf install ghostscript

# Arch
sudo pacman -S ghostscript

# Windows — 有 winget 的话一行搞定：
winget install ArtifexSoftware.GhostScript
# 或者下载安装包：https://www.ghostscript.com/download/gsdnld.html
```

> **没有系统安装权限？** 脚本会自动降级到 pikepdf（`pip install pikepdf`），效果会打折扣但不需要任何系统权限。

**3. 添加为 Claude skill**

Claude Code 从你配置的目录读取 skill，按以下步骤设置：

```bash
mkdir -p ~/.claude/skills
mv pdf-compressor ~/.claude/skills/
```

然后打开（或创建）`~/.claude/CLAUDE.md`，加入：

```markdown
## Skills
@~/.claude/skills/pdf-compressor/SKILL.md
```

下次启动 Claude Code 时 skill 就自动生效了。

> **验证是否加载成功**：问 Claude "你有哪些 skill？"，它应该会提到 PDF 压缩。

### 使用方式

**作为 Claude skill** — 直接用自然语言说：
> "帮我把这篇论文压缩一下。"
> "这个 PDF 太大了，帮我压一下，我要上传给 AI。"
> "Compress this paper."

Claude 会先给你一个 DPI 选项让你选，压缩后汇报真实结果。

**作为独立 CLI 工具：**
```bash
# 交互模式
python pdf_compress.py

# 命名预设
python pdf_compress.py paper.pdf -q screen     # 72 dpi，最小
python pdf_compress.py paper.pdf -q ebook      # 150 dpi
python pdf_compress.py paper.pdf -q printer    # 300 dpi

# 1–5 档快捷选择
python pdf_compress.py paper.pdf -l 1          # 72 dpi
python pdf_compress.py paper.pdf -l 3          # 150 dpi
python pdf_compress.py paper.pdf -l 5          # 300 dpi

# 直接指定 DPI
python pdf_compress.py paper.pdf --dpi 200

# 指定输出目录
python pdf_compress.py paper.pdf --dpi 200 -o ~/Desktop
```

### 质量选项

日常论文压缩推荐从 **200 dpi** 开始，压缩幅度明显，图表在屏幕和打印时都还清晰。

| 选项 | DPI | 图片质量 | 适合场景 |
|------|-----|---------|---------|
| `-q screen` / `-l 1` | 72 | 低，明显模糊 | 快速分享、上传给 AI |
| `-l 2` | 120 | 中低 | 邮件附件、随手阅读 |
| `-q ebook` / `-l 3` | 150 | 中 | 日常屏幕阅读 |
| `-l 4` / `--dpi 200` | 200 | 中高 | **推荐起点** — 论文压缩的好平衡 |
| `-q printer` / `-l 5` | 300 | 高 | 归档、专业打印 |
| `--dpi N` | 任意 | — | 精确控制 |

> 实际压缩后的文件大小取决于 PDF 内容，无法事先预测。Claude 压缩完成后会汇报真实数字。

### 定制

脚本故意写得很简单，方便修改。改 `pdf_compress.py` 可以增加预设或调整默认值；改 `SKILL.md` 可以调整 Claude 理解用户意图的方式和回复格式。

---

## Files

```
pdf-compressor/
├── pdf_compress.py   # The compression script (CLI + agent mode)
├── SKILL.md          # Claude skill definition
├── install_gs.sh     # One-command Ghostscript installer (auto-detects OS)
└── README.md         # This file
```

## License

MIT
