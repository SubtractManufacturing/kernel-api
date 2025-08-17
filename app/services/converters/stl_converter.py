import os
import struct
import numpy as np
import trimesh
from app.services.converters.base_converter import BaseConverter
from app.services.converters import MeshData
from app.core.logging import get_logger

logger = get_logger(__name__)

class STLConverter(BaseConverter):
    """Converter for STL files (both ASCII and binary)"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.stl']
    
    def read(self, file_path: str, **kwargs) -> MeshData:
        """Read STL file and convert to mesh data"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Use trimesh for STL reading
            logger.info(f"Reading STL file: {file_path}")
            mesh = trimesh.load(file_path, file_type='stl')
            
            # Convert to MeshData
            mesh_data = self._trimesh_to_meshdata(mesh)
            mesh_data.metadata['source_format'] = 'STL'
            mesh_data.metadata['source_file'] = os.path.basename(file_path)
            
            # Detect if ASCII or binary
            is_ascii = self._is_ascii_stl(file_path)
            mesh_data.metadata['stl_type'] = 'ASCII' if is_ascii else 'Binary'
            
            logger.info(f"Successfully read STL file: {mesh_data.metadata['vertices_count']} vertices, {mesh_data.metadata['faces_count']} faces")
            return mesh_data
            
        except Exception as e:
            logger.error(f"Error reading STL file: {str(e)}")
            raise
    
    def _is_ascii_stl(self, file_path: str) -> bool:
        """Check if STL file is ASCII or binary"""
        with open(file_path, 'rb') as f:
            # Read first 5 bytes
            header = f.read(5)
            if header.startswith(b'solid'):
                # Could be ASCII, need to check further
                f.seek(0)
                try:
                    # Try to decode as ASCII
                    content = f.read(1000).decode('ascii')
                    return 'facet normal' in content or 'FACET NORMAL' in content
                except:
                    return False
            return False