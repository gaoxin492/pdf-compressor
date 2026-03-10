#!/usr/bin/env python3
"""
PDF Compressor
Primary:  Ghostscript (best compression, supports image downsampling)
Fallback: pikepdf    (pip install pikepdf, no system dependencies)

Usage: python pdf_compress.py [file] [options]
"""

import subprocess
import sys
import shutil
import argparse
from pathlib import Path


# ── Terminal colors ───────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"
    DIM    = "\033[2m"

AGENT_MODE = False

def ok(msg):
    if AGENT_MODE: print(f"[OK] {msg}")
    else: print(f"  {C.GREEN}✔{C.RESET}  {msg}")

def info(msg):
    if AGENT_MODE: print(f"[INFO] {msg}")
    else: print(f"  {C.CYAN}ℹ{C.RESET}  {msg}")

def warn(msg):
    if AGENT_MODE: print(f"[WARN] {msg}")
    else: print(f"  {C.YELLOW}⚠{C.RESET}  {msg}")

def err(msg):
    if AGENT_MODE: print(f"[ERROR] {msg}")
    else: print(f"  {C.RED}✘{C.RESET}  {msg}")

def sep():
    if not AGENT_MODE:
        print(f"  {C.DIM}{'─' * 48}{C.RESET}")


# ── Presets and DPI levels ────────────────────────────────────
# Named presets: (gs_setting, dpi, description)
PRESETS = {
    "screen":  ("/screen",   72,  "Screen / sharing (72 dpi, smallest)"),
    "ebook":   ("/ebook",    150, "E-book / general (150 dpi, recommended)"),
    "printer": ("/printer",  300, "Print (300 dpi, high quality)"),
    "prepress":("/prepress", 300, "Prepress (300 dpi, color-accurate)"),
}

# Custom DPI levels (1–4 shorthand, or any integer via --dpi)
DPI_LEVELS = {
    1: (50,  "Aggressive — roughly 1/6 of ebook quality"),
    2: (72,  "Screen — same as 'screen' preset"),
    3: (120, "Moderate — between screen and ebook"),
    4: (150, "Standard — same as 'ebook' preset"),
}


# ── Backend detection ─────────────────────────────────────────
def find_gs() -> str | None:
    for name in ["gs", "gswin64c", "gswin32c"]:
        if shutil.which(name):
            return name
    return None

def find_pikepdf() -> bool:
    try:
        import pikepdf  # noqa: F401
        return True
    except ImportError:
        return False


def human_size(n_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n_bytes < 1024:
            return f"{n_bytes:.1f} {unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f} GB"


# ── Compression backends ──────────────────────────────────────
def compress_gs(input_path: Path, output_path: Path,
                gs_setting: str, dpi: int, gs: str) -> bool:
    cmd = [
        gs, "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.5",
        f"-dPDFSETTINGS={gs_setting}",
        "-dNOPAUSE", "-dQUIET", "-dBATCH",
        "-dDetectDuplicateImages=true",
        "-dCompressFonts=true",
        f"-dColorImageResolution={dpi}",
        f"-dGrayImageResolution={dpi}",
        f"-dMonoImageResolution={min(dpi * 2, 600)}",
        "-dColorImageDownsampleType=/Bicubic",
        "-dGrayImageDownsampleType=/Bicubic",
        "-dDownsampleColorImages=true",
        "-dDownsampleGrayImages=true",
        f"-sOutputFile={output_path}",
        str(input_path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            err(f"Ghostscript error: {result.stderr.strip()}")
            return False
        return True
    except FileNotFoundError:
        err(f"Ghostscript executable not found: {gs}")
        return False


def compress_pikepdf(input_path: Path, output_path: Path) -> bool:
    try:
        import pikepdf
        with pikepdf.open(str(input_path)) as pdf:
            pdf.save(
                str(output_path),
                compress_streams=True,
                object_stream_mode=pikepdf.ObjectStreamMode.generate,
                recompress_flate=True,
            )
        return True
    except Exception as e:
        err(f"pikepdf error: {e}")
        return False


# ── Output path helper ────────────────────────────────────────
def make_output_path(input_path: Path, output_dir: Path | None) -> Path:
    out_dir = output_dir if output_dir else input_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / (input_path.stem + "_compressed.pdf")
    counter = 1
    while output_path.exists():
        output_path = out_dir / f"{input_path.stem}_compressed_{counter}.pdf"
        counter += 1
    return output_path


# ── Main ──────────────────────────────────────────────────────
def main():
    global AGENT_MODE

    parser = argparse.ArgumentParser(
        prog="pdf_compress",
        description="PDF Compressor — Ghostscript (primary) + pikepdf (fallback)",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "DPI shorthand levels (--level):\n"
            + "\n".join(f"  {k}  {v[0]:>4} dpi  {v[1]}" for k, v in DPI_LEVELS.items())
        ),
    )
    parser.add_argument("input", nargs="?", help="Input PDF file path")
    parser.add_argument("-o", "--output-dir",
                        help="Output directory (default: same as input)", default=None)

    quality_group = parser.add_mutually_exclusive_group()
    quality_group.add_argument(
        "-q", "--quality",
        choices=list(PRESETS.keys()),
        default=None,
        help="Named preset: screen / ebook (default) / printer / prepress",
    )
    quality_group.add_argument(
        "-l", "--level",
        type=int, choices=list(DPI_LEVELS.keys()),
        default=None,
        help="DPI shorthand: 1 (50dpi) / 2 (72dpi) / 3 (120dpi) / 4 (150dpi)",
    )
    quality_group.add_argument(
        "--dpi",
        type=int,
        default=None,
        metavar="N",
        help="Explicit DPI value, e.g. --dpi 100",
    )

    parser.add_argument("--gs", help="Path to Ghostscript executable", default=None)
    parser.add_argument("--no-fallback", action="store_true",
                        help="Fail instead of falling back to pikepdf")
    parser.add_argument("--agent", action="store_true",
                        help="Agent mode: plain text output, no colors, no interactive prompts")

    args = parser.parse_args()
    AGENT_MODE = args.agent

    if not AGENT_MODE:
        print()
        print(f"  {C.BOLD}PDF Compressor{C.RESET}  {C.DIM}Ghostscript + pikepdf{C.RESET}")
        sep()

    # ── Detect backend ────────────────────────────────────────
    gs = args.gs or find_gs()
    has_pike = find_pikepdf()

    if gs:
        backend = "ghostscript"
        ok(f"Ghostscript ready ({shutil.which(gs)})")
    elif not args.no_fallback and has_pike:
        backend = "pikepdf"
        warn("Ghostscript not found — falling back to pikepdf.")
        warn("Image downsampling unavailable; compression will be moderate.")
        info("For best results, install Ghostscript:")
        if not AGENT_MODE:
            print()
            print("    macOS:          brew install ghostscript")
            print("    Ubuntu/Debian:  sudo apt install ghostscript")
            print("    Fedora:         sudo dnf install ghostscript")
            print("    Arch:           sudo pacman -S ghostscript")
            print("    Windows:        winget install ArtifexSoftware.GhostScript")
            print()
    else:
        err("No compression backend available.")
        if not AGENT_MODE:
            print()
            print("  Option A — Install Ghostscript (recommended):")
            print("    macOS:         brew install ghostscript")
            print("    Ubuntu/Debian: sudo apt install ghostscript")
            print("    Windows:       winget install ArtifexSoftware.GhostScript")
            print()
            print("  Option B — Install pikepdf (pure Python, no system install needed):")
            print("    pip install pikepdf")
            print()
        sys.exit(1)

    if AGENT_MODE:
        print(f"RESULT_BACKEND: {backend}")

    # ── Input file ────────────────────────────────────────────
    if args.input:
        input_str = args.input.strip()
    elif AGENT_MODE:
        err("Input file path is required in --agent mode")
        sys.exit(1)
    else:
        sep()
        input_str = input(f"  {C.CYAN}?{C.RESET}  PDF file path: ").strip().strip('"').strip("'")

    input_path = Path(input_str)
    if not input_path.exists():
        err(f"File not found: {input_path}")
        sys.exit(1)
    if input_path.suffix.lower() != ".pdf":
        warn("File extension is not .pdf — attempting compression anyway")

    output_path = make_output_path(
        input_path, Path(args.output_dir) if args.output_dir else None
    )
    orig_size = input_path.stat().st_size

    # ── Resolve DPI and GS setting ────────────────────────────
    if args.dpi:
        dpi = args.dpi
        gs_setting = "/screen"   # use screen as base when DPI is explicit
        preset_label = f"custom DPI={dpi}"
    elif args.level:
        dpi, desc = DPI_LEVELS[args.level][0], DPI_LEVELS[args.level][1]
        gs_setting = "/screen"
        preset_label = f"level {args.level} ({dpi} dpi)"
    elif args.quality:
        gs_setting, dpi, desc = PRESETS[args.quality]
        preset_label = f"{args.quality} ({dpi} dpi)"
    elif AGENT_MODE:
        gs_setting, dpi, desc = PRESETS["ebook"]
        preset_label = "ebook (default, 150 dpi)"
        info("No quality specified — using default: ebook")
    else:
        # Interactive
        sep()
        print(f"  {C.CYAN}?{C.RESET}  Select compression level:")
        print()
        print(f"    [1] {C.BOLD}screen  {C.RESET} {C.DIM}72 dpi  — smallest size, for sharing{C.RESET}")
        print(f"    [2] {C.BOLD}ebook   {C.RESET} {C.DIM}150 dpi — balanced  {C.GREEN}← default{C.RESET}")
        print(f"    [3] {C.BOLD}printer {C.RESET} {C.DIM}300 dpi — high quality, for printing{C.RESET}")
        print(f"    [4] {C.BOLD}prepress{C.RESET} {C.DIM}300 dpi — color-accurate, for publishing{C.RESET}")
        print(f"    [5] {C.BOLD}custom  {C.RESET} {C.DIM}enter your own DPI value{C.RESET}")
        print()
        raw = input(f"  Enter [1-5] (Enter for default ebook): ").strip()
        mapping = {"1": "screen", "2": "ebook", "3": "printer", "4": "prepress"}
        if raw == "" or raw == "2":
            gs_setting, dpi, _ = PRESETS["ebook"]
            preset_label = "ebook (150 dpi)"
        elif raw in mapping:
            key = mapping[raw]
            gs_setting, dpi, _ = PRESETS[key]
            preset_label = f"{key} ({dpi} dpi)"
        elif raw == "5":
            raw_dpi = input(f"  Enter DPI (e.g. 100): ").strip()
            try:
                dpi = int(raw_dpi)
                gs_setting = "/screen"
                preset_label = f"custom ({dpi} dpi)"
            except ValueError:
                warn("Invalid DPI — using default: ebook (150 dpi)")
                gs_setting, dpi, _ = PRESETS["ebook"]
                preset_label = "ebook (150 dpi)"
        else:
            warn("Invalid input — using default: ebook (150 dpi)")
            gs_setting, dpi, _ = PRESETS["ebook"]
            preset_label = "ebook (150 dpi)"

    # ── Compress ──────────────────────────────────────────────
    sep()
    info(f"Input:    {input_path.name}  ({human_size(orig_size)})")
    info(f"Output:   {output_path}")
    info(f"Quality:  {preset_label}")
    info(f"Backend:  {backend}")
    sep()
    if not AGENT_MODE:
        print(f"  {C.YELLOW}⏳ Compressing…{C.RESET}")

    if backend == "ghostscript":
        success = compress_gs(input_path, output_path, gs_setting, dpi, gs)
    else:
        success = compress_pikepdf(input_path, output_path)

    if not success:
        sys.exit(1)

    if not output_path.exists() or output_path.stat().st_size == 0:
        err("Output file is empty — compression failed")
        sys.exit(1)

    # ── Results ───────────────────────────────────────────────
    new_size = output_path.stat().st_size
    ratio    = (1 - new_size / orig_size) * 100 if orig_size > 0 else 0

    sep()
    if new_size >= orig_size:
        warn("Compressed file is larger than the original (already optimized)")
        warn("Try a lower DPI or the 'screen' preset")
    else:
        ok("Done!")

    print()
    print(f"RESULT_ORIGINAL_SIZE: {orig_size}")
    print(f"RESULT_COMPRESSED_SIZE: {new_size}")
    print(f"RESULT_RATIO: {ratio:.1f}")
    print(f"RESULT_OUTPUT_PATH: {output_path.resolve()}")
    print(f"RESULT_BACKEND: {backend}")
    print(f"RESULT_DPI: {dpi}")
    print()

    if not AGENT_MODE:
        print(f"    Original    {C.DIM}{human_size(orig_size):>10}{C.RESET}")
        print(f"    Compressed  {C.BOLD}{human_size(new_size):>10}{C.RESET}  "
              f"{C.GREEN if ratio > 0 else C.YELLOW}▼ {abs(ratio):.1f}%{C.RESET}")
        print(f"    Saved to    {C.CYAN}{output_path.name}{C.RESET}")
        print(f"    Backend     {C.DIM}{backend}{C.RESET}")
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {C.DIM}Cancelled{C.RESET}\n")
        sys.exit(0)