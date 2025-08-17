from typing import Protocol, Dict, Any
import numpy as np

class MeshData:
    """Standard mesh data container for conversion pipeline"""
    def __init__(self):
        self.vertices: np.ndarray = np.array([])
        self.faces: np.ndarray = np.array([])
        self.normals: np.ndarray = np.array([])
        self.metadata: Dict[str, Any] = {}

class ConverterProtocol(Protocol):
    """Protocol for all file converters"""
    def can_read(self, file_path: str) -> bool:
        """Check if this converter can read the file"""
        ...
    
    def read(self, file_path: str, **kwargs) -> MeshData:
        """Read file and return mesh data"""
        ...