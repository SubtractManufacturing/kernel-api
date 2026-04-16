import os
import numpy as np
import trimesh
import trimesh.visual.material as trimesh_material
import pygltflib
from app.services.converters import MeshData
from app.core.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Canonical appearance for all GLB/GLTF exports.
# Values produce a neutral light-gray PBR surface that looks consistent
# across STEP, IGES, and STL sources regardless of original CAD face colours.
# ---------------------------------------------------------------------------
_BASE_COLOR_FACTOR = [0.8, 0.8, 0.8, 1.0]   # RGBA – light grey, fully opaque
_METALLIC_FACTOR   = 0.0
_ROUGHNESS_FACTOR  = 0.45
_DOUBLE_SIDED      = True                     # avoids black patches on thin sheets


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
            if binary is None:
                ext = os.path.splitext(output_path)[1].lower()
                binary = (ext == '.glb')

            format_name = 'GLB' if binary else 'GLTF'
            logger.info(f"Exporting to {format_name}: {output_path}")

            has_normals = (
                len(mesh_data.normals) > 0
                and mesh_data.normals.shape == mesh_data.vertices.shape
            )

            mesh = trimesh.Trimesh(
                vertices=mesh_data.vertices,
                faces=mesh_data.faces,
                vertex_normals=mesh_data.normals if has_normals else None,
            )

            # Apply the canonical PBR material so every GLB looks identical
            # regardless of source format or what CAD appearance data was present.
            pbr = trimesh_material.PBRMaterial(
                baseColorFactor=_BASE_COLOR_FACTOR,
                metallicFactor=_METALLIC_FACTOR,
                roughnessFactor=_ROUGHNESS_FACTOR,
                doubleSided=_DOUBLE_SIDED,
                alphaMode='OPAQUE',
            )
            mesh.visual = trimesh.visual.TextureVisuals(material=pbr)

            if binary:
                mesh.export(output_path, file_type='glb')
            else:
                mesh.export(output_path, file_type='gltf')

            file_size = os.path.getsize(output_path)
            logger.info(f"Successfully exported {format_name} file: {output_path} ({file_size} bytes)")
            return output_path

        except Exception as e:
            logger.error(f"Error exporting GLTF/GLB file: {str(e)}")
            try:
                return self._export_with_pygltflib(mesh_data, output_path, binary)
            except Exception as e2:
                logger.error(f"Alternative export also failed: {str(e2)}")
                raise

    def _export_with_pygltflib(self, mesh_data: MeshData, output_path: str, binary: bool = True) -> str:
        """Fallback export using pygltflib directly.

        Produces the same canonical PBR material and includes NORMAL attributes
        when vertex normals are available so the output matches the primary path.
        """
        logger.info("Using alternative GLTF export method")

        has_normals = (
            len(mesh_data.normals) > 0
            and mesh_data.normals.shape == mesh_data.vertices.shape
        )

        gltf = pygltflib.GLTF2()

        # --- raw byte buffers ---
        vertices_f32  = mesh_data.vertices.flatten().astype(np.float32)
        indices_u32   = mesh_data.faces.flatten().astype(np.uint32)
        vertex_bytes  = vertices_f32.tobytes()
        index_bytes   = indices_u32.tobytes()

        if has_normals:
            normals_f32  = mesh_data.normals.flatten().astype(np.float32)
            normal_bytes = normals_f32.tobytes()
        else:
            normal_bytes = b''

        total_bytes = len(vertex_bytes) + len(index_bytes) + len(normal_bytes)

        # --- buffer ---
        buf = pygltflib.Buffer(byteLength=total_bytes)
        gltf.buffers.append(buf)

        # --- buffer views ---
        vertex_bv = pygltflib.BufferView(
            buffer=0,
            byteOffset=0,
            byteLength=len(vertex_bytes),
            target=pygltflib.ARRAY_BUFFER,
        )
        index_bv = pygltflib.BufferView(
            buffer=0,
            byteOffset=len(vertex_bytes),
            byteLength=len(index_bytes),
            target=pygltflib.ELEMENT_ARRAY_BUFFER,
        )
        gltf.bufferViews.extend([vertex_bv, index_bv])  # indices 0, 1

        # --- accessors ---
        vertex_acc = pygltflib.Accessor(
            bufferView=0,
            componentType=pygltflib.FLOAT,
            count=len(mesh_data.vertices),
            type=pygltflib.VEC3,
            max=mesh_data.vertices.max(axis=0).tolist(),
            min=mesh_data.vertices.min(axis=0).tolist(),
        )
        index_acc = pygltflib.Accessor(
            bufferView=1,
            componentType=pygltflib.UNSIGNED_INT,
            count=len(indices_u32),
            type=pygltflib.SCALAR,
        )
        gltf.accessors.extend([vertex_acc, index_acc])  # indices 0 (POSITION), 1 (indices)

        # Normal buffer view + accessor (if available)
        normal_acc_idx = None
        if has_normals:
            normal_bv = pygltflib.BufferView(
                buffer=0,
                byteOffset=len(vertex_bytes) + len(index_bytes),
                byteLength=len(normal_bytes),
                target=pygltflib.ARRAY_BUFFER,
            )
            gltf.bufferViews.append(normal_bv)  # index 2

            n_max = mesh_data.normals.max(axis=0).tolist()
            n_min = mesh_data.normals.min(axis=0).tolist()
            normal_acc = pygltflib.Accessor(
                bufferView=2,
                componentType=pygltflib.FLOAT,
                count=len(mesh_data.vertices),
                type=pygltflib.VEC3,
                max=n_max,
                min=n_min,
            )
            gltf.accessors.append(normal_acc)   # index 2 (NORMAL)
            normal_acc_idx = 2

        # --- canonical PBR material ---
        material = pygltflib.Material(
            name='default',
            pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(
                baseColorFactor=_BASE_COLOR_FACTOR,
                metallicFactor=_METALLIC_FACTOR,
                roughnessFactor=_ROUGHNESS_FACTOR,
            ),
            doubleSided=_DOUBLE_SIDED,
            alphaMode='OPAQUE',
        )
        gltf.materials.append(material)

        # --- mesh primitive ---
        attrs = pygltflib.Attributes(POSITION=0)
        if normal_acc_idx is not None:
            attrs.NORMAL = normal_acc_idx

        primitive = pygltflib.Primitive(
            attributes=attrs,
            indices=1,
            material=0,
        )
        mesh_obj = pygltflib.Mesh(primitives=[primitive])
        gltf.meshes.append(mesh_obj)

        # --- scene ---
        node = pygltflib.Node(mesh=0)
        gltf.nodes.append(node)
        scene = pygltflib.Scene(nodes=[0])
        gltf.scenes.append(scene)
        gltf.scene = 0

        # --- binary blob ---
        gltf.set_binary_blob(vertex_bytes + index_bytes + normal_bytes)

        gltf.save(output_path)
        return output_path
