import os
import struct
import numpy as np
import trimesh
from app.services.converters import MeshData
from app.core.logging import get_logger

logger = get_logger(__name__)

class STLExporter:
    """Exporter for STL files (both ASCII and binary)"""
    
    def __init__(self):
        self.supported_formats = ['stl', 'stl_ascii', 'stl_binary']
    
    def can_export(self, format: str) -> bool:
        """Check if this exporter can handle the format"""
        return format.lower() in self.supported_formats
    
    def export(self, mesh_data: MeshData, output_path: str, binary: bool = True, **kwargs) -> str:
        """Export mesh data to STL file"""
        try:
            logger.info(f"Exporting to STL ({'binary' if binary else 'ASCII'}): {output_path}")
            
            # Create trimesh object
            mesh = trimesh.Trimesh(
                vertices=mesh_data.vertices,
                faces=mesh_data.faces,
                vertex_normals=mesh_data.normals if len(mesh_data.normals) > 0 else None
            )
            
            # Ensure the mesh has face normals
            mesh.fix_normals()
            
            # Export based on format
            if binary:
                mesh.export(output_path, file_type='stl')
            else:
                with open(output_path, 'w') as f:
                    f.write(mesh.export(file_type='stl_ascii'))
            
            file_size = os.path.getsize(output_path)
            logger.info(f"Successfully exported STL file: {output_path} ({file_size} bytes)")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting STL file: {str(e)}")
            raise
    
    def export_ascii(self, mesh_data: MeshData, output_path: str, **kwargs) -> str:
        """Export mesh data to ASCII STL file"""
        return self.export(mesh_data, output_path, binary=False, **kwargs)
    
    def export_binary(self, mesh_data: MeshData, output_path: str, **kwargs) -> str:
        """Export mesh data to binary STL file"""
        return self.export(mesh_data, output_path, binary=True, **kwargs)