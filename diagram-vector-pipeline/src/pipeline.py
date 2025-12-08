from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path
from typing import List, Optional

from convert_drawio_to_svg import convert_drawio_to_svg
from convert_svg_to_emf import convert_svg_to_emf


def find_drawio_files(diagrams_dir: Path) -> List[Path]:
    return sorted(diagrams_dir.glob("*.drawio"))


def resolve_cli(name: str, override: Optional[str], env_var: str, default: str) -> Optional[str]:
    """Resolve a CLI executable path using override/env/available PATH entries."""

    candidate = override or os.environ.get(env_var, default)
    resolved = shutil.which(candidate)
    if resolved:
        return resolved

    print(
        f"[pipeline] ERROR: {name} CLI '{candidate}' not found. "
        f"Install it or set {env_var} to the executable path."
    )
    return None


def process_drawio_file(
    drawio_file: Path,
    *,
    drawio_cli: Optional[str],
    inkscape_cli: Optional[str],
) -> bool:
    svg_path = drawio_file.with_suffix(".svg")
    emf_path = drawio_file.with_suffix(".emf")

    svg_ok = convert_drawio_to_svg(drawio_file, svg_path, drawio_cli=drawio_cli)
    if not svg_ok:
        print(f"[pipeline] Skipping EMF conversion because SVG export failed for {drawio_file}")
        return False

    emf_ok = convert_svg_to_emf(svg_path, emf_path, inkscape_cli=inkscape_cli)
    if not emf_ok:
        print(f"[pipeline] ERROR: SVG exported but EMF conversion failed for {drawio_file}")
        return False

    return True


def run_pipeline(
    diagrams_dir: Path,
    *,
    drawio_cli: Optional[str] = None,
    inkscape_cli: Optional[str] = None,
    dry_run: bool = False,
) -> int:
    resolved_drawio = resolve_cli("draw.io", drawio_cli, "DRAWIO_CLI", "drawio")
    resolved_inkscape = resolve_cli("Inkscape", inkscape_cli, "INKSCAPE_CLI", "inkscape")

    if resolved_drawio is None or resolved_inkscape is None:
        return 1

    print(f"[pipeline] Looking for .drawio files in {diagrams_dir}")
    if not diagrams_dir.exists():
        print(f"[pipeline] ERROR: diagrams directory not found at {diagrams_dir}")
        return 1

    drawio_files = find_drawio_files(diagrams_dir)
    if not drawio_files:
        print("[pipeline] No .drawio files found. Nothing to do.")
        return 0

    if dry_run:
        print("[pipeline] Dry run enabled. No files will be converted.")
        for drawio_file in drawio_files:
            svg_path = drawio_file.with_suffix(".svg")
            emf_path = drawio_file.with_suffix(".emf")
            print(f" - {drawio_file.name} -> {svg_path.name} -> {emf_path.name}")
        print(
            "[pipeline] Dry run completed. Rerun without --dry-run to perform conversions."
        )
        return 0

    success = 0
    for drawio_file in drawio_files:
        print(f"[pipeline] Processing {drawio_file.name}")
        if process_drawio_file(
            drawio_file,
            drawio_cli=resolved_drawio,
            inkscape_cli=resolved_inkscape,
        ):
            success += 1

    print(
        f"[pipeline] Completed. {success}/{len(drawio_files)} diagrams converted successfully."
    )
    return 0 if success == len(drawio_files) else 2


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parent.parent
    default_diagram_dir = project_root / "diagrams"

    parser = argparse.ArgumentParser(
        description="Convert draw.io diagrams to SVG and EMF for Office embedding.",
    )
    parser.add_argument(
        "--diagrams-dir",
        type=Path,
        default=default_diagram_dir,
        help=f"Directory containing .drawio files (default: {default_diagram_dir})",
    )
    parser.add_argument(
        "--drawio-cli",
        type=str,
        default=None,
        help="Optional path to draw.io CLI executable (or set DRAWIO_CLI).",
    )
    parser.add_argument(
        "--inkscape-cli",
        type=str,
        default=None,
        help="Optional path to Inkscape executable (or set INKSCAPE_CLI).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "List planned conversions after verifying CLIs without writing any files. "
            "Use this to test pipeline readiness."
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    exit_code = run_pipeline(
        args.diagrams_dir,
        drawio_cli=args.drawio_cli,
        inkscape_cli=args.inkscape_cli,
        dry_run=args.dry_run,
    )
    raise SystemExit(exit_code)
