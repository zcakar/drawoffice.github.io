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
