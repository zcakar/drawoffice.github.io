from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional


def convert_drawio_to_svg(
    drawio_file: Path,
    svg_file: Path,
    *,
    drawio_cli: Optional[str] = None,
) -> bool:
    """Convert a .drawio file to SVG using the diagrams.net CLI.

    Args:
        drawio_file: Path to the input .drawio file.
        svg_file: Path to write the SVG output.
        drawio_cli: Optional override for the draw.io CLI executable.

    Returns:
        True if the conversion succeeds, False otherwise.
    """
    cli = drawio_cli or os.environ.get("DRAWIO_CLI", "drawio")
    svg_file.parent.mkdir(parents=True, exist_ok=True)

    command = [
        cli,
        "--export",
        "--format",
        "svg",
        "--embed-fonts",
        "--embed-images",
        "--uncompressed",
        "--output",
        str(svg_file),
        str(drawio_file),
    ]

    print(f"[draw.io] Converting {drawio_file} -> {svg_file} with '{cli}'")

    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print(
            f"[draw.io] ERROR: draw.io CLI '{cli}' not found. Install draw.io/diagrams.net desktop or set DRAWIO_CLI."
        )
        return False

    if result.returncode != 0:
        print("[draw.io] ERROR: failed to export SVG")
        if result.stdout:
            print("[draw.io] stdout:\n" + result.stdout)
        if result.stderr:
            print("[draw.io] stderr:\n" + result.stderr)
        return False

    print(f"[draw.io] SVG written to {svg_file}")
    return True


__all__ = ["convert_drawio_to_svg"]
