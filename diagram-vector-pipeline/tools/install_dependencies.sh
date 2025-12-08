#!/usr/bin/env bash
set -euo pipefail

# Minimal helper for Debian/Ubuntu hosts.
# Installs draw.io (diagrams.net) and Inkscape from apt repositories.

if ! command -v sudo >/dev/null 2>&1; then
  echo "[install] sudo is required to install packages on this system." >&2
  exit 1
fi

sudo apt-get update
sudo apt-get install -y inkscape drawio

cat <<'MSG'
[install] Dependencies installed.
- drawio CLI: run 'drawio --help' to verify.
- Inkscape CLI: run 'inkscape --version' to verify.

If packages are missing in your distribution, install manually:
- Inkscape: https://inkscape.org/release
- diagrams.net desktop: https://github.com/jgraph/drawio-desktop/releases
MSG
