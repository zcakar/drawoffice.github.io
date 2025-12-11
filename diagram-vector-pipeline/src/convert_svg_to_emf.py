from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Union


def _run(cmd: list[str]) -> int:
    """
    Run a command and print stdout/stderr for debugging.
    Returns the process return code.
    """
    print("[svg->emf] running:", " ".join(cmd))
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.stdout:
        print("[svg->emf][stdout]")
        print(proc.stdout)
    if proc.stderr:
        print("[svg->emf][stderr]")
        print(proc.stderr)
    print("[svg->emf] return code:", proc.returncode)
    return proc.returncode


def convert_svg_to_emf(svg_path: Union[str, Path], emf_path: Union[str, Path]) -> bool:
    """
    Convert an SVG file to EMF using Inkscape.

    Parameters
    ----------
    svg_path : str | Path
        Input SVG file.
    emf_path : str | Path
        Output EMF file that should be created.

    Returns
    -------
    bool
        True if the EMF file was successfully created, otherwise False.
    """
    svg = Path(svg_path)
    emf = Path(emf_path)

    if not svg.exists():
        print(f"[svg->emf] Input SVG does not exist: {svg}")
        return False

    # Make sure parent directory exists
    emf.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "inkscape",
        str(svg),
        "--export-type=emf",
        f"--export-filename={emf}",
    ]

    rc = _run(cmd)

    if rc != 0:
        print(f"[svg->emf] Inkscape failed with return code {rc}")
        return False

    if not emf.exists():
        print(f"[svg->emf] Expected EMF at {emf}, but the file does not exist.")
        return False

    print(f"[svg->emf] EMF written to {emf}")
    return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python -m src.convert_svg_to_emf INPUT.svg OUTPUT.emf")
        raise SystemExit(1)

    input_svg = Path(sys.argv[1])
    output_emf = Path(sys.argv[2])

    ok = convert_svg_to_emf(input_svg, output_emf)
    print("success:", ok)
    raise SystemExit(0 if ok else 1)
