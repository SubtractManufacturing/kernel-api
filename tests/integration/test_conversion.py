import os
import tempfile
import numpy as np
import trimesh
from app.services.conversion_pipeline import ConversionPipeline
from app.services.converters import MeshData
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