FROM python:3.10-slim

# Install system dependencies for DrawIO → SVG → EMF conversion
RUN apt-get update && apt-get install -y \
    libreoffice-draw \
    libreoffice-common \
    imagemagick \
    libmagickwand-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configure ImageMagick to allow EMF operations (if exists)
RUN if [ -f /etc/ImageMagick-6/policy.xml ]; then \
    sed -i 's/<policy domain="coder" rights="none" pattern="EMF" \/>/<!-- EMF policy enabled -->/g' /etc/ImageMagick-6/policy.xml && \
    sed -i 's/<policy domain="coder" rights="none" pattern="PDF" \/>/<!-- PDF policy enabled -->/g' /etc/ImageMagick-6/policy.xml; \
fi

WORKDIR /app

# Copy requirements and install Python dependencies
COPY diagram-vector-pipeline/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY diagram-vector-pipeline/src /app/src

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:9000/health || exit 1

# Run FastAPI app
CMD ["python", "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "9000"]
