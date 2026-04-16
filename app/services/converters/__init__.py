from typing import Protocol, Dict, Any
import numpy as np


class MeshData:
    """Standard mesh data container for conversion pipeline"""
    def __init__(self):
        self.vertices: np.ndarray = np.array([])
        self.faces: np.ndarray = np.array([])
        self.normals: np.ndarray = np.array([])
        self.metadata: Dict[str, Any] = {}


def ensure_vertex_normals(mesh_data: 'MeshData') -> 'MeshData':
    """Guarantee mesh_data has valid per-vertex normals.

    If normals are absent or have a different shape than vertices (which
    happens for IGES and some other converters), they are recomputed via
    trimesh so every downstream exporter receives consistent normal data.
    """
    import trimesh as _trimesh

    has_valid = (
        mesh_data.normals.size > 0
        and mesh_data.normals.shape == mesh_data.vertices.shape
    )
    if not has_valid:
        try:
            tmp = _trimesh.Trimesh(
                vertices=mesh_data.vertices,
                faces=mesh_data.faces,
                process=False,
            )
            mesh_data.normals = np.array(tmp.vertex_normals, dtype=np.float32)
        except Exception:
            pass  # leave empty; exporter will handle gracefully
    return mesh_data


class ConverterProtocol(Protocol):
    """Protocol for all file converters"""
    def can_read(self, file_path: str) -> bool:
        """Check if this converter can read the file"""
        ...

    def read(self, file_path: str, **kwargs) -> MeshData:
        """Read file and return mesh data"""
        ...