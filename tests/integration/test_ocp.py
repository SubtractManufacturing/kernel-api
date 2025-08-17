"""Test if OCP (OpenCascade Python) is working correctly"""

def test_ocp_import():
    """Test basic OCP import"""
    print("Testing OCP import...")
    
    try:
        print("1. Importing basic OCP modules...")
        from OCP import gp
        print("   [OK] OCP.gp imported")
        
        from OCP import TopoDS
        print("   [OK] OCP.TopoDS imported")
        
        from OCP import BRepPrimAPI
        print("   [OK] OCP.BRepPrimAPI imported")
        
        print("\n2. Creating a simple shape...")
        from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
        
        # Create a simple box
        box_maker = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0)
        box_shape = box_maker.Shape()
        
        print("   [OK] Created box shape")
        print(f"   Shape is null: {box_shape.IsNull()}")
        
        print("\n3. Testing STEP reader...")
        from OCP.STEPControl import STEPControl_Reader
        reader = STEPControl_Reader()
        print("   [OK] STEP reader created")
        
        print("\n[SUCCESS] OCP is working correctly!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] OCP test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_conversion():
    """Test a very simple shape conversion"""
    print("\n" + "=" * 50)
    print("Testing Simple Shape to STL Conversion")
    print("=" * 50)
    
    try:
        from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
        from OCP.BRepMesh import BRepMesh_IncrementalMesh
        from OCP.StlAPI import StlAPI_Writer
        import os
        from app.core.config import settings
        
        print("1. Creating a box...")
        box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0)
        shape = box.Shape()
        
        print("2. Meshing the shape...")
        mesh = BRepMesh_IncrementalMesh(shape, 0.1)
        mesh.Perform()
        
        if mesh.IsDone():
            print("   [OK] Mesh created successfully")
        else:
            print("   [FAILED] Mesh creation failed")
            return
        
        print("3. Writing to STL...")
        writer = StlAPI_Writer()
        writer.ASCIIMode = True  # Set ASCII mode
        
        output_file = os.path.join(settings.OUTPUT_DIR, "test_box.stl")
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        success = writer.Write(shape, output_file)
        
        if success:
            print(f"   [OK] STL written to: {output_file}")
            print(f"   File size: {os.path.getsize(output_file)} bytes")
        else:
            print("   [FAILED] Failed to write STL")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if test_ocp_import():
        test_simple_conversion()