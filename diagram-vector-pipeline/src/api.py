from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import PlainTextResponse, Response
from pathlib import Path
import tempfile

from .convert_drawio_to_svg import convert_drawio_to_svg
from .convert_svg_to_emf import convert_svg_to_emf   # <-- senin dosyan

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # istersen burayı daha sonra sadece kendi domainine daraltırız
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_class=PlainTextResponse)
def health():
    return "OK"


@app.post("/convert/svg")
async def convert_svg(file: UploadFile = File(...)):
    tmpdir = Path(tempfile.mkdtemp(prefix="drawio-"))
    input_path = tmpdir / file.filename
    output_svg = tmpdir / "output.svg"

    input_path.write_bytes(await file.read())
    print(f"[api] Received {input_path}")

    ok = convert_drawio_to_svg(input_path, output_svg)
    print(f"[api] convert_drawio_to_svg -> {ok}, exists={output_svg.exists()}")

    if not ok or not output_svg.exists():
        raise HTTPException(status_code=500, detail="SVG conversion failed")

    return Response(content=output_svg.read_bytes(), media_type="image/svg+xml")


@app.post("/convert/png")
async def convert_png(file: UploadFile = File(...)):
    """
    Convert DrawIO to PNG using LibreOffice.
    Useful for quick preview before EMF conversion.
    """
    import subprocess
    
    tmpdir = Path(tempfile.mkdtemp(prefix="drawio-"))
    input_path = tmpdir / file.filename
    output_png = tmpdir / "output.png"

    input_path.write_bytes(await file.read())
    print(f"[api] Received {input_path} for PNG conversion")

    # Use LibreOffice to convert DrawIO to PNG
    cmd = [
        "libreoffice",
        "--headless",
        "--convert-to", "png",
        "--outdir", str(tmpdir),
        str(input_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    
    if result.returncode != 0:
        print(f"[api] PNG conversion error: {result.stderr}")
        raise HTTPException(status_code=500, detail="PNG conversion failed")
    
    # Find the generated PNG
    png_files = list(tmpdir.glob("*.png"))
    if not png_files:
        print(f"[api] No PNG file generated")
        raise HTTPException(status_code=500, detail="No PNG generated")
    
    png_content = png_files[0].read_bytes()
    print(f"[api] PNG conversion success: {len(png_content)} bytes")
    
    return Response(content=png_content, media_type="image/png")


@app.post("/convert/emf")
async def convert_emf(file: UploadFile = File(...)):
    """
    1) drawio -> svg
    2) svg -> emf
    3) emf dosyasını client’a gönder
    """
    tmpdir = Path(tempfile.mkdtemp(prefix="drawio-"))
    input_path = tmpdir / file.filename
    svg_path = tmpdir / "output.svg"
    emf_path = tmpdir / "output.emf"

    # Gelen drawio dosyasını geçici klasöre yaz
    input_path.write_bytes(await file.read())
    print(f"[api] Received {input_path}")

    # 1) drawio → svg
    ok_svg = convert_drawio_to_svg(input_path, svg_path)
    print(f"[api] convert_drawio_to_svg -> {ok_svg}, exists={svg_path.exists()}")
    if not ok_svg:
        raise HTTPException(status_code=500, detail="SVG conversion failed")

    # 2) svg → emf
    ok_emf = convert_svg_to_emf(svg_path, emf_path)
    print(f"[api] convert_svg_to_emf -> {ok_emf}, exists={emf_path.exists()}")
    if not ok_emf:
        raise HTTPException(status_code=500, detail="EMF conversion failed")

    # 3) Dönüş: EMF binary
    return Response(content=emf_path.read_bytes(), media_type="image/emf")
