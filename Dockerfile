# Use Python 3.12 slim image for smaller size
FROM python:3.12-slim

# Install system dependencies for OpenCascade
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglu1-mesa \
    libxrender1 \
    libxext6 \
    libxi6 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir cadquery-ocp

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads outputs temp

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]