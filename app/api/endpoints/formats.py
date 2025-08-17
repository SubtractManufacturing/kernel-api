from fastapi import APIRouter
from typing import Dict, List, Any
from app.core.config import settings

router = APIRouter()

@router.get("/formats")
async def get_supported_formats():
    return {
        "input_formats": settings.SUPPORTED_INPUT_FORMATS,
        "output_formats": settings.SUPPORTED_OUTPUT_FORMATS,
        "format_details": {
            "step": {"extensions": [".step", ".stp"], "description": "Standard for Exchange of Product Data"},
            "iges": {"extensions": [".iges", ".igs"], "description": "Initial Graphics Exchange Specification"},
            "brep": {"extensions": [".brep"], "description": "Boundary Representation format"},
            "stl": {"extensions": [".stl"], "description": "Stereolithography format", "variants": ["ascii", "binary"]},
            "obj": {"extensions": [".obj"], "description": "Wavefront OBJ format"},
            "glb": {"extensions": [".glb"], "description": "GL Transmission Format Binary"},
            "gltf": {"extensions": [".gltf"], "description": "GL Transmission Format"}
        }
    }