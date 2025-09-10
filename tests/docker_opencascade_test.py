#!/usr/bin/env python3
"""
Test script to verify OpenCascade functionality in Docker container.
This script should be run inside the Docker container to verify OCP is working correctly.
"""

import sys
import os
import tempfile
import traceback
from pathlib import Path

def test_ocp_import():
    """Test that OCP can be imported"""
    print("Testing OCP import...")
    try:
        import OCP
        print("✓ OCP module imported successfully")
        
        # Test specific OCP modules
        from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer
        from OCP.BRepMesh import BRepMesh_IncrementalMesh
        from OCP.TopExp import TopExp_Explorer
        from OCP.TopAbs import TopAbs_FACE, TopAbs_VERTEX
        from OCP.BRep import BRep_Tool
        from OCP.TopLoc import TopLoc_Location
        from OCP.gp import gp_Pnt
        from OCP.Poly import Poly_Triangulation
        from OCP.TopoDS import TopoDS
        from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
        
        print("✓ All required OCP modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import OCP: {e}")
        return False

def create_test_step_file():
    """Create a simple STEP file for testing"""
    print("\nCreating test STEP file...")
    try:
        from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
        from OCP.STEPControl import STEPControl_Writer, STEPControl_StepModelType
        from OCP.IFSelect import IFSelect_ReturnStatus
        
        # Create a simple box
        box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
        
        # Write to STEP file
        writer = STEPControl_Writer()
        writer.Transfer(box, STEPControl_StepModelType.STEPControl_AsIs)
        
        # Create temp file
        temp_file = tempfile.NamedTemporaryFile(suffix='.step', delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        status = writer.Write(temp_path)
        
        if status == IFSelect_ReturnStatus.IFSelect_RetDone:
            print(f"✓ Test STEP file created: {temp_path}")
            return temp_path
        else:
            print(f"✗ Failed to write STEP file, status: {status}")
            return None
            
    except Exception as e:
        print(f"✗ Failed to create test STEP file: {e}")
        traceback.print_exc()
        return None

def test_step_conversion(step_file_path):
    """Test STEP file reading and conversion"""
    print(f"\nTesting STEP file conversion: {step_file_path}")
    try:
        from OCP.STEPControl import STEPControl_Reader
        from OCP.BRepMesh import BRepMesh_IncrementalMesh
        from OCP.TopExp import TopExp_Explorer
        from OCP.TopAbs import TopAbs_FACE
        from OCP.BRep import BRep_Tool
        from OCP.TopLoc import TopLoc_Location
        from OCP.TopoDS import TopoDS
        
        # Read STEP file
        reader = STEPControl_Reader()
        status = reader.ReadFile(step_file_path)
        
        if status != 1:  # IFSelect_RetDone
            print(f"✗ Failed to read STEP file, status: {status}")
            return False
        
        print("✓ STEP file read successfully")
        
        # Transfer to shape
        reader.TransferRoots()
        shape = reader.OneShape()
        
        if shape.IsNull():
            print("✗ Failed to extract shape from STEP file")
            return False
        
        print("✓ Shape extracted successfully")
        
        # Mesh the shape
        deflection = 0.1
        angular_deflection = 0.5
        mesh = BRepMesh_IncrementalMesh(shape, deflection, False, angular_deflection, True)
        mesh.Perform()
        
        if not mesh.IsDone():
            print("✗ Meshing failed")
            return False
        
        print("✓ Shape meshed successfully")
        
        # Count faces and vertices
        face_count = 0
        vertex_count = 0
        triangle_count = 0
        
        explorer = TopExp_Explorer(shape, TopAbs_FACE)
        while explorer.More():
            face = TopoDS.Face_s(explorer.Current())
            location = TopLoc_Location()
            triangulation = BRep_Tool.Triangulation_s(face, location)
            
            if triangulation:
                face_count += 1
                vertex_count += triangulation.NbNodes()
                triangle_count += triangulation.NbTriangles()
            
            explorer.Next()
        
        print(f"✓ Mesh statistics:")
        print(f"  - Faces: {face_count}")
        print(f"  - Vertices: {vertex_count}")
        print(f"  - Triangles: {triangle_count}")
        
        return True
        
    except Exception as e:
        print(f"✗ STEP conversion failed: {e}")
        traceback.print_exc()
        return False

def test_api_integration():
    """Test the actual API converter"""
    print("\nTesting API integration...")
    try:
        # Add parent directory to path
        sys.path.insert(0, '/app')
        
        from app.services.converters.step_converter_ocp import STEPConverterOCP
        from app.services.converters import MeshData
        
        # Create converter
        converter = STEPConverterOCP()
        print("✓ STEPConverterOCP instantiated")
        
        # Create a test STEP file
        step_path = create_test_step_file()
        if not step_path:
            return False
        
        # Convert the file
        mesh_data = converter.read(step_path, deflection=0.1, angular_deflection=0.5)
        
        if isinstance(mesh_data, MeshData):
            print("✓ Conversion returned MeshData object")
            print(f"  - Vertices shape: {mesh_data.vertices.shape if mesh_data.vertices is not None else 'None'}")
            print(f"  - Faces shape: {mesh_data.faces.shape if mesh_data.faces is not None else 'None'}")
            print(f"  - Normals shape: {mesh_data.normals.shape if mesh_data.normals is not None else 'None'}")
            
            # Clean up
            os.unlink(step_path)
            return True
        else:
            print("✗ Conversion did not return MeshData object")
            return False
            
    except Exception as e:
        print(f"✗ API integration test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("OpenCascade Docker Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test 1: Import OCP
    results.append(("OCP Import", test_ocp_import()))
    
    if results[-1][1]:  # Only continue if OCP imported successfully
        # Test 2: Create STEP file
        step_file = create_test_step_file()
        results.append(("Create STEP", step_file is not None))
        
        if step_file:
            # Test 3: Convert STEP file
            results.append(("Convert STEP", test_step_conversion(step_file)))
            
            # Clean up
            try:
                os.unlink(step_file)
            except:
                pass
        
        # Test 4: API Integration
        results.append(("API Integration", test_api_integration()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All tests passed! OpenCascade is working correctly in Docker.")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()