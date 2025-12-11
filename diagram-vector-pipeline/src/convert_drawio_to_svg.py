from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional


def convert_drawio_to_svg(
    drawio_file: Path,
    svg_file: Path,
    drawio_cli: Optional[str] = None,
) -> bool:
    """
    Convert a .drawio file to an SVG using the diagrams.net CLI.

    I always try to respect the requested output path, but if the CLI ignores
    the --output argument and writes next to the input file, I will move that
    file into the requested location.
    """

    cli = drawio_cli or os.environ.get("DRAWIO_CLI", "drawio")

    # I make sure the target directory exists before calling the CLI.
    svg_file.parent.mkdir(parents=True, exist_ok=True)

    command = [
        cli,
        "--export",
        "--format",
        "svg",
        "--output",
        str(svg_file),
        str(drawio_file),
    ]

    print(f"[draw.io] Converting {drawio_file} -> {svg_file} with '{cli}'")
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[draw.io] CLI returned non-zero exit code: {result.returncode}")
        print("[draw.io] stderr:")
        print(result.stderr)
        return False

    # If the CLI ignored --output, it might have written next to the input file.
    if not svg_file.exists():
        fallback = drawio_file.with_suffix(".svg")
        if fallback.exists():
            print(f"[draw.io] Output not found at {svg_file}, using fallback {fallback}")
            fallback.rename(svg_file)

    if not svg_file.exists():
        print(f"[draw.io] Expected SVG at {svg_file} but the file does not exist")
        return False

    print(f"[draw.io] SVG written to {svg_file}")
    return True
