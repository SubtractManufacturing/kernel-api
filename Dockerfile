# Multi-stage build for OpenCascade support
FROM python:3.12-slim as builder

# Install build dependencies for OpenCascade
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    cmake \
    make \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libx11-dev \
    libxi-dev \
    libxmu-dev \
    libfreetype6-dev \
    libtbb-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
WORKDIR /app
COPY requirements.txt .

# Install pip packages including cadquery-ocp for OpenCascade support
RUN pip install --no-cache-dir --upgrade pip wheel setuptools && \
    pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt && \
    pip wheel --no-cache-dir --wheel-dir /app/wheels cadquery-ocp==7.7.2

# Final stage
FROM python:3.12-slim

# Install runtime dependencies for OpenCascade
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgomp1 \
    libgl1 \
    libglu1-mesa \
    libx11-6 \
    libxi6 \
    libxmu6 \
    libfreetype6 \
    libtbb12 \
    libxext6 \
    libxrender1 \
    libxfixes3 \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder and install
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Verify OCP installation
RUN python -c "import OCP; print('OCP installed successfully')"

# Set environment
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000
ENV ENABLE_OPENCASCADE=true

WORKDIR /app

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads outputs temp

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health').read()" || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]