import os
import numpy as np
import trimesh
from app.services.converters import MeshData
from app.core.logging import get_logger

logger = get_logger(__name__)

class OBJExporter:
    """Exporter for OBJ files"""
    
    def __init__(self):
        self.supported_formats = ['obj']
    
    def can_export(self, format: str) -> bool:
        """Check if this exporter can handle the format"""
        return format.lower() in self.supported_formats
    
    def export(self, mesh_data: MeshData, output_path: str, include_normals: bool = True, **kwargs) -> str:
        """Export mesh data to OBJ file"""
        try:
            logger.info(f"Exporting to OBJ: {output_path}")
            
            # Create trimesh object
            mesh = trimesh.Trimesh(
                vertices=mesh_data.vertices,
                faces=mesh_data.faces,
                vertex_normals=mesh_data.normals if len(mesh_data.normals) > 0 else None
            )
            
            # Export to OBJ
            mesh.export(output_path, file_type='obj', include_normals=include_normals)
            
            # Also create MTL file if requested
            if kwargs.get('include_material', False):
                mtl_path = output_path.replace('.obj', '.mtl')
                self._write_mtl_file(mtl_path, kwargs.get('material_name', 'default'))
            
            file_size = os.path.getsize(output_path)
            logger.info(f"Successfully exported OBJ file: {output_path} ({file_size} bytes)")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting OBJ file: {str(e)}")
            raise
    
    def _write_mtl_file(self, mtl_path: str, material_name: str = 'default'):
        """Write a basic MTL file for the OBJ"""
        with open(mtl_path, 'w') as f:
            f.write(f"# Material file\n")
            f.write(f"newmtl {material_name}\n")
            f.write("Ka 0.2 0.2 0.2\n")  # Ambient color
            f.write("Kd 0.8 0.8 0.8\n")  # Diffuse color
            f.write("Ks 1.0 1.0 1.0\n")  # Specular color
            f.write("Ns 100.0\n")        # Specular exponent
            f.write("d 1.0\n")           # Transparency
            f.write("illum 2\n")         # Illumination model