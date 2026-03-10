#!/usr/bin/env bash
# install_gs.sh — auto-detect OS and install Ghostscript
set -e

echo ""
echo "  Ghostscript Installer"
echo "  ─────────────────────────────────────────"

# Already installed?
if command -v gs &>/dev/null; then
  echo "  ✔ Ghostscript is already installed: $(gs --version)"
  echo ""
  exit 0
fi

OS="$(uname -s 2>/dev/null || echo "Windows")"

case "$OS" in
  Darwin)
    echo "  → macOS detected."
    echo ""
    if command -v brew &>/dev/null; then
      echo "  Installing via Homebrew..."
      brew install ghostscript
    else
      echo "  Homebrew not found. You have two options:"
      echo ""
      echo "  Option A — Direct .pkg installer (no Homebrew needed, ~50 MB):"
      echo "    1. Go to: https://www.ghostscript.com/download/gsdnld.html"
      echo "    2. Download the macOS .pkg file"
      echo "    3. Double-click to install"
      echo ""
      echo "  Option B — Install Homebrew first, then Ghostscript:"
      echo "    Note: Homebrew requires Xcode Command Line Tools (~500 MB, 5-15 min)"
      echo ""
      read -r -p "  Install Homebrew automatically? [y/N] " choice
      if [[ "$choice" =~ ^[Yy]$ ]]; then
        echo "  Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        brew install ghostscript
      else
        echo ""
        echo "  → Please use the .pkg installer above, then re-run this script to verify."
        exit 0
      fi
    fi
    ;;
  Linux)
    if command -v apt-get &>/dev/null; then
      echo "  → Debian/Ubuntu detected..."
      sudo apt-get update -qq && sudo apt-get install -y ghostscript
    elif command -v dnf &>/dev/null; then
      echo "  → Fedora/RHEL detected..."
      sudo dnf install -y ghostscript
    elif command -v pacman &>/dev/null; then
      echo "  → Arch Linux detected..."
      sudo pacman -S --noconfirm ghostscript
    elif command -v zypper &>/dev/null; then
      echo "  → openSUSE detected..."
      sudo zypper install -y ghostscript
    else
      echo "  ✘ Could not detect your package manager."
      echo "    Please install Ghostscript manually:"
      echo "    https://www.ghostscript.com/download/gsdnld.html"
      exit 1
    fi
    ;;
  Windows*|MINGW*|CYGWIN*|MSYS*)
    echo "  → Windows detected."
    echo ""
    echo "  Easiest — one command if you have winget (Windows 10+):"
    echo "    winget install ArtifexSoftware.GhostScript"
    echo ""
    echo "  Or download the installer manually:"
    echo "    1. Go to: https://www.ghostscript.com/download/gsdnld.html"
    echo "    2. Download the 64-bit .exe installer"
    echo "    3. Run it (default options are fine)"
    echo "    4. Add the bin folder to PATH if not done automatically:"
    echo "       C:\\Program Files\\gs\\gs10.xx.x\\bin"
    echo ""
    exit 0
    ;;
  *)
    echo "  ✘ Unknown OS: $OS"
    echo "    Please install manually: https://www.ghostscript.com/download/gsdnld.html"
    exit 1
    ;;
esac

echo ""
if command -v gs &>/dev/null; then
  echo "  ✔ Ghostscript installed successfully: $(gs --version)"
else
  echo "  ⚠ Installation finished but 'gs' not found in PATH."
  echo "    You may need to restart your terminal."
fi
echo ""
