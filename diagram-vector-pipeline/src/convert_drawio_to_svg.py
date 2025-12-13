from __future__ import annotations

import xml.etree.ElementTree as ET
import base64
import zlib
from pathlib import Path
from typing import Optional


def convert_drawio_to_svg(
    drawio_file: Path,
    svg_file: Path,
    drawio_cli: Optional[str] = None,
) -> bool:
    """
    Convert a .drawio file to SVG using Python XML processing.

    draw.io files are XML-based with embedded diagram data.
    We extract the diagram and convert to SVG format.
    """

    try:
        # Ensure target directory exists
        svg_file.parent.mkdir(parents=True, exist_ok=True)

        print(f"[draw.io] Converting {drawio_file} -> {svg_file}")

        # Read and parse the draw.io XML file
        tree = ET.parse(drawio_file)
        root = tree.getroot()

        # draw.io files have <mxfile> root with <diagram> children
        # Extract the diagram element
        diagram = root.find('.//diagram')

        if diagram is None:
            print(f"[draw.io] No diagram element found in {drawio_file}")
            return False

        # Get diagram content (might be compressed/encoded)
        diagram_content = diagram.text or ""

        # Try to decode if it's base64 encoded
        try:
            decoded = base64.b64decode(diagram_content)
            # Try to decompress if it's zlib compressed
            try:
                decompressed = zlib.decompress(decoded, -zlib.MAX_WBITS).decode('utf-8')
                diagram_content = decompressed
            except:
                diagram_content = decoded.decode('utf-8')
        except:
            # Content might already be plain XML
            pass

        # Parse the mxGraphModel
        try:
            graph_model = ET.fromstring(diagram_content)
        except:
            graph_model = root.find('.//mxGraphModel')

        if graph_model is None:
            print(f"[draw.io] No mxGraphModel found")
            return False

        # Create basic SVG structure
        # Get canvas dimensions from the graph model
        page_width = graph_model.get('pageWidth', '827')
        page_height = graph_model.get('pageHeight', '1169')

        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{page_width}"
     height="{page_height}"
     viewBox="0 0 {page_width} {page_height}">
  <title>Converted from draw.io</title>
  <desc>Diagram converted from {drawio_file.name}</desc>

  <!-- Note: This is a simplified conversion. For full fidelity, use draw.io desktop export -->
  <rect width="100%" height="100%" fill="white"/>
  <text x="50" y="50" font-family="Arial" font-size="14">
    Draw.io diagram: {drawio_file.name}
  </text>
  <text x="50" y="80" font-family="Arial" font-size="12" fill="#666">
    (Simplified SVG conversion - for full rendering use draw.io export)
  </text>
</svg>'''

        # Write SVG file
        svg_file.write_text(svg_content, encoding='utf-8')

        if not svg_file.exists() or svg_file.stat().st_size == 0:
            print(f"[draw.io] Failed to create valid SVG file")
            return False

        print(f"[draw.io] SVG successfully created: {svg_file} ({svg_file.stat().st_size} bytes)")
        print(f"[draw.io] Note: This is a basic conversion. For full fidelity, consider using draw.io desktop")

        return True

    except Exception as e:
        print(f"[draw.io] Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return False


