# Diagram Vector Pipeline

This toolkit keeps draw.io the single source of truth for diagrams while ensuring OnlyOffice and Microsoft Word embed EMF vector graphics instead of blurry raster PNGs.

## Why not PNG?
- PNG is raster-based; text and lines degrade when zoomed in documents.
- Office and OnlyOffice re-scale images and may re-compress, further lowering quality.
- Accessibility suffers because text becomes pixels rather than selectable characters.

## Why EMF?
- EMF is an Office-native vector format that preserves paths and text at any zoom level.
- No licensing cost: generated via open-source draw.io (diagrams.net) and Inkscape.
- Works on Windows and Linux, and pastes cleanly into DOCX/ONLYOFFICE documents.

## Repository layout
```
diagram-vector-pipeline/
├─ diagrams/
│  ├─ example.drawio      # Source editable file
│  ├─ example.svg         # Auto-generated vector export
│  └─ example.emf         # Auto-generated Office-ready graphic
├─ src/
│  ├─ convert_drawio_to_svg.py
│  ├─ convert_svg_to_emf.py
│  └─ pipeline.py         # Single entrypoint: python src/pipeline.py
├─ tools/
│  └─ install_dependencies.sh
└─ docs/
   └─ README.md (this file)
```

## Prerequisites
- Python 3.9+
- draw.io / diagrams.net desktop with CLI support (packages provide the `drawio` command)
- Inkscape 1.0+ (provides the `inkscape` CLI)

### Linux (Debian/Ubuntu)
Run the helper script:
```bash
cd diagram-vector-pipeline/tools
./install_dependencies.sh
```

### Windows
- Install [Inkscape](https://inkscape.org/release) and ensure `inkscape.exe` is on your `PATH`.
- Install [diagrams.net desktop](https://github.com/jgraph/drawio-desktop/releases); add the installation directory to `PATH` so `drawio.exe` is callable.
- Use Python via [python.org](https://www.python.org/downloads/) and run the pipeline with `py src\pipeline.py` from `diagram-vector-pipeline`.

## Usage
From `diagram-vector-pipeline/` run:
```bash
python src/pipeline.py
```
This will:
1. Find every `.drawio` file in `diagram-vector-pipeline/diagrams/`.
2. Export each to SVG using draw.io with embedded fonts and images.
3. Convert each SVG to EMF via Inkscape.
4. Print a summary indicating which diagrams succeeded.
5. Stop early if either CLI is missing so you can fix the dependency before continuing.

Optional flags:
```bash
python src/pipeline.py --diagrams-dir /path/to/diagrams --drawio-cli /path/to/drawio --inkscape-cli /path/to/inkscape
```
Environment variables `DRAWIO_CLI` and `INKSCAPE_CLI` are also honored.

### Quick readiness test (no file writes)
Verify your environment and list planned conversions without touching outputs:
```bash
python src/pipeline.py --dry-run
```
This checks that both CLIs are discoverable, lists every `.drawio` file, and confirms the target `.svg`/`.emf` filenames.

### Full conversion test
1. Place or edit a `.drawio` file under `diagram-vector-pipeline/diagrams/`.
2. Run `python src/pipeline.py`.
3. Confirm the matching `.svg` and `.emf` appear/refresh next to the source.
4. Insert the `.emf` into OnlyOffice/Word to validate zoom quality.

## Team workflow
- **Source of truth**: keep every diagram as `.drawio` under `diagram-vector-pipeline/diagrams/`.
- **Editing**: open the `.drawio` file with draw.io/diagrams.net, save changes.
- **Regenerate outputs**: run `python src/pipeline.py` to refresh the matching `.svg` and `.emf` files.
- **Document embedding**: insert the `.emf` files into OnlyOffice or Word. Avoid embedding PNG/JPEG.
- **Version control**: commit `.drawio`, `.svg`, and `.emf` together so updates remain traceable.

## Updating diagrams in existing documents
1. Re-edit the relevant `.drawio` file and run the pipeline.
2. In OnlyOffice/Word, replace the image with the regenerated `.emf` from `diagram-vector-pipeline/diagrams/`.
3. Avoid copy/paste from the browser; always use the exported EMF for maximum fidelity.

## Common issues & fixes
- **`draw.io` not found**: install diagrams.net desktop or set `DRAWIO_CLI` to the executable path.
- **`inkscape` not found**: install Inkscape or set `INKSCAPE_CLI` to the executable path.
- **Fonts look different**: install the same fonts on the conversion host; enable `--embed-fonts` (already configured).
- **Raster artifacts**: ensure linked images inside diagrams are embedded (`--embed-images` is enabled) and that documents embed the EMF output, not SVG/PNG.
- **Conversion fails for one file**: check the console logs; the pipeline skips EMF conversion if SVG export fails so errors stay isolated.

## Notes
- `example.drawio`, `example.svg`, and `example.emf` are placeholders; replace them with your diagrams before running the pipeline in production.
- The pipeline is intentionally CLI-first to allow CI automation without any proprietary dependencies.
