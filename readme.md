# Kernel API - CAD to Mesh Conversion Service

Production-ready API for converting CAD files (STEP, IGES, BREP) to mesh formats (STL, OBJ, GLTF, GLB) with full OpenCascade support.

## Features

- ✅ **OpenCascade Integration**: Full STEP/IGES/BREP support via cadquery-ocp
- ✅ **Multiple Output Formats**: STL, OBJ, GLTF, GLB
- ✅ **Consistent Web Preview**: GLB/GLTF output uses a canonical PBR material and guaranteed vertex normals so STEP, IGES, and STL sources render identically in Three.js / React Three Fiber
- ✅ **Quality Control**: Configurable deflection and angular deflection settings
- ✅ **Async Processing**: Redis-backed job queue for large files
- ✅ **Auto Cleanup**: Automatic file cleanup with configurable TTL
- ✅ **Docker Ready**: Production-ready Docker configuration

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/kernel-api.git
cd kernel-api

# Copy environment variables
cp .env.example .env

# Start services
docker-compose up -d

# API will be available at http://localhost:8000
# Documentation at http://localhost:8000/docs
```

### API Endpoints

- `POST /api/v1/convert` - Convert CAD file to mesh format
- `GET /api/v1/status/{job_id}` - Check conversion job status
- `GET /api/v1/download/{job_id}` - Download converted file
- `GET /api/v1/formats` - List supported formats
- `GET /api/v1/health` - Health check

## Supported Formats

### Input Formats
- STEP (.step, .stp)
- IGES (.iges, .igs)
- BREP (.brep)

### Output Formats
- STL (ASCII/Binary)
- OBJ (Wavefront)
- GLTF/GLB (GL Transmission Format)

## Configuration

Key environment variables in `.env`:

```env
# File size limits
MAX_UPLOAD_SIZE=104857600  # 100MB

# Conversion quality
DEFAULT_DEFLECTION=0.1
DEFAULT_ANGULAR_DEFLECTION=0.5

# OpenCascade
ENABLE_OPENCASCADE=true
```

## Production Deployment

The service is containerized and ready for deployment to any Docker-compatible platform:

- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- Kubernetes

### Requirements

- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- 10GB disk space recommended

## License

[Add your license here]
