---
name: pdf-compressor
description: Compress PDF files to reduce size. Uses Ghostscript when available, falls back to pikepdf automatically. Trigger when the user says things like "compress this PDF", "PDF is too large", "reduce PDF size", "compress to around 1MB", or equivalent in any language.
---

# PDF Compressor Skill

Compresses PDF files using a local Python script. Ghostscript is the primary backend (best compression, including image downsampling); pikepdf is the automatic fallback (pure Python, no system install required).

**Script location**: `<SKILL_DIRECTORY>/pdf_compress.py`

> **Language**: Always respond to the user in their language. These instructions are for Claude only.

---

## Instructions for Claude

### Step 1: Check available backends

The script auto-detects Ghostscript first, then falls back to pikepdf. If neither is available it exits with `[ERROR] No compression backend available.` Tell the user (in their language) to install at least one:

- **Ghostscript** (recommended, required for DPI control):
  - macOS: `bash install_gs.sh` or `brew install ghostscript`
  - Ubuntu/Debian: `sudo apt install ghostscript`
  - Fedora: `sudo dnf install ghostscript`
  - Arch: `sudo pacman -S ghostscript`
  - Windows: `winget install ArtifexSoftware.GhostScript`
- **pikepdf** (no system install, moderate compression): `pip install pikepdf`

### Step 2: Choose the right quality argument

The script accepts three mutually exclusive quality options. Pick the most natural one for the user's request:

**`-q` — named preset** (simplest, use when intent is clear):

| User says | `-q` value |
|-----------|-----------|
| "compress it" / no preference | `ebook` (default) |
| "smallest", "for email / WeChat / upload to AI" | `screen` |
| "for printing", "keep quality" | `printer` |
| "for publishing", "color accuracy" | `prepress` |

**`-l` — level shorthand 1–4** (use when user picks a number or wants a quick gradient):

| Level | DPI | Size estimate* |
|-------|-----|----------------|
| 1 | 50  | ~5–10% of original |
| 2 | 72  | ~10–20% (same as `screen`) |
| 3 | 120 | ~20–35% |
| 4 | 150 | ~30–50% (same as `ebook`) |

**`--dpi N` — explicit DPI** (use when user specifies DPI, or when estimating for a size target):

> When a user says "around 1MB" or "under 2MB":
> 1. Check `RESULT_ORIGINAL_SIZE` from a prior run, or ask the user the file size.
> 2. Estimate: `target_mb / original_mb` gives a rough ratio. Image-heavy PDFs compress roughly proportional to `(target_dpi / original_dpi)²`. Start from an assumed 200 dpi scan.
> 3. Pick a single DPI and run once. Tell the user the estimate is approximate and offer to adjust.
>
> **Quick heuristic table** (for a typical 8–10 MB image-heavy paper):
>
> | Target | Suggested DPI |
> |--------|--------------|
> | ~4–5 MB | `--dpi 120` |
> | ~2–3 MB | `--dpi 90` |
> | ~1–1.5 MB | `--dpi 60` |
> | < 1 MB | `--dpi 40` |

### Step 3: Run the script — always pass `--agent`

```bash
python <SKILL_DIRECTORY>/pdf_compress.py <INPUT_PATH> [quality_option] --agent
```

`--agent` is mandatory: disables prompts, strips ANSI, emits `RESULT_*` lines.

**Examples:**
```bash
# Named preset
python ~/skills/pdf_compress.py paper.pdf -q screen --agent
python ~/skills/pdf_compress.py paper.pdf -q ebook --agent

# Level shorthand
python ~/skills/pdf_compress.py paper.pdf -l 1 --agent
python ~/skills/pdf_compress.py paper.pdf -l 3 --agent

# Explicit DPI (e.g. user wants ~1MB from a 9MB file)
python ~/skills/pdf_compress.py paper.pdf --dpi 60 --agent

# Custom output directory
python ~/skills/pdf_compress.py paper.pdf -q ebook -o ~/Downloads --agent
```

### Step 4: Parse output and report to user

Look for these lines in stdout:

```
RESULT_ORIGINAL_SIZE: <bytes>
RESULT_COMPRESSED_SIZE: <bytes>
RESULT_RATIO: <float>           # positive = reduction
RESULT_OUTPUT_PATH: <path>
RESULT_BACKEND: ghostscript | pikepdf
RESULT_DPI: <int>
```

Report in the user's language: original size, compressed size, reduction %, output path. If the file grew instead of shrinking (`RESULT_RATIO` ≤ 0), explain it was already well-optimized and suggest a lower DPI or `screen` preset. Offer to re-run with a different setting if the result doesn't match expectations.

---

## Quick reference

```
# Named presets
pdf_compress.py <input> -q screen   --agent   # 72 dpi, smallest
pdf_compress.py <input> -q ebook    --agent   # 150 dpi, default
pdf_compress.py <input> -q printer  --agent   # 300 dpi
pdf_compress.py <input> -q prepress --agent   # 300 dpi, color

# Level shorthand (1=50dpi … 4=150dpi)
pdf_compress.py <input> -l 1 --agent
pdf_compress.py <input> -l 3 --agent

# Explicit DPI
pdf_compress.py <input> --dpi 80 --agent

# Options
  -o <dir>          Custom output directory
  --no-fallback     Require Ghostscript, don't use pikepdf
  --gs <path>       Manually specify Ghostscript path
```