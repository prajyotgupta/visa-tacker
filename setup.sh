#!/bin/sh
# ---------------------------------------------------------------------------
# setup.sh — one-command bootstrap for visa-tracker
#
# Compatible with: bash, zsh, sh, dash, csh/tcsh (via sh -c fallback)
#
# Usage:
#   source setup.sh        (bash / zsh / sh)
#   source setup.sh        (tcsh / csh — delegates to sh internally)
#   ./setup.sh             (any shell, but venv won't persist in caller)
# ---------------------------------------------------------------------------

set -e

# ---- Helpers --------------------------------------------------------------

log()   { printf "\033[1;34m==>\033[0m %s\n" "$1"; }
warn()  { printf "\033[1;33mWARN:\033[0m %s\n" "$1"; }
err()   { printf "\033[1;31mERROR:\033[0m %s\n" "$1"; }

# ---- Resolve project root (directory this script lives in) ----------------

if [ -n "$BASH_SOURCE" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$BASH_SOURCE")" && pwd)"
elif [ -n "$ZSH_VERSION" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
else
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
fi

cd "$SCRIPT_DIR"
log "Project root: $SCRIPT_DIR"

# ---- Check Python >= 3.10 ------------------------------------------------

PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        ver=$("$candidate" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        major=$(echo "$ver" | cut -d. -f1)
        minor=$(echo "$ver" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    err "Python >= 3.10 is required but not found. Please install it first."
    return 1 2>/dev/null || exit 1
fi

log "Using Python: $PYTHON ($ver)"

# ---- Check for Tesseract OCR engine --------------------------------------

if ! command -v tesseract >/dev/null 2>&1; then
    warn "tesseract-ocr not found. OCR will fail at runtime."
    case "$(uname -s)" in
        Darwin)  warn "  Install with:  brew install tesseract" ;;
        Linux)   warn "  Install with:  sudo apt-get install tesseract-ocr" ;;
        *)       warn "  Install Tesseract from: https://github.com/tesseract-ocr/tesseract" ;;
    esac
else
    log "Tesseract found: $(tesseract --version 2>&1 | head -1)"
fi

# ---- Install uv if missing -----------------------------------------------

if ! command -v uv >/dev/null 2>&1; then
    log "Installing uv ..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

log "Using uv: $(uv --version)"

# ---- Sync dependencies via uv --------------------------------------------

log "Syncing dependencies ..."
uv sync

# ---- Create images/ dir (download target for media) ----------------------

mkdir -p images

# ---- Activate the virtual environment for the caller's shell -------------

VENV_DIR="$SCRIPT_DIR/.venv"

if [ -f "$VENV_DIR/bin/activate" ]; then
    # Works in bash, zsh, sh, dash
    . "$VENV_DIR/bin/activate"
    log "Virtual environment activated (.venv)"
else
    warn "Could not locate .venv/bin/activate — run 'uv sync' manually."
fi

# ---- Done -----------------------------------------------------------------

log "Setup complete! Run the bot with:"
log "  uv run visa_listener.py"
