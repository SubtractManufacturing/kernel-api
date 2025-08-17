import os
from typing import Any
from app.services.converters.base_converter import BaseConverter
from app.services.converters import MeshData
from app.core.logging import get_logger

logger = get_logger(__name__)

class STEPConverter(BaseConverter):
    """Converter for STEP files"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.step', '.stp']
        self.has_opencascade = self._check_opencascade()
    
    def _check_opencascade(self) -> bool:
        """Check if OpenCascade is available"""
        try:
            from OCC.Core.STEPControl import STEPControl_Reader
            from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
            return True
        except ImportError:
            logger.warning("OpenCascade not available for STEP conversion")
            return False
    
    def read(self, file_path: str, deflection: float = 0.1, angular_deflection: float = 0.5) -> MeshData:
        """Read STEP file and convert to mesh data"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if self.has_opencascade:
            return self._read_with_opencascade(file_path, deflection, angular_deflection)
        else:
            return self._read_fallback(file_path, deflection, angular_deflection)
    
    def _read_with_opencascade(self, file_path: str, deflection: float, angular_deflection: float) -> MeshData:
        """Read STEP file using OpenCascade"""
        try:
            from OCC.Core.STEPControl import STEPControl_Reader
            from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
            from OCC.Core.TopExp import TopExp_Explorer
            from OCC.Core.TopAbs import TopAbs_FACE
            from OCC.Core.BRep import BRep_Tool
            from OCC.Core.TopLoc import TopLoc_Location
            import numpy as np
            
            logger.info(f"Reading STEP file with OpenCascade: {file_path}")
            
            # Read STEP file
            step_reader = STEPControl_Reader()
            status = step_reader.ReadFile(file_path)
            
            if status != 1:  # IFSelect_RetDone
                raise ValueError(f"Failed to read STEP file: {file_path}")
            
            step_reader.TransferRoots()
            shape = step_reader.OneShape()
            
            # Mesh the shape
            mesh = BRepMesh_IncrementalMesh(shape, deflection, False, angular_deflection, True)
            mesh.Perform()
            
            if not mesh.IsDone():
                raise ValueError("Meshing failed")
            
            # Extract vertices and faces
            vertices = []
            faces = []
            vertex_map = {}
            vertex_index = 0
            
            # Explore all faces
            explorer = TopExp_Explorer(shape, TopAbs_FACE)
            while explorer.More():
                face = explorer.Current()
                location = TopLoc_Location()
                triangulation = BRep_Tool.Triangulation(face, location)
                
                if triangulation:
                    # Get vertices
                    num_nodes = triangulation.NbNodes()
                    for i in range(1, num_nodes + 1):
                        node = triangulation.Node(i)
                        vertex = [node.X(), node.Y(), node.Z()]
                        
                        # Apply transformation if needed
                        if not location.IsIdentity():
                            trsf = location.Transformation()
                            vertex = [
                                trsf.Value(1, 1) * vertex[0] + trsf.Value(1, 2) * vertex[1] + trsf.Value(1, 3) * vertex[2] + trsf.Value(1, 4),
                                trsf.Value(2, 1) * vertex[0] + trsf.Value(2, 2) * vertex[1] + trsf.Value(2, 3) * vertex[2] + trsf.Value(2, 4),
                                trsf.Value(3, 1) * vertex[0] + trsf.Value(3, 2) * vertex[1] + trsf.Value(3, 3) * vertex[2] + trsf.Value(3, 4)
                            ]
                        
                        vertex_key = tuple(vertex)
                        if vertex_key not in vertex_map:
                            vertex_map[vertex_key] = vertex_index
                            vertices.append(vertex)
                            vertex_index += 1
                    
                    # Get triangles
                    num_triangles = triangulation.NbTriangles()
                    for i in range(1, num_triangles + 1):
                        triangle = triangulation.Triangle(i)
                        n1, n2, n3 = triangle.Get()
                        
                        # Map to global vertex indices
                        v1 = vertices[n1 - 1]
                        v2 = vertices[n2 - 1]
                        v3 = vertices[n3 - 1]
                        
                        i1 = vertex_map[tuple(v1)]
                        i2 = vertex_map[tuple(v2)]
                        i3 = vertex_map[tuple(v3)]
                        
                        faces.append([i1, i2, i3])
                
                explorer.Next()
            
            # Create mesh data
            mesh_data = MeshData()
            mesh_data.vertices = np.array(vertices, dtype=np.float32)
            mesh_data.faces = np.array(faces, dtype=np.int32)
            mesh_data.metadata = {
                'source_format': 'STEP',
                'deflection': deflection,
                'angular_deflection': angular_deflection,
                'vertices_count': len(vertices),
                'faces_count': len(faces)
            }
            
            logger.info(f"Successfully read STEP file: {len(vertices)} vertices, {len(faces)} faces")
            return mesh_data
            
        except Exception as e:
            logger.error(f"Error reading STEP file with OpenCascade: {str(e)}")
            raise
    
    def _read_fallback(self, file_path: str, deflection: float, angular_deflection: float) -> MeshData:
        """Fallback method when OpenCascade is not available"""
        logger.warning(f"OpenCascade not available, using placeholder for STEP file: {file_path}")
        
        # Check if we can at least read basic file info
        file_size = os.path.getsize(file_path)
        
        # Create placeholder mesh
        mesh_data = self._tessellate_with_params(None, deflection, angular_deflection)
        mesh_data.metadata.update({
            'source_format': 'STEP',
            'source_file': os.path.basename(file_path),
            'file_size': file_size,
            'opencascade_required': True,
            'placeholder': True,
            'message': 'OpenCascade required for actual STEP conversion'
        })
        
        return mesh_data