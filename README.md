# pdf-compressor-skill

**A simple Claude skill for compressing PDFs.**

[English](#english) · [中文](#中文)

---

## English

### Motivation

Academic papers keep getting bigger. It's now routine to encounter 8–9 MB PDFs packed with figures, plots, and screenshots. When you want to discuss a paper in full with an AI, that size becomes a real problem — many interfaces impose file size limits, and large files chew through context budgets fast.

I kept reaching for online PDF compressors, and kept running into the same frustrations: paywalls for anything beyond basic compression, no control over quality trade-offs, and no way to adapt the tool to my workflow. So I built this: a small, hackable Claude skill that wraps Ghostscript (with a pikepdf fallback) and lets you compress any PDF by just telling Claude to do it.

### What it does

- Compresses PDFs using **Ghostscript** (primary) or **pikepdf** (automatic fallback if GS isn't installed)
- Three ways to control quality: named presets, 1–4 level shorthand, or explicit DPI
- When you say "around 1MB", Claude estimates the right DPI and runs once — no slow multi-pass search
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
git clone https://github.com/<your-username>/pdf-compressor-skill
cd pdf-compressor-skill
```

**2. Install Ghostscript**

Ghostscript is strongly recommended — it's the only backend that can downsample images, which is where most of the savings come from in image-heavy PDFs.

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

```bash
# Point your Claude Code config at the skill directory
~/pdf-compressor-skill/SKILL.md
```

### Usage

**As a Claude skill** — just talk naturally:
> "Compress this paper, as small as possible."
> "I need this PDF under 2MB for email."
> "把这个PDF压缩到1MB左右。"

Claude picks the right settings and runs once — no back-and-forth.

**As a standalone CLI tool:**
```bash
# Interactive mode — guided prompts
python pdf_compress.py

# Named preset
python pdf_compress.py paper.pdf -q screen     # 72 dpi, smallest
python pdf_compress.py paper.pdf -q ebook      # 150 dpi, default
python pdf_compress.py paper.pdf -q printer    # 300 dpi

# Level shorthand (1–4)
python pdf_compress.py paper.pdf -l 1          # 50 dpi, aggressive
python pdf_compress.py paper.pdf -l 3          # 120 dpi, moderate

# Explicit DPI
python pdf_compress.py paper.pdf --dpi 80

# Custom output directory
python pdf_compress.py paper.pdf -q ebook -o ~/Desktop
```

### Quality options

| Option | DPI | Typical size* | Use case |
|--------|-----|--------------|----------|
| `-q screen` / `-l 2` | 72 | ~10–20% of original | Sharing, uploading to AI |
| `-q ebook` / `-l 4` | 150 | ~30–50% | General reading (default) |
| `-q printer` | 300 | ~60–80% | Printing, archiving |
| `-l 1` | 50 | ~5–10% | Aggressive, last resort |
| `-l 3` | 120 | ~20–35% | Between screen and ebook |
| `--dpi N` | any | varies | Precise control |

*Estimates for a typical 8–10 MB image-heavy conference paper.

### Typical results

A 9 MB CVPR paper with lots of figures: `screen` → ~1.5 MB, `ebook` → ~3 MB. Well within most upload limits.

### Customizing

The script is intentionally simple. Edit `pdf_compress.py` to add presets or change defaults. Edit `SKILL.md` to change how Claude interprets requests or formats its response. This is the point of keeping it as a local skill.

---

## 中文

### 动机

现在的论文越来越大。8、9 MB 的 PDF 已经很常见，里面塞满了图表、截图和实验结果。想把整篇论文扔给 AI 讨论？文件太大，要么超过上传限制，要么把 context 耗得很快。

我找了很多 PDF 压缩工具，都不太满意：免费版功能阉割，付费版不便宜，而且完全不能定制。于是写了这个简单的 Claude skill，用 Ghostscript 压缩（装不了就自动用 pikepdf 兜底），直接跟 Claude 说"帮我压缩这个 PDF"就行。

### 功能

- 使用 **Ghostscript**（首选）或 **pikepdf**（自动兜底）压缩 PDF
- 三种控制方式：命名预设、1–4 档快捷选择、或直接指定 DPI
- 说"压缩到 1MB 左右"，Claude 估算好 DPI 一次搞定，不反复尝试
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
git clone https://github.com/<your-username>/pdf-compressor-skill
cd pdf-compressor-skill
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

```bash
# 在 Claude Code 配置中指向 skill 目录
~/pdf-compressor-skill/SKILL.md
```

### 使用方式

**作为 Claude skill** — 直接用自然语言说：
> "帮我把这篇论文压缩一下，越小越好。"
> "压缩到 1MB 左右，要发微信。"
> "Compress this, I need it under 2MB."

Claude 估算好参数，一次执行，不需要你来回调整。

**作为独立 CLI 工具：**
```bash
# 交互模式
python pdf_compress.py

# 命名预设
python pdf_compress.py paper.pdf -q screen     # 72 dpi，最小
python pdf_compress.py paper.pdf -q ebook      # 150 dpi，默认
python pdf_compress.py paper.pdf -q printer    # 300 dpi

# 1–4 档快捷选择
python pdf_compress.py paper.pdf -l 1          # 50 dpi，激进压缩
python pdf_compress.py paper.pdf -l 3          # 120 dpi，中等

# 直接指定 DPI
python pdf_compress.py paper.pdf --dpi 80

# 指定输出目录
python pdf_compress.py paper.pdf -q ebook -o ~/Desktop
```

### 质量选项

| 选项 | DPI | 典型大小* | 适合场景 |
|------|-----|---------|---------|
| `-q screen` / `-l 2` | 72 | 原始的 10–20% | 分享、上传给 AI |
| `-q ebook` / `-l 4` | 150 | 原始的 30–50% | 日常阅读（默认） |
| `-q printer` | 300 | 原始的 60–80% | 打印、归档 |
| `-l 1` | 50 | 原始的 5–10% | 激进压缩，最后手段 |
| `-l 3` | 120 | 原始的 20–35% | screen 和 ebook 之间 |
| `--dpi N` | 任意 | 因文件而异 | 精确控制 |

*基于典型的 8–10 MB 图片多的会议论文估算。

### 典型效果

一篇 9 MB 的 CVPR 论文（图很多）：`screen` 压到约 1.5 MB，`ebook` 压到约 3 MB，基本满足各类上传限制。

### 定制

脚本故意写得很简单，方便修改。改 `pdf_compress.py` 可以增加预设或调整默认值；改 `SKILL.md` 可以调整 Claude 理解用户意图的方式和回复格式。

---

## Files

```
pdf-compressor-skill/
├── pdf_compress.py   # The compression script (CLI + agent mode)
├── SKILL.md          # Claude skill definition
├── install_gs.sh     # One-command Ghostscript installer (auto-detects OS)
└── README.md         # This file
```

## License

MIT
