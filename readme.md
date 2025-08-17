# Kernel API

A REST API service for converting CAD BREP files to mesh formats using OpenCascade.

## Overview

This project provides a web API that converts various CAD file formats (STEP, IGES, BREP) into mesh formats (STL, OBJ, GLB) using the OpenCascade geometry kernel.

## Features (Planned)

- Convert BREP-based CAD files to mesh formats
- Support for multiple input formats: STEP, IGES, BREP
- Support for multiple output formats: STL, OBJ, GLB/GLTF
- RESTful API built with FastAPI
- Configurable tessellation quality
- Async job processing

## Technology Stack

- Python
- FastAPI
- OpenCascade (via PythonOCC)

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the API

### Development Server

```bash
python run.py
```

Or directly with uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- OpenAPI schema: http://localhost:8000/openapi.json

## API Endpoints

- `GET /` - Root endpoint with API information
- `GET /api/v1/health` - Health check endpoint
- `GET /api/v1/formats` - List supported input/output formats
- `POST /api/v1/convert` - Convert a CAD file (placeholder - OpenCascade integration pending)
- `GET /api/v1/status/{job_id}` - Check conversion job status
- `GET /api/v1/download/{job_id}` - Download converted file

## Testing

Run the basic test suite:

```bash
python test_api.py
```

## Configuration

Copy `.env.example` to `.env` and modify as needed. Key settings:

- `MAX_UPLOAD_SIZE` - Maximum file upload size
- `DEFAULT_DEFLECTION` - Default tessellation accuracy
- `ENABLE_OPENCASCADE` - Enable OpenCascade integration (currently false)

## Project Structure

```
kernel-api/
├── app/                        # Main application package
│   ├── api/                   # API layer
│   │   └── endpoints/         # API endpoint modules
│   │       ├── conversion.py  # File conversion endpoints
│   │       ├── formats.py     # Supported formats endpoint
│   │       └── health.py      # Health check endpoint
│   ├── core/                  # Core functionality
│   │   ├── config.py         # Application configuration
│   │   └── logging.py        # Logging setup
│   ├── models/               # Data models (future: DB models)
│   ├── schemas/              # Pydantic schemas for validation
│   │   └── conversion.py     # Conversion request/response schemas
│   ├── services/             # Business logic layer
│   │   └── conversion.py     # CAD conversion service
│   ├── utils/                # Utility functions
│   └── main.py              # FastAPI application entry point
├── docs/                     # Documentation
├── planning/                 # Project planning documents
│   └── overview.md          # Implementation roadmap
├── tests/                    # Test suite
├── uploads/                  # Temporary upload storage (gitignored)
├── outputs/                  # Conversion output storage (gitignored)
├── temp/                     # Temporary files (gitignored)
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
├── run.py                   # Development server launcher
└── test_api.py             # Basic API tests
```

## Getting Started with Development

### Prerequisites

- **Python 3.12** (REQUIRED for STEP/IGES conversion)
  - Python 3.11 also works
  - Python 3.13 has compatibility issues with OpenCascade
- pip package manager
- Git
- Redis (optional, for async task processing)

### Initial Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/SubtractManufacturing/kernel-api
   cd kernel-api
   ```

2. **Install Python 3.12** (if not already installed)
   
   Download from: https://www.python.org/downloads/release/python-3120/
   - Choose "Windows installer (64-bit)"
   - Check "Add Python to PATH" during installation

3. **Set up Python 3.12 environment**

   **Option A: Automated Setup (Recommended)**
   ```bash
   # Windows Command Prompt
   scripts\setup_python312.bat
   
   # Windows PowerShell
   .\scripts\setup_python312.ps1
   ```

   **Option B: Manual Setup**
   ```bash
   # Windows - Create venv with Python 3.12
   py -3.12 -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python3.12 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   pip install cadquery-ocp  # OpenCascade Python bindings
   ```

5. **Set up environment variables**

   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env with your configuration
   ```

### Development Workflow

#### Running the Development Server

```bash
# Using the run script (recommended for development)
python run.py

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# With custom settings
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080 --log-level debug
```

#### Running Tests

```bash
# Run basic API tests
python test_api.py

# Run with pytest (more detailed)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

#### Code Quality

```bash
# Format code with black
black app/ tests/

# Lint with ruff
ruff check app/ tests/

# Type checking (requires mypy installation)
mypy app/
```

### Development Guidelines

#### Adding New Endpoints

1. Create endpoint module in `app/api/endpoints/`
2. Define request/response schemas in `app/schemas/`
3. Implement business logic in `app/services/`
4. Register router in `app/main.py`
5. Add tests in `tests/`

Example:

```python
# app/api/endpoints/new_feature.py
from fastapi import APIRouter
from app.schemas.new_feature import NewFeatureRequest, NewFeatureResponse

router = APIRouter()

@router.post("/new-feature", response_model=NewFeatureResponse)
async def new_feature(request: NewFeatureRequest):
    # Implementation
    pass

# app/main.py
from app.api.endpoints import new_feature
app.include_router(new_feature.router, prefix="/api/v1", tags=["new_feature"])
```

#### Working with OpenCascade

OpenCascade integration is planned for Phase 2. To prepare:

1. Install PythonOCC (may require conda):

   ```bash
   conda install -c conda-forge pythonocc-core
   ```

2. Enable in configuration:

   ```python
   # .env
   ENABLE_OPENCASCADE=true
   ```

3. Implement converters in `app/services/opencascade/`

#### Environment Variables

Key configuration options in `.env`:

| Variable             | Description                                 | Default           |
| -------------------- | ------------------------------------------- | ----------------- |
| `HOST`               | Server host                                 | 0.0.0.0           |
| `PORT`               | Server port                                 | 8000              |
| `LOG_LEVEL`          | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO              |
| `MAX_UPLOAD_SIZE`    | Maximum file upload size in bytes           | 104857600 (100MB) |
| `DEFAULT_DEFLECTION` | Default mesh tessellation accuracy          | 0.1               |
| `ENABLE_OPENCASCADE` | Enable OpenCascade features                 | false             |

### API Documentation

Once the server is running, you can access:

- **Interactive API Documentation (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Documentation (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Common Development Tasks

#### Adding a New Conversion Format

1. Update supported formats in `app/core/config.py`:

   ```python
   SUPPORTED_INPUT_FORMATS: List[str] = ["step", "stp", "iges", "igs", "brep", "new_format"]
   ```

2. Implement converter in `app/services/conversion.py`

3. Add format details in `app/api/endpoints/formats.py`

#### Debugging

1. Enable debug logging:

   ```bash
   LOG_LEVEL=DEBUG python run.py
   ```

2. Use FastAPI's automatic reload:

   ```bash
   uvicorn app.main:app --reload
   ```

3. Check logs in JSON format for structured debugging

#### Performance Monitoring

- Use `/api/v1/health` endpoint for basic health checks
- Monitor upload/output directories for disk usage
- Check Redis for async task queue status (when implemented)

### Troubleshooting

#### Common Issues

1. **Import errors**: Ensure virtual environment is activated
2. **Port already in use**: Change PORT in .env or kill existing process
3. **File upload fails**: Check MAX_UPLOAD_SIZE and disk space
4. **OpenCascade not found**: Follow OpenCascade installation guide in Phase 2

### Contributing

1. Follow the project structure conventions
2. Write tests for new features
3. Update documentation as needed
4. Run code quality checks before committing

## Status

**Under Development** - Phase 2 Complete

### Phase 1 (Complete)
- ✅ Basic FastAPI application structure
- ✅ Configuration management
- ✅ Logging system
- ✅ API endpoints
- ✅ Basic testing framework

### Phase 2 (Complete)
- ✅ Conversion pipeline architecture
- ✅ STL file reader/writer
- ✅ OBJ exporter
- ✅ GLB/GLTF exporter
- ✅ Mesh quality controls
- ✅ Error handling
- ✅ OpenCascade integration via OCP (cadquery-ocp installed)
- ⚠️ STEP/IGES readers (implemented but requires Python 3.11/3.12 for stability)

### Current Capabilities
- **Working Conversions**: STL ↔ OBJ, STL → GLB/GLTF
- **STEP/IGES Support**: Implemented with OpenCascade (OCP library installed, best with Python 3.11/3.12)
- **Quality Presets**: Low, Medium, High, Ultra
- **Export Formats**: STL (ASCII/Binary), OBJ, GLB, GLTF
- **API Endpoints**: Full REST API with file upload and conversion

### Current Status with Python 3.12

✅ **Working Features:**
- Python 3.12 environment successfully set up
- OCP (OpenCascade Python) installed and functional
- STL ↔ OBJ conversion working
- STL → GLB/GLTF conversion working
- Basic shape creation and STL export via OCP working

⚠️ **Known Issue with STEP Files:**
- STEP file reading causes segmentation fault on Windows
- This appears to be a Windows-specific issue with OCP's STEP reader
- The implementation is complete but requires further troubleshooting

**Workaround Options:**
1. Use WSL2 (Windows Subsystem for Linux) with Python 3.12
2. Use Docker container with Linux base (recommended for production)
3. Use conda environment with pythonocc-core instead of OCP
4. For now, use STL files as input (fully working)

### Next Steps (Phase 3)
- [ ] Async processing with Celery
- [ ] Job queue management
- [ ] Status tracking
- [ ] Batch conversion support
- [ ] Docker containerization

## Testing the Conversion Pipeline

Run the conversion test suite:
```bash
python tests/integration/test_conversion.py
```

Test the API with a sample file:
```bash
# Start the server
python run.py

# Send a file for conversion (from Windows)
python utils/send_file_to_api.py sample.step stl

# Or use the web interface
# Open utils/web_upload.html in your browser
```

## WSL2 Setup (Recommended for STEP Files)

For full STEP/IGES support without segmentation faults, use WSL2:

📖 **[WSL2 Setup Guide](docs/setup_wsl.md)**

This allows you to run the Linux version of the API on Windows with full OpenCascade support.

## Additional Documentation

- 📚 [STEP Conversion Solutions Guide](docs/STEP_CONVERSION_GUIDE.md) - Comprehensive guide for handling STEP files
- 🛠️ [Utilities Documentation](utils/README.md) - How to use the conversion utilities
- 📋 [API Planning Overview](planning/overview.md) - Development roadmap
