# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the API
```bash
# Primary method - handles environment setup
python run.py

# Alternative - direct uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Docker (recommended for STEP file support)
docker-compose up --build
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test file
python tests/integration/test_conversion.py

# Test real STEP conversion (will fail on Windows, works in WSL/Docker)
python tests/integration/test_real_step.py

# Quick API test
python tests/integration/test_api.py
```

### Linting and Type Checking
```bash
# Format code
black app/ tests/

# Lint
ruff check app/ tests/

# Type check (if mypy configured)
mypy app/
```

## Architecture Overview

This is a CAD-to-mesh conversion API built with FastAPI. The system converts engineering files (STEP, IGES, BREP) to mesh formats (STL, OBJ, GLTF).

### Core Pipeline Flow
1. **Input** → `app/api/endpoints/conversion.py` receives file upload
2. **Routing** → `app/services/conversion.py` determines sync/async processing
3. **Conversion** → `app/services/conversion_pipeline.py` orchestrates the pipeline:
   - Selects appropriate converter from `app/services/converters/`
   - Converts to internal MeshData representation
   - Passes to appropriate exporter in `app/services/exporters/`
4. **Output** → Returns converted file or job ID for async tracking

### Key Architectural Decisions

**Converter Selection:** The pipeline dynamically selects converters based on file extension:
- STEP/STP → `step_converter_ocp.py` (or `step_converter_safe.py` as fallback)
- IGES/IGS → `iges_converter.py`
- STL → `stl_converter.py`

**MeshData Abstraction:** All converters produce a common `MeshData` object containing vertices, faces, and normals, allowing uniform export to any output format. After each converter runs, `ensure_vertex_normals()` (in `app/services/converters/__init__.py`) guarantees vertex normals are populated before the exporter is called—even for formats like IGES whose converter does not compute them natively.

**GLB/GLTF Visual Consistency:** Every GLB/GLTF export applies a single canonical PBR material (light grey, non-metallic, `roughnessFactor=0.45`, `doubleSided=true`) defined as constants in `app/services/exporters/gltf_exporter.py`. CAD face colours are not preserved in `MeshData` today; the output is intentionally appearance-neutral so all source formats look identical in Three.js / React Three Fiber viewers.

**Quality Control:** Conversion quality controlled via deflection parameters:
- `deflection`: Surface deviation tolerance (0.001-1.0)
- `angular_deflection`: Angular deviation in radians (0.1-1.0)

## Critical Platform Considerations

### Windows STEP File Issue
**Problem:** OpenCascade (OCP) causes segmentation faults when reading STEP files on Windows with Python 3.12+.

**Solutions (in order of preference):**
1. Use Docker: `docker-compose up --build`
2. Use WSL2: See `docs/setup_wsl.md`
3. Switch to safe converter: Edit `app/services/conversion_pipeline.py` to import `STEPConverterSafe` instead of `STEPConverterOCP`

### Python Version Requirements
- **Required:** Python 3.11 or 3.12
- **Avoid:** Python 3.13 (OCP compatibility issues)

## Configuration

### Key Settings (`app/core/config.py`)
- `MAX_UPLOAD_SIZE`: Default 100MB
- `ENABLE_OPENCASCADE`: Set to `true` for STEP support (requires proper environment)
- `DEFAULT_DEFLECTION`: 0.1 (medium quality)
- `DEFAULT_ANGULAR_DEFLECTION`: 0.5

### Quality Presets
The pipeline includes presets in `conversion_pipeline.py`:
- **low**: Fast preview (deflection=1.0)
- **medium**: Balanced (deflection=0.1)
- **high**: Detailed (deflection=0.01)
- **ultra**: Maximum quality (deflection=0.001)

## Development Workflow

### Adding New Input Format
1. Create converter in `app/services/converters/` inheriting from `BaseConverter`
2. Implement `convert()` method returning `MeshData`
3. Register in `conversion_pipeline.py` converter selection logic

### Adding New Output Format
1. Create exporter in `app/services/exporters/`
2. Implement export method accepting `MeshData`
3. Add to `SUPPORTED_OUTPUT_FORMATS` in config
4. Register in `conversion_pipeline.py` exporter selection

### Testing File Conversions
Use the utilities in `utils/`:
- `send_file_to_api.py`: Command-line conversion tool
- `web_upload.html`: Browser-based testing interface

## API Endpoints

- `POST /api/v1/convert`: Main conversion endpoint
- `GET /api/v1/status/{job_id}`: Check async job status
- `GET /api/v1/download/{job_id}`: Download converted file
- `GET /api/v1/formats`: List supported formats
- `GET /api/v1/health`: Health check

Documentation available at `http://localhost:8000/docs` when running.

## Project Structure Notes

- **Uploads**: Stored in `uploads/` directory
- **Outputs**: Stored in `outputs/` directory
- **Temp files**: May accumulate in `temp/` - safe to clean periodically

## Dependencies

Core dependencies managed via `requirements.txt`. Special attention needed for:
- `cadquery-ocp`: Must be installed separately, not in requirements.txt
- Platform-specific installation may be required for OpenCascade support

## Common Issues

1. **"Segmentation fault" on Windows**: Use Docker or WSL2
2. **"Module 'OCP' not found"**: Install cadquery-ocp separately or disable ENABLE_OPENCASCADE
3. **Large file timeout**: Use async_processing=true for files >50MB
4. **Memory issues**: Reduce quality settings or process files sequentially