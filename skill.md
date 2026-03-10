---
name: pdf-compressor
description: Compress PDF files to reduce size. Uses Ghostscript when available, falls back to pikepdf automatically. Trigger when the user says things like "compress this PDF", "PDF is too large", "reduce PDF size", or equivalent in any language.
---

# PDF Compressor Skill

Compresses PDF files using a local Python script. Ghostscript is the primary backend (best compression, including image downsampling); pikepdf is the automatic fallback (pure Python, no system install required).

**Script location**: `<SKILL_DIRECTORY>/pdf_compress.py`

> **Language**: Always respond to the user in their language. These instructions are for Claude only.

---

## Instructions for Claude

### Step 1: Clarify intent BEFORE running anything

When this skill is triggered, **do not run the script immediately**. Ask the user to pick a DPI level. Respond in the user's language.

Present a menu like this (adapt tone naturally):

---
To compress your PDF, please pick a DPI level. Higher DPI = better image quality, larger file. Lower DPI = smaller file, softer images.

| Option | DPI | Image quality | Good for |
|--------|-----|---------------|----------|
| 1 | 72 dpi | Low — visibly softer | Uploading to AI, quick sharing |
| 2 | 120 dpi | Medium-low | Email attachments, casual reading |
| 3 | 150 dpi | Medium | Everyday screen reading (recommended) |
| 4 | 200 dpi | Medium-high | HiDPI screens, occasional printing |
| 5 | 300 dpi | High | Archiving, professional printing |

Which one would you like? You can also type a custom DPI if you have a specific value in mind.

---

**Do not predict or estimate the output file size.** The actual result depends on the number of images, their original resolution, and content — estimates are unreliable. Let the real output speak for itself.

Skip this step only if the user already specifies a DPI or preset explicitly (e.g. "use 150 dpi", "screen preset", "make it as small as possible" → use 72 dpi).

### Step 2: Map user choice to script argument

Once the user picks a level or DPI, map it directly:

| User picks | Script argument |
|------------|----------------|
| Option 1 / "72 dpi" / "smallest" | `--dpi 72` |
| Option 2 / "120 dpi" | `--dpi 120` |
| Option 3 / "150 dpi" / "balanced" / no preference | `--dpi 150` or `-q ebook` |
| Option 4 / "200 dpi" | `--dpi 200` |
| Option 5 / "300 dpi" / "for printing" | `--dpi 300` or `-q printer` |
| Custom value N | `--dpi N` |

Named presets (`-q`) are fine for the standard cases; use `--dpi` for anything in between.

### Step 3: Run the script — always pass `--agent`

```bash
python <SKILL_DIRECTORY>/pdf_compress.py <INPUT_PATH> [quality_option] --agent
```

`--agent` is mandatory: disables interactive prompts, strips ANSI codes, emits structured `RESULT_*` lines.

**Examples:**
```bash
python ~/skills/pdf_compress.py paper.pdf --dpi 72  --agent
python ~/skills/pdf_compress.py paper.pdf --dpi 150 --agent
python ~/skills/pdf_compress.py paper.pdf --dpi 200 --agent
python ~/skills/pdf_compress.py paper.pdf -q ebook  --agent
python ~/skills/pdf_compress.py paper.pdf -q screen --agent
python ~/skills/pdf_compress.py paper.pdf --dpi 150 -o ~/Downloads --agent
```

### Step 4: Report the real result

Look for these lines in stdout:

```
RESULT_ORIGINAL_SIZE: <bytes>
RESULT_COMPRESSED_SIZE: <bytes>
RESULT_RATIO: <float>           # positive = size reduction %
RESULT_OUTPUT_PATH: <path>
RESULT_BACKEND: ghostscript | pikepdf
RESULT_DPI: <int>
```

Report the **actual** numbers from the output — never estimate or predict sizes. Include: original size, compressed size, reduction %, output path.

Offer to re-run with a different DPI if the user wants a different trade-off. Example: "Result is 3.8 MB at 200 dpi. Want me to try 120 dpi for a smaller file, or 300 dpi for higher quality?"

**If `RESULT_RATIO` ≤ 0**: the file was already well-optimized. Explain this and suggest trying a lower DPI.

---

## Quick reference

```
pdf_compress.py <input> --dpi 72  --agent   # smallest
pdf_compress.py <input> --dpi 120 --agent
pdf_compress.py <input> --dpi 150 --agent   # default / ebook
pdf_compress.py <input> --dpi 200 --agent
pdf_compress.py <input> --dpi 300 --agent   # print quality

pdf_compress.py <input> -q screen   --agent  # 72 dpi
pdf_compress.py <input> -q ebook    --agent  # 150 dpi
pdf_compress.py <input> -q printer  --agent  # 300 dpi

# Options
  -o <dir>          Custom output directory
  --no-fallback     Require Ghostscript, don't use pikepdf
  --gs <path>       Manually specify Ghostscript path
```