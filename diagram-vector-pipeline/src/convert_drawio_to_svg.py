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
    Convert a .drawio file to an SVG using LibreOffice and ImageMagick.
    """

    # Ensure target directory exists
    svg_file.parent.mkdir(parents=True, exist_ok=True)

    # Step 1: Convert DrawIO to PNG using LibreOffice
    png_file = svg_file.parent / "temp_conversion.png"
    
    command_png = [
        "libreoffice",
        "--headless",
        "--convert-to", "png",
        "--outdir", str(svg_file.parent),
        str(drawio_file),
    ]

    print(f"[draw.io] Converting {drawio_file} -> PNG using LibreOffice")
    result = subprocess.run(command_png, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        print(f"[draw.io] LibreOffice PNG conversion failed: {result.returncode}")
        print(f"[draw.io] Error: {result.stderr[:200]}")
        return False

    # Find generated PNG file
    png_path = None
    for f in svg_file.parent.glob("*.png"):
        png_path = f
        break

    if not png_path or not png_path.exists():
        print(f"[draw.io] No PNG generated in {svg_file.parent}")
        # Try fallback: use the stem name
        png_path = svg_file.parent / f"{drawio_file.stem}.png"
        if not png_path.exists():
            return False

    # Step 2: Convert PNG to SVG using ImageMagick (potrace would be better, but using IM for simplicity)
    # For vector quality, we use ImageMagick's PNG to SVG conversion
    command_svg = [
        "convert",
        "-quality", "100",
        str(png_path),
        str(svg_file)
    ]

    print(f"[draw.io] Converting PNG -> {svg_file} using ImageMagick")
    result = subprocess.run(command_svg, capture_output=True, text=True, timeout=120)

    # Cleanup PNG
    try:
        png_path.unlink()
    except Exception as e:
        print(f"[draw.io] Warning: Could not delete {png_path}: {e}")

    if result.returncode != 0:
        print(f"[draw.io] ImageMagick SVG conversion failed: {result.returncode}")
        print(f"[draw.io] Error: {result.stderr[:200]}")
        return False

    if not svg_file.exists():
        print(f"[draw.io] Expected SVG at {svg_file} but the file does not exist")
        return False

    print(f"[draw.io] SVG written to {svg_file}")
    return True


