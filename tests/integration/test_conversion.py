import os
import numpy as np
import trimesh
import pygltflib
from app.services.conversion_pipeline import ConversionPipeline
from app.services.converters import MeshData, ensure_vertex_normals
from app.services.exporters.gltf_exporter import (
    _BASE_COLOR_FACTOR, _METALLIC_FACTOR, _ROUGHNESS_FACTOR, _DOUBLE_SIDED,
    GLTFExporter,
)
from app.core.config import settings


def create_test_stl_file(file_path: str):
    """Create a simple test STL file (cube)"""
    vertices = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
    ])
    
    faces = np.array([
        [0, 1, 2], [0, 2, 3],  # bottom
        [4, 7, 6], [4, 6, 5],  # top
        [0, 4, 5], [0, 5, 1],  # front
        [2, 6, 7], [2, 7, 3],  # back
        [0, 3, 7], [0, 7, 4],  # left
        [1, 5, 6], [1, 6, 2]   # right
    ])
    
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    mesh.export(file_path, file_type='stl')
    print(f"Created test STL file: {file_path}")
    return file_path

def test_stl_to_obj_conversion():
    """Test STL to OBJ conversion"""
    print("\n=== Testing STL to OBJ Conversion ===")
    
    # Create test STL file
    test_stl = os.path.join(settings.TEMP_DIR, "test_cube.stl")
    create_test_stl_file(test_stl)
    
    # Convert to OBJ
    pipeline = ConversionPipeline()
    output_file = pipeline.convert(
        input_path=test_stl,
        output_format='obj',
        quality='medium'
    )
    
    print(f"Converted to OBJ: {output_file}")
    
    # Verify output exists
    assert os.path.exists(output_file), "Output file not created"
    
    # Verify it's a valid OBJ file
    with open(output_file, 'r') as f:
        content = f.read()
        assert 'v ' in content, "OBJ file should contain vertices"
        assert 'f ' in content, "OBJ file should contain faces"
    
    print("[OK] STL to OBJ conversion successful")
    return output_file

