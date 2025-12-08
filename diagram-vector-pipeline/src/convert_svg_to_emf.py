from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional


def convert_svg_to_emf(
    svg_file: Path,
    emf_file: Path,
    *,
    inkscape_cli: Optional[str] = None,
) -> bool:
    """Convert an SVG to EMF using Inkscape CLI.

    Args:
        svg_file: Path to the source SVG.
        emf_file: Path for the EMF output.
        inkscape_cli: Optional override for the inkscape executable.

    Returns:
        True if conversion succeeds, False otherwise.
    """
    cli = inkscape_cli or os.environ.get("INKSCAPE_CLI", "inkscape")
    emf_file.parent.mkdir(parents=True, exist_ok=True)

    command = [
        cli,
        str(svg_file),
        "--export-type=emf",
        f"--export-filename={emf_file}",
    ]

    print(f"[inkscape] Converting {svg_file} -> {emf_file} with '{cli}'")

    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print(
            f"[inkscape] ERROR: Inkscape CLI '{cli}' not found. Install Inkscape and/or set INKSCAPE_CLI."
        )
        return False

    if result.returncode != 0:
        print("[inkscape] ERROR: failed to export EMF")
        if result.stdout:
            print("[inkscape] stdout:\n" + result.stdout)
        if result.stderr:
            print("[inkscape] stderr:\n" + result.stderr)
        return False

    print(f"[inkscape] EMF written to {emf_file}")
    return True


__all__ = ["convert_svg_to_emf"]
