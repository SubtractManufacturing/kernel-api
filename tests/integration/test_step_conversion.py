import os
import requests
from app.core.config import settings

def create_sample_step_file(file_path: str):
    """Create a minimal STEP file for testing"""
    step_content = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('Simple STEP File'),'2;1');
FILE_NAME('sample.step','2024-01-01T00:00:00',('Author'),('Organization'),'Preprocessor','','');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));
ENDSEC;
DATA;
#1=CARTESIAN_POINT('Origin',(0.0,0.0,0.0));
#2=DIRECTION('Z-axis',(0.0,0.0,1.0));
#3=DIRECTION('X-axis',(1.0,0.0,0.0));
#4=AXIS2_PLACEMENT_3D('',#1,#2,#3);
#5=ADVANCED_BREP_SHAPE_REPRESENTATION('',(#6),#7);
#6=AXIS2_PLACEMENT_3D('',#1,#2,#3);
#7=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#8)) GLOBAL_UNIT_ASSIGNED_CONTEXT((#9,#10,#11)) REPRESENTATION_CONTEXT('3D',''));
#8=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),#9,'distance_accuracy_value','confusion accuracy');
#9=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));
#10=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));
#11=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());
ENDSEC;
END-ISO-10303-21;"""
    
    with open(file_path, 'w') as f:
        f.write(step_content)
    print(f"Created sample STEP file: {file_path}")
    return file_path

def test_step_conversion_pipeline():
    """Test STEP to STL conversion using the pipeline directly"""
    print("\n=== Testing STEP to STL Conversion (Pipeline) ===")
    
    from app.services.conversion_pipeline import ConversionPipeline
    
    # Create sample STEP file
    step_file = os.path.join(settings.TEMP_DIR, "sample.step")
    create_sample_step_file(step_file)
    
    # Test conversion
    pipeline = ConversionPipeline()
    
    try:
        output_file = pipeline.convert(
            input_path=step_file,
            output_format='stl',
            quality='medium'
        )
        print(f"✓ Conversion completed: {output_file}")
        
        # Check output
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"  Output file size: {size} bytes")
            
            # Read first few lines to check content
            with open(output_file, 'r') as f:
                lines = f.readlines()[:5]
                print("  First few lines of output:")
                for line in lines:
                    print(f"    {line.strip()}")
                    
            # Check if it's a placeholder
            content = ''.join(lines)
            if 'placeholder' in content.lower() or 'opencascade' in content.lower():
                print("\n⚠️  NOTE: This is a PLACEHOLDER file.")
                print("  For actual STEP conversion, install OpenCascade:")
                print("  conda install -c conda-forge pythonocc-core")
            else:
                print("\n✓ Actual STL file generated!")
    
    except Exception as e:
        print(f"✗ Conversion failed: {e}")

def test_step_conversion_api():
    """Test STEP to STL conversion via API"""
    print("\n=== Testing STEP to STL Conversion (API) ===")
    
    # First check if server is running
    try:
        response = requests.get("http://localhost:8000/api/v1/health")
        if response.status_code != 200:
            print("❌ Server not responding. Start it with: python run.py")
            return
    except:
        print("❌ Server not running. Start it with: python run.py")
        return
    
    # Create sample STEP file
    step_file = os.path.join(settings.TEMP_DIR, "sample_api.step")
    create_sample_step_file(step_file)
    
    # Upload and convert via API
    with open(step_file, 'rb') as f:
        files = {'file': ('sample.step', f, 'application/step')}
        data = {
            'output_format': 'stl',
            'deflection': 0.1,
            'angular_deflection': 0.5
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/convert",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ API conversion successful!")
        print(f"  Job ID: {result.get('job_id')}")
        print(f"  Status: {result.get('status')}")
        print(f"  Output: {result.get('output_file')}")
        
        # Try to download the file
        if result.get('job_id'):
            download_url = f"http://localhost:8000/api/v1/download/{result['job_id']}"
            download_response = requests.get(download_url)
            if download_response.status_code == 200:
                output_path = os.path.join(settings.OUTPUT_DIR, f"downloaded_{result['job_id']}.stl")
                with open(output_path, 'wb') as f:
                    f.write(download_response.content)
                print(f"  Downloaded to: {output_path}")
    else:
        print(f"✗ API conversion failed: {response.status_code}")
        print(f"  Error: {response.text}")

def check_opencascade_status():
    """Check if OpenCascade is available"""
    print("\n=== OpenCascade Status ===")
    
    try:
        from OCC.Core.STEPControl import STEPControl_Reader
        print("✓ OpenCascade is installed and available!")
        print("  Full STEP to STL conversion will work.")
        return True
    except ImportError:
        print("⚠️  OpenCascade is NOT installed")
        print("  STEP files will generate placeholder STL files only.")
        print("\n  To enable full STEP support:")
        print("  1. Install Anaconda or Miniconda")
        print("  2. Run: conda install -c conda-forge pythonocc-core")
        print("  3. Activate the conda environment before running the API")
        return False

def main():
    print("=" * 50)
    print("STEP to STL Conversion Test")
    print("=" * 50)
    
    # Check OpenCascade status
    has_opencascade = check_opencascade_status()
    
    # Test pipeline directly
    test_step_conversion_pipeline()
    
    # Test via API (if server is running)
    print("\nTo test via API, make sure server is running (python run.py)")
    response = input("Is the server running? (y/n): ").strip().lower()
    if response == 'y':
        test_step_conversion_api()
    
    print("\n" + "=" * 50)
    if not has_opencascade:
        print("REMINDER: Install OpenCascade for actual STEP conversion")
        print("Currently using placeholder implementation")
    print("=" * 50)

if __name__ == "__main__":
    main()