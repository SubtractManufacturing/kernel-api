import os
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Any
import numpy as np
import trimesh
from app.core.logging import get_logger
from app.services.converters import MeshData

logger = get_logger(__name__)

class BaseConverter(ABC):
    """Base class for all CAD file converters"""
    
    def __init__(self):
        self.supported_extensions = []
    
    def can_read(self, file_path: str) -> bool:
        """Check if this converter can read the file"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_extensions
    
    @abstractmethod
    def read(self, file_path: str, **kwargs) -> MeshData:
        """Read file and return mesh data"""
        pass
    
    def _trimesh_to_meshdata(self, mesh: trimesh.Trimesh) -> MeshData:
        """Convert trimesh object to our MeshData format"""
        mesh_data = MeshData()
        mesh_data.vertices = np.array(mesh.vertices, dtype=np.float32)
        mesh_data.faces = np.array(mesh.faces, dtype=np.int32)
        
        if hasattr(mesh, 'vertex_normals'):
            mesh_data.normals = np.array(mesh.vertex_normals, dtype=np.float32)
        
        mesh_data.metadata = {
            'bounds': mesh.bounds.tolist() if hasattr(mesh, 'bounds') else None,
            'volume': float(mesh.volume) if hasattr(mesh, 'volume') else None,
            'area': float(mesh.area) if hasattr(mesh, 'area') else None,
            'vertices_count': len(mesh.vertices),
            'faces_count': len(mesh.faces)
        }
        
        return mesh_data
    
    def _tessellate_with_params(
        self, 
        shape: Any, 
        deflection: float = 0.1, 
        angular_deflection: float = 0.5
    ) -> MeshData:
        """
        Tessellate a shape with given parameters.
        This is a placeholder for OpenCascade tessellation.
        """
        logger.warning("OpenCascade tessellation not available, using placeholder")
        mesh_data = MeshData()
        
        # Create a simple placeholder mesh (cube)
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
            [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
        ], dtype=np.float32)
        
        faces = np.array([
            [0, 1, 2], [0, 2, 3],  # bottom
            [4, 7, 6], [4, 6, 5],  # top
            [0, 4, 5], [0, 5, 1],  # front
            [2, 6, 7], [2, 7, 3],  # back
            [0, 3, 7], [0, 7, 4],  # left
            [1, 5, 6], [1, 6, 2]   # right
        ], dtype=np.int32)
        
        mesh_data.vertices = vertices
        mesh_data.faces = faces
        mesh_data.metadata = {
            'placeholder': True,
            'deflection': deflection,
            'angular_deflection': angular_deflection
        }
        
        return mesh_data