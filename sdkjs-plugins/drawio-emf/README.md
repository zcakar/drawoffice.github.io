# Draw.io EMF Plugin

Converts `.drawio` diagrams to high-quality EMF (Enhanced Metafile) format for use in ONLYOFFICE documents.

## Features

- **Batch Conversion**: Convert multiple diagrams at once
- **Quality Preservation**: Maintains vector quality and formatting
- **Cross-Editor Support**: Works with Writer (Word), Calc (Spreadsheet), Impress (Presentation), and PDF documents
- **Error Handling**: Comprehensive error messages and logging

## Configuration

### Local Development

```bash
# Start the conversion API service
cd diagram-vector-pipeline
python3 -m uvicorn src.api:app --host 127.0.0.1 --port 9000 --reload
```

Then open the plugin in your ONLYOFFICE editor.

### Production (Hetzner)

The API URL will be automatically configured to your deployment domain:
- Development: `http://127.0.0.1:9000/convert/emf`
- Production: `https://your-domain/api/convert/emf` (or set `window.API_EMF_URL` in JavaScript)

## API Endpoint

**POST** `/convert/emf`

Request:
```
Content-Type: multipart/form-data
Body: file (binary .drawio file)
```

Response:
```
Content-Type: image/emf
Body: binary EMF file
```

## Architecture

1. **Frontend** (`index.html`, `code.js`): User interface and file upload
2. **Backend API** (`diagram-vector-pipeline/src/api.py`):
   - Receives `.drawio` file
   - Converts to SVG using libreoffice/draw
   - Converts SVG to EMF using ImageMagick
   - Returns binary EMF to client

## Packaging

This plugin is packaged using `packer/pack.py`:

```bash
cd ../..
python3 packer/pack.py
```

Output: `artifacts/drawio-emf.plugin`

## Requirements

### Backend
- Python 3.8+
- FastAPI
- LibreOffice (for DrawIO → SVG conversion)
- ImageMagick (for SVG → EMF conversion)
- Poppler Utils (for PDF support)

See `requirements.txt` for Python dependencies.

### Frontend
- Modern web browser with FileAPI and Fetch API support
- ONLYOFFICE Docs or DocSpace instance

## Troubleshooting

### "Server error: 500"
- Check if the API service is running
- Verify the API URL in browser console: `console.log(API_URL)`
- Check API logs for conversion errors

### "Empty file returned"
- Verify the input `.drawio` file is valid
- Check backend logs for conversion failures
- Ensure ImageMagick and LibreOffice are properly installed

### CORS errors
- Ensure API allows requests from your ONLYOFFICE domain
- Check `CORSMiddleware` configuration in `api.py`

## Support

For issues and contributions, see the main repository:
https://github.com/zcakar/drawoffice.github.io
