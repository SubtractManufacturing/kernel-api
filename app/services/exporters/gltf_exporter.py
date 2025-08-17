import os
import numpy as np
import trimesh
import pygltflib
from app.services.converters import MeshData
from app.core.logging import get_logger

logger = get_logger(__name__)

class GLTFExporter:
    """Exporter for GLTF/GLB files"""
    
    def __init__(self):
        self.supported_formats = ['gltf', 'glb']
    
    def can_export(self, format: str) -> bool:
        """Check if this exporter can handle the format"""
        return format.lower() in self.supported_formats
    
    def export(self, mesh_data: MeshData, output_path: str, binary: bool = None, **kwargs) -> str:
        """Export mesh data to GLTF/GLB file"""
        try:
            # Determine format from extension if binary not specified
            if binary is None:
                ext = os.path.splitext(output_path)[1].lower()
                binary = (ext == '.glb')
            
            format_name = 'GLB' if binary else 'GLTF'
            logger.info(f"Exporting to {format_name}: {output_path}")
            
            # Create trimesh object
            mesh = trimesh.Trimesh(
                vertices=mesh_data.vertices,
                faces=mesh_data.faces,
                vertex_normals=mesh_data.normals if len(mesh_data.normals) > 0 else None
            )
            
            # Export using trimesh
            if binary:
                mesh.export(output_path, file_type='glb')
            else:
                mesh.export(output_path, file_type='gltf')
            
            file_size = os.path.getsize(output_path)
            logger.info(f"Successfully exported {format_name} file: {output_path} ({file_size} bytes)")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting GLTF/GLB file: {str(e)}")
            # Try alternative method using pygltflib
            try:
                return self._export_with_pygltflib(mesh_data, output_path, binary)
            except Exception as e2:
                logger.error(f"Alternative export also failed: {str(e2)}")
                raise
    
    def _export_with_pygltflib(self, mesh_data: MeshData, output_path: str, binary: bool = True) -> str:
        """Alternative export method using pygltflib directly"""
        logger.info("Using alternative GLTF export method")
        
        # Create a basic GLTF structure
        gltf = pygltflib.GLTF2()
        
        # Add mesh data
        vertices = mesh_data.vertices.flatten().astype(np.float32)
        indices = mesh_data.faces.flatten().astype(np.uint32)
        
        # Create buffers
        vertex_buffer = vertices.tobytes()
        index_buffer = indices.tobytes()
        
        # Create buffer
        buffer = pygltflib.Buffer(byteLength=len(vertex_buffer) + len(index_buffer))
        gltf.buffers.append(buffer)
        
        # Create buffer views
        vertex_buffer_view = pygltflib.BufferView(
            buffer=0,
            byteOffset=0,
            byteLength=len(vertex_buffer),
            target=pygltflib.ARRAY_BUFFER
        )
        
        index_buffer_view = pygltflib.BufferView(
            buffer=0,
            byteOffset=len(vertex_buffer),
            byteLength=len(index_buffer),
            target=pygltflib.ELEMENT_ARRAY_BUFFER
        )
        
        gltf.bufferViews.extend([vertex_buffer_view, index_buffer_view])
        
        # Create accessors
        vertex_accessor = pygltflib.Accessor(
            bufferView=0,
            componentType=pygltflib.FLOAT,
            count=len(mesh_data.vertices),
            type=pygltflib.VEC3,
            max=mesh_data.vertices.max(axis=0).tolist(),
            min=mesh_data.vertices.min(axis=0).tolist()
        )
        
        index_accessor = pygltflib.Accessor(
            bufferView=1,
            componentType=pygltflib.UNSIGNED_INT,
            count=len(indices),
            type=pygltflib.SCALAR
        )
        
        gltf.accessors.extend([vertex_accessor, index_accessor])
        
        # Create mesh
        primitive = pygltflib.Primitive(
            attributes=pygltflib.Attributes(POSITION=0),
            indices=1
        )
        
        mesh = pygltflib.Mesh(primitives=[primitive])
        gltf.meshes.append(mesh)
        
        # Create node
        node = pygltflib.Node(mesh=0)
        gltf.nodes.append(node)
        
        # Create scene
        scene = pygltflib.Scene(nodes=[0])
        gltf.scenes.append(scene)
        gltf.scene = 0
        
        # Set binary data
        gltf.set_binary_blob(vertex_buffer + index_buffer)
        
        # Save
        gltf.save(output_path)
        
        return output_path