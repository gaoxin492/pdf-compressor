# pdf-compressor-skill

**A Claude skill for compressing PDFs — because research papers shouldn't cost you your context window.**

[English](#english) · [中文](#中文)

---

## English

### Motivation

Academic papers keep getting bigger. It's now routine to encounter 8–9 MB PDFs packed with figures, plots, and screenshots. When you want to discuss a paper in full with an AI, that size becomes a real problem — many interfaces impose file size limits, and large files chew through context budgets fast.

I kept reaching for online PDF compressors, and kept running into the same frustrations: paywalls for anything beyond basic compression, no control over quality trade-offs, and no way to adapt the tool to my workflow. So I built this: a small, hackable Claude skill that wraps Ghostscript (with a pikepdf fallback) and lets you compress any PDF by just telling Claude to do it.

### What it does

- Compresses PDFs using **Ghostscript** (primary) or **pikepdf** (automatic fallback if GS isn't installed)
- Four quality presets: `screen` · `ebook` · `printer` · `prepress`
- Auto-names output as `filename_compressed.pdf` in the same directory
- Works as a **standalone CLI tool** or as a **Claude skill** (Claude Code / compatible agents)
- Responds to the user in whatever language they use

### Backends

| Backend | Install | Image downsampling | Best for |
|---------|---------|-------------------|----------|
| Ghostscript | System package | ✅ Yes | Maximum compression, image-heavy PDFs |
| pikepdf | `pip install pikepdf` | ❌ No | Stream/font compression, easier setup |

The script tries Ghostscript first and falls back to pikepdf automatically — you don't need to think about it.

### Installation

**1. Get the files**
```bash
git clone https://github.com/<your-username>/pdf-compressor-skill
cd pdf-compressor-skill
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

# Windows — one-liner if you have winget:
winget install ArtifexSoftware.GhostScript
# Or download the installer: https://www.ghostscript.com/download/gsdnld.html
```

> **Don't have system-level install permissions?** The script will automatically fall back to pikepdf (`pip install pikepdf`), which handles stream and font compression but cannot downsample images. You'll still get some reduction, just not as much.

**3. Add as a Claude skill**

Point your Claude Code config at the skill directory:
```bash
# In your Claude Code settings, add the skill path:
~/pdf-compressor-skill/SKILL.md
```

### Usage

**As a Claude skill** — just talk to Claude naturally:
> "Compress this paper for me, as small as possible."
> "Help me reduce the size of report.pdf."
> "把这个PDF压缩一下，要能发微信的大小。"

**As a standalone CLI tool:**
```bash
# Interactive mode
python pdf_compress.py

# Direct mode
python pdf_compress.py paper.pdf -q screen
python pdf_compress.py paper.pdf -q ebook -o ~/Desktop
```

### Quality presets

| Preset | DPI | Use case |
|--------|-----|----------|
| `screen` | 72 | Sharing via email, WeChat, uploading to AI |
| `ebook` | 150 | General reading, default |
| `printer` | 300 | Printing, archiving |
| `prepress` | 300 | Publishing, color-critical work |

### Typical results

A 9 MB conference paper with lots of figures compressed to ~1.8 MB with `screen`, ~3.2 MB with `ebook` — well within most upload limits.

### Customizing

The script is intentionally simple. Edit `pdf_compress.py` to add presets, change defaults, or extend the fallback chain. Edit `SKILL.md` to change how Claude interprets user intent or formats its response.

---

## 中文

### 动机

现在的论文越来越大。8、9 MB 的 PDF 已经很常见，里面塞满了图表、截图和实验结果。想把整篇论文扔给 AI 讨论？文件太大，要么超过上传限制，要么把 context 耗得很快。

我找了很多 PDF 压缩工具，都不太满意：免费版功能阉割，付费版不便宜，而且完全不能定制。于是写了这个简单的 Claude skill，用 Ghostscript 压缩（装不了就自动用 pikepdf 兜底），直接跟 Claude 说"帮我压缩这个 PDF"就行。

### 功能

- 使用 **Ghostscript**（首选）或 **pikepdf**（自动兜底）压缩 PDF
- 四种质量预设：`screen` · `ebook` · `printer` · `prepress`
- 自动命名输出文件为 `原文件名_compressed.pdf`，保存在同目录
- 可以作为 **独立 CLI 工具** 使用，也可以作为 **Claude skill** 集成
- 根据用户语言自动回复

### 两种后端

| 后端 | 安装方式 | 图片降采样 | 适合场景 |
|------|---------|-----------|---------|
| Ghostscript | 系统包管理器 | ✅ 支持 | 最大压缩率，图片多的 PDF |
| pikepdf | `pip install pikepdf` | ❌ 不支持 | 流/字体压缩，安装更简单 |

脚本会自动检测，优先用 Ghostscript，找不到再用 pikepdf，不需要手动配置。

### 安装

**1. 获取代码**
```bash
git clone https://github.com/<your-username>/pdf-compressor-skill
cd pdf-compressor-skill
```

**2. 安装 Ghostscript**

强烈推荐安装 Ghostscript。它是唯一能对图片做降采样的后端，而这正是图片多的 PDF 压缩率最高的来源。

最省事的方式：直接运行附带的安装脚本，会自动识别操作系统。

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

> **没有系统安装权限？** 脚本会自动降级使用 pikepdf（`pip install pikepdf`），能压缩流和字体数据，但无法对图片降采样，效果会打折扣。

**3. 添加为 Claude skill**

在 Claude Code 配置中指向 skill 目录：
```bash
# 添加 SKILL.md 所在路径到 Claude Code 设置
~/pdf-compressor-skill/SKILL.md
```

### 使用方式

**作为 Claude skill** — 直接用自然语言说：
> "帮我把这篇论文压缩一下，越小越好。"
> "Compress this PDF, I need to send it over email."
> "把 report.pdf 压缩到桌面上。"

**作为独立 CLI 工具：**
```bash
# 交互模式
python pdf_compress.py

# 直接模式
python pdf_compress.py paper.pdf -q screen
python pdf_compress.py paper.pdf -q ebook -o ~/Desktop
```

### 质量预设

| 预设 | DPI | 适合场景 |
|------|-----|---------|
| `screen` | 72 | 微信发送、邮件附件、上传给 AI |
| `ebook` | 150 | 日常阅读，默认值 |
| `printer` | 300 | 打印、归档 |
| `prepress` | 300 | 出版、色彩精确要求高 |

### 典型效果

一篇图很多的 9 MB 会议论文，`screen` 预设压到约 1.8 MB，`ebook` 压到约 3.2 MB，基本能满足各类上传限制。

### 定制

脚本故意写得很简单，方便修改。改 `pdf_compress.py` 可以增加预设、调整默认值、扩展兜底逻辑；改 `SKILL.md` 可以调整 Claude 理解用户意图的方式和回复格式。这就是自己写 skill 的意义所在。

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
