import os
import numpy as np
from typing import List, Tuple
from app.services.converters.base_converter import BaseConverter
from app.services.converters import MeshData
from app.core.logging import get_logger

logger = get_logger(__name__)

class STEPConverterOCP(BaseConverter):
    """STEP file converter using OCP (OpenCascade Python)"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.step', '.stp']
    
    def read(self, file_path: str, deflection: float = 0.1, angular_deflection: float = 0.5) -> MeshData:
        """Read STEP file and convert to mesh data using OCP"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            from OCP.STEPControl import STEPControl_Reader
            from OCP.BRepMesh import BRepMesh_IncrementalMesh
            from OCP.TopExp import TopExp_Explorer
            from OCP.TopAbs import TopAbs_FACE, TopAbs_VERTEX
            from OCP.BRep import BRep_Tool
            from OCP.TopLoc import TopLoc_Location
            from OCP.gp import gp_Pnt
            from OCP.Poly import Poly_Triangulation
            from OCP.TopoDS import TopoDS
            
            logger.info(f"Reading STEP file with OCP: {file_path}")
            
            # Read STEP file
            reader = STEPControl_Reader()
            status = reader.ReadFile(file_path)
            
            if status != 1:  # IFSelect_RetDone
                raise ValueError(f"Failed to read STEP file: {file_path}, status: {status}")
            
            # Transfer to shape
            reader.TransferRoots()
            shape = reader.OneShape()
            
            if shape.IsNull():
                raise ValueError("Failed to extract shape from STEP file")
            
            # Mesh the shape
            mesh = BRepMesh_IncrementalMesh(shape, deflection, False, angular_deflection, True)
            mesh.Perform()
            
            if not mesh.IsDone():
                raise ValueError("Meshing failed")
            
            # Extract vertices and faces
            vertices = []
            faces = []
            vertex_map = {}
            
            # Explore all faces
            explorer = TopExp_Explorer(shape, TopAbs_FACE)
            
            while explorer.More():
                face = TopoDS.Face_s(explorer.Current())
                location = TopLoc_Location()
                triangulation = BRep_Tool.Triangulation_s(face, location)
                
                if triangulation:
                    # Get transformation
                    transformation = location.Transformation()
                    
                    # Process vertices
                    base_vertex_index = len(vertices)
                    num_nodes = triangulation.NbNodes()
                    
                    for i in range(1, num_nodes + 1):
                        node = triangulation.Node(i)
                        
                        # Apply transformation if needed
                        if not location.IsIdentity():
                            node = node.Transformed(transformation)
                        
                        vertex = [node.X(), node.Y(), node.Z()]
                        vertices.append(vertex)
                    
                    # Process triangles
                    num_triangles = triangulation.NbTriangles()
                    
                    for i in range(1, num_triangles + 1):
                        triangle = triangulation.Triangle(i)
                        n1, n2, n3 = triangle.Get()
                        
                        # Adjust indices (OCP uses 1-based indexing)
                        face_indices = [
                            base_vertex_index + n1 - 1,
                            base_vertex_index + n2 - 1,
                            base_vertex_index + n3 - 1
                        ]
                        
                        # Check face orientation
                        if face.Orientation() == 1:  # TopAbs_REVERSED
                            face_indices = [face_indices[0], face_indices[2], face_indices[1]]
                        
                        faces.append(face_indices)
                
                explorer.Next()
            
            # Create mesh data
            mesh_data = MeshData()
            mesh_data.vertices = np.array(vertices, dtype=np.float32)
            mesh_data.faces = np.array(faces, dtype=np.int32)
            
            # Calculate normals
            mesh_data.normals = self._calculate_vertex_normals(mesh_data.vertices, mesh_data.faces)
            
            mesh_data.metadata = {
                'source_format': 'STEP',
                'deflection': deflection,
                'angular_deflection': angular_deflection,
                'vertices_count': len(vertices),
                'faces_count': len(faces),
                'opencascade_version': 'OCP'
            }
            
            logger.info(f"Successfully read STEP file: {len(vertices)} vertices, {len(faces)} faces")
            return mesh_data
            
        except ImportError as e:
            logger.error(f"OCP not available: {e}")
            raise ValueError("OCP (OpenCascade Python) is required for STEP conversion")
        except Exception as e:
            logger.error(f"Error reading STEP file: {str(e)}")
            raise
    
    def _calculate_vertex_normals(self, vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
        """Calculate vertex normals from faces"""
        normals = np.zeros_like(vertices)
        
        for face in faces:
            # Get vertices of the face
            v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
            
            # Calculate face normal
            edge1 = v1 - v0
            edge2 = v2 - v0
            face_normal = np.cross(edge1, edge2)
            
            # Normalize
            length = np.linalg.norm(face_normal)
            if length > 0:
                face_normal /= length
            
            # Add to vertex normals
            for vertex_idx in face:
                normals[vertex_idx] += face_normal
        
        # Normalize all vertex normals
        for i in range(len(normals)):
            length = np.linalg.norm(normals[i])
            if length > 0:
                normals[i] /= length
        
        return normals