def test_stl_to_glb_conversion():
    """Test STL to GLB conversion"""
    print("\n=== Testing STL to GLB Conversion ===")
    
    # Create test STL file
    test_stl = os.path.join(settings.TEMP_DIR, "test_cube2.stl")
    create_test_stl_file(test_stl)
    
    # Convert to GLB
    pipeline = ConversionPipeline()
    output_file = pipeline.convert(
        input_path=test_stl,
        output_format='glb',
        quality='high'
    )
    
    print(f"Converted to GLB: {output_file}")
    
    # Verify output exists
    assert os.path.exists(output_file), "Output file not created"
    
    # Verify file size (GLB files should have some content)
    file_size = os.path.getsize(output_file)
    assert file_size > 100, "GLB file seems too small"
    
    # Try to load it back with trimesh to verify
    try:
        mesh = trimesh.load(output_file)
        print(f"GLB file loaded successfully: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
    except Exception as e:
        print(f"Warning: Could not verify GLB file: {e}")
    
    print("[OK] STL to GLB conversion successful")
    return output_file

def test_quality_presets():
    """Test different quality presets"""
    print("\n=== Testing Quality Presets ===")
    
    # Create test STL file
    test_stl = os.path.join(settings.TEMP_DIR, "test_quality.stl")
    create_test_stl_file(test_stl)
    
    pipeline = ConversionPipeline()
    
    for quality in ['low', 'medium', 'high']:
        output_file = pipeline.convert(
            input_path=test_stl,
            output_format='stl',
            quality=quality
        )
        
        file_size = os.path.getsize(output_file)
        print(f"Quality '{quality}': {output_file} ({file_size} bytes)")
    
    print("[OK] Quality presets working")

def test_glb_has_canonical_material():
    """GLB exported from STL must contain exactly one canonical PBR material."""
    print("\n=== Testing GLB canonical material ===")

    test_stl = os.path.join(settings.TEMP_DIR, "test_material.stl")
    create_test_stl_file(test_stl)

    pipeline = ConversionPipeline()
    output_file = pipeline.convert(
        input_path=test_stl,
        output_format='glb',
        quality='medium',
    )

    gltf = pygltflib.GLTF2().load(output_file)
    assert len(gltf.materials) == 1, f"Expected 1 material, got {len(gltf.materials)}"

    pbr = gltf.materials[0].pbrMetallicRoughness
    assert pbr is not None, "Material must have pbrMetallicRoughness"
    assert abs(pbr.metallicFactor - _METALLIC_FACTOR) < 1e-4, "Metallic factor mismatch"
    assert abs(pbr.roughnessFactor - _ROUGHNESS_FACTOR) < 1e-4, "Roughness factor mismatch"
    assert gltf.materials[0].doubleSided == _DOUBLE_SIDED, "doubleSided mismatch"

    print("[OK] GLB canonical material verified")
    return output_file


def test_glb_has_normals():
    """GLB exported from STL must include a NORMAL accessor in its primitive."""
    print("\n=== Testing GLB NORMAL attribute ===")

    test_stl = os.path.join(settings.TEMP_DIR, "test_normals.stl")
    create_test_stl_file(test_stl)

    pipeline = ConversionPipeline()
    output_file = pipeline.convert(
        input_path=test_stl,
        output_format='glb',
        quality='medium',
    )

    gltf = pygltflib.GLTF2().load(output_file)
    assert len(gltf.meshes) > 0, "GLB must contain at least one mesh"
    prim = gltf.meshes[0].primitives[0]
    assert prim.attributes.NORMAL is not None, "GLB primitive must have NORMAL attribute"

    print("[OK] GLB NORMAL attribute verified")


def test_ensure_vertex_normals_fills_missing():
    """ensure_vertex_normals must compute normals when a converter leaves them empty (IGES case)."""
    print("\n=== Testing ensure_vertex_normals with empty normals ===")

    mesh_data = MeshData()
    mesh_data.vertices = np.array([
        [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1],
    ], dtype=np.float32)
    mesh_data.faces = np.array([[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]], dtype=np.int32)
    # normals intentionally left empty, mirroring IGESConverter behaviour

    assert mesh_data.normals.size == 0, "Precondition: normals should be empty"

    result = ensure_vertex_normals(mesh_data)

    assert result.normals.shape == result.vertices.shape, (
        f"Normals shape {result.normals.shape} must match vertices shape {result.vertices.shape}"
    )
    norms = np.linalg.norm(result.normals, axis=1)
    assert np.all(norms > 0), "All vertex normals must be non-zero after computation"

    print("[OK] ensure_vertex_normals fills missing normals correctly")


def test_pygltflib_fallback_has_material_and_normals():
    """The pygltflib fallback path must also produce a canonical material + NORMAL accessor."""
    print("\n=== Testing pygltflib fallback canonical output ===")

    mesh_data = MeshData()
    mesh_data.vertices = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
    ], dtype=np.float32)
    mesh_data.faces = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int32)
    mesh_data.normals = np.tile([0.0, 0.0, 1.0], (4, 1)).astype(np.float32)

    output_path = os.path.join(settings.TEMP_DIR, "test_fallback.glb")
    exporter = GLTFExporter()
    exporter._export_with_pygltflib(mesh_data, output_path, binary=True)

    gltf = pygltflib.GLTF2().load(output_path)

    assert len(gltf.materials) == 1, "Fallback GLB must have exactly one material"
    pbr = gltf.materials[0].pbrMetallicRoughness
    assert abs(pbr.roughnessFactor - _ROUGHNESS_FACTOR) < 1e-4
    assert gltf.materials[0].doubleSided == _DOUBLE_SIDED

    prim = gltf.meshes[0].primitives[0]
    assert prim.material == 0, "Primitive must reference material index 0"
    assert prim.attributes.NORMAL is not None, "Fallback GLB must include NORMAL attribute"

    print("[OK] pygltflib fallback produces canonical material and NORMAL accessor")


def test_supported_formats():
    """Test getting supported formats"""
    print("\n=== Testing Supported Formats ===")
    
    pipeline = ConversionPipeline()
    formats = pipeline.get_supported_formats()
    
    print(f"Input formats: {formats['input_formats']}")
    print(f"Output formats: {formats['output_formats']}")
    
    assert 'stl' in formats['input_formats'], "STL should be supported as input"
    assert 'obj' in formats['output_formats'], "OBJ should be supported as output"
    assert 'glb' in formats['output_formats'], "GLB should be supported as output"
    
    print("[OK] Format listing working")

def main():
    """Run all conversion tests"""
    print("Starting Conversion Pipeline Tests")
    print("=" * 40)
    
    try:
        # Ensure directories exist
        os.makedirs(settings.TEMP_DIR, exist_ok=True)
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        
        # Run tests
        test_supported_formats()
        test_stl_to_obj_conversion()
        test_stl_to_glb_conversion()
        test_quality_presets()
        test_ensure_vertex_normals_fills_missing()
        test_glb_has_canonical_material()
        test_glb_has_normals()
        test_pygltflib_fallback_has_material_and_normals()
        
        print("\n" + "=" * 40)
        print("All conversion tests passed successfully!")
        
    except Exception as e:
        print(f"\n[FAILED] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())