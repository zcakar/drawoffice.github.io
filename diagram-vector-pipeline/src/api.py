from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.get("/health", response_class=PlainTextResponse)
def health() -> str:
    return "OK"
from fastapi import UploadFile, File, HTTPException
from fastapi.responses import Response
from pathlib import Path
import tempfile

from .convert_drawio_to_svg import convert_drawio_to_svg  # ← senin pipelinedeki fonksiyon

@app.post("/convert/svg")
async def convert_svg(file: UploadFile = File(...)):
    """
    Accept a .drawio file, convert it to SVG, and return the SVG content.
    I log a couple of debug lines so I can see what really happens during the request.
    """
    tmpdir = Path(tempfile.mkdtemp(prefix="drawio-"))
    input_path = tmpdir / file.filename
    output_path = tmpdir / "output.svg"

    # I store the uploaded file in a temporary location.
    input_path.write_bytes(await file.read())

    print(f"[api] Received {input_path}")
    ok = convert_drawio_to_svg(input_path, output_path)
    print(f"[api] convert_drawio_to_svg -> {ok}, exists={output_path.exists()}")

    if not ok:
        # I want to see what went wrong before raising the error.
        raise HTTPException(status_code=500, detail="SVG conversion failed")

    svg_bytes = output_path.read_bytes()
    return Response(content=svg_bytes, media_type="image/svg+xml")
