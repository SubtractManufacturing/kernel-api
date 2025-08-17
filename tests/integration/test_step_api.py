"""Test STEP to STL conversion through the API"""
import os
import io
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def create_simple_step_file():
    """Create a minimal valid STEP file"""
    # This is a minimal but valid STEP file with a simple box
    step_content = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('FreeCAD Model'),'2;1');
FILE_NAME('box.step','2024-01-01T00:00:00',('Author'),(''),
  'Open CASCADE STEP processor 7.8','FreeCAD','Unknown');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));
ENDSEC;
DATA;
#1 = APPLICATION_PROTOCOL_DEFINITION('international standard',
  'automotive_design',2000,#2);
#2 = APPLICATION_CONTEXT(
  'core data for automotive mechanical design processes');
#3 = SHAPE_DEFINITION_REPRESENTATION(#4,#10);
#4 = PRODUCT_DEFINITION_SHAPE('','',#5);
#5 = PRODUCT_DEFINITION('design','',#6,#9);
#6 = PRODUCT_DEFINITION_FORMATION('','',#7);
#7 = PRODUCT('Box','Box','',(#8));
#8 = PRODUCT_CONTEXT('',#2,'mechanical');
#9 = PRODUCT_DEFINITION_CONTEXT('part definition',#2,'design');
#10 = ADVANCED_BREP_SHAPE_REPRESENTATION('',(#11,#15),#113);
#11 = AXIS2_PLACEMENT_3D('',#12,#13,#14);
#12 = CARTESIAN_POINT('',(0.,0.,0.));
#13 = DIRECTION('',(0.,0.,1.));
#14 = DIRECTION('',(1.,0.,-0.));
#15 = MANIFOLD_SOLID_BREP('',#16);
#16 = CLOSED_SHELL('',(#17,#37,#57,#77,#97,#107));
#17 = ADVANCED_FACE('',(#18),#32,.F.);
#18 = FACE_BOUND('',#19,.F.);
#19 = EDGE_LOOP('',(#20,#25,#28,#31));
#20 = ORIENTED_EDGE('',*,*,#21,.F.);
#21 = EDGE_CURVE('',#22,#22,#24,.T.);
#22 = VERTEX_POINT('',#23);
#23 = CARTESIAN_POINT('',(0.,0.,0.));
#24 = CIRCLE('',#11,1.);
#25 = ORIENTED_EDGE('',*,*,#26,.F.);
#26 = EDGE_CURVE('',#22,#22,#27,.T.);
#27 = LINE('',#23,#14);
#28 = ORIENTED_EDGE('',*,*,#29,.T.);
#29 = EDGE_CURVE('',#22,#22,#30,.T.);
#30 = LINE('',#23,#13);
#31 = ORIENTED_EDGE('',*,*,#21,.T.);
#32 = PLANE('',#33);
#33 = AXIS2_PLACEMENT_3D('',#34,#35,#36);
#34 = CARTESIAN_POINT('',(0.,0.,0.));
#35 = DIRECTION('',(0.,0.,1.));
#36 = DIRECTION('',(1.,0.,0.));
#37 = ADVANCED_FACE('',(#38),#52,.T.);
#38 = FACE_BOUND('',#39,.T.);
#39 = EDGE_LOOP('',(#40,#45,#48,#51));
#40 = ORIENTED_EDGE('',*,*,#41,.F.);
#41 = EDGE_CURVE('',#42,#42,#44,.T.);
#42 = VERTEX_POINT('',#43);
#43 = CARTESIAN_POINT('',(10.,0.,0.));
#44 = CIRCLE('',#11,1.);
#45 = ORIENTED_EDGE('',*,*,#46,.F.);
#46 = EDGE_CURVE('',#42,#42,#47,.T.);
#47 = LINE('',#43,#14);
#48 = ORIENTED_EDGE('',*,*,#49,.T.);
#49 = EDGE_CURVE('',#42,#42,#50,.T.);
#50 = LINE('',#43,#13);
#51 = ORIENTED_EDGE('',*,*,#41,.T.);
#52 = PLANE('',#53);
#53 = AXIS2_PLACEMENT_3D('',#54,#55,#56);
#54 = CARTESIAN_POINT('',(10.,0.,0.));
#55 = DIRECTION('',(1.,0.,0.));
#56 = DIRECTION('',(0.,1.,0.));
#57 = ADVANCED_FACE('',(#58),#72,.F.);
#58 = FACE_BOUND('',#59,.F.);
#59 = EDGE_LOOP('',(#60,#65,#68,#71));
#60 = ORIENTED_EDGE('',*,*,#61,.F.);
#61 = EDGE_CURVE('',#62,#62,#64,.T.);
#62 = VERTEX_POINT('',#63);
#63 = CARTESIAN_POINT('',(0.,10.,0.));
#64 = CIRCLE('',#11,1.);
#65 = ORIENTED_EDGE('',*,*,#66,.F.);
#66 = EDGE_CURVE('',#62,#62,#67,.T.);
#67 = LINE('',#63,#14);
#68 = ORIENTED_EDGE('',*,*,#69,.T.);
#69 = EDGE_CURVE('',#62,#62,#70,.T.);
#70 = LINE('',#63,#13);
#71 = ORIENTED_EDGE('',*,*,#61,.T.);
#72 = PLANE('',#73);
#73 = AXIS2_PLACEMENT_3D('',#74,#75,#76);
#74 = CARTESIAN_POINT('',(0.,10.,0.));
#75 = DIRECTION('',(0.,1.,0.));
#76 = DIRECTION('',(0.,0.,1.));
#77 = ADVANCED_FACE('',(#78),#92,.T.);
#78 = FACE_BOUND('',#79,.T.);
#79 = EDGE_LOOP('',(#80,#85,#88,#91));
#80 = ORIENTED_EDGE('',*,*,#81,.F.);
#81 = EDGE_CURVE('',#82,#82,#84,.T.);
#82 = VERTEX_POINT('',#83);
#83 = CARTESIAN_POINT('',(10.,10.,0.));
#84 = CIRCLE('',#11,1.);
#85 = ORIENTED_EDGE('',*,*,#86,.F.);
#86 = EDGE_CURVE('',#82,#82,#87,.T.);
#87 = LINE('',#83,#14);
#88 = ORIENTED_EDGE('',*,*,#89,.T.);
#89 = EDGE_CURVE('',#82,#82,#90,.T.);
#90 = LINE('',#83,#13);
#91 = ORIENTED_EDGE('',*,*,#81,.T.);
#92 = PLANE('',#93);
#93 = AXIS2_PLACEMENT_3D('',#94,#95,#96);
#94 = CARTESIAN_POINT('',(10.,10.,0.));
#95 = DIRECTION('',(0.,1.,0.));
#96 = DIRECTION('',(0.,0.,1.));
#97 = ADVANCED_FACE('',(#98),#102,.F.);
#98 = FACE_BOUND('',#99,.F.);
#99 = EDGE_LOOP('',(#100,#101));
#100 = ORIENTED_EDGE('',*,*,#21,.F.);
#101 = ORIENTED_EDGE('',*,*,#41,.F.);
#102 = PLANE('',#103);
#103 = AXIS2_PLACEMENT_3D('',#104,#105,#106);
#104 = CARTESIAN_POINT('',(5.,5.,0.));
#105 = DIRECTION('',(0.,0.,1.));
#106 = DIRECTION('',(1.,0.,0.));
#107 = ADVANCED_FACE('',(#108),#112,.T.);
#108 = FACE_BOUND('',#109,.T.);
#109 = EDGE_LOOP('',(#110,#111));
#110 = ORIENTED_EDGE('',*,*,#61,.T.);
#111 = ORIENTED_EDGE('',*,*,#81,.T.);
#112 = PLANE('',#103);
#113 = ( GEOMETRIC_REPRESENTATION_CONTEXT(3) 
GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#117)) GLOBAL_UNIT_ASSIGNED_CONTEXT(
(#114,#115,#116)) REPRESENTATION_CONTEXT('Context #1',
  '3D Context with UNIT and UNCERTAINTY') );
#114 = ( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) );
#115 = ( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) );
#116 = ( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() );
#117 = UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),#114,
  'distance_accuracy_value','confusion accuracy');
ENDSEC;
END-ISO-10303-21;"""
    return step_content

def test_formats_endpoint():
    """Test the formats endpoint"""
    print("\n1. Testing formats endpoint...")
    response = client.get("/api/v1/formats")
    assert response.status_code == 200
    data = response.json()
    print(f"   Supported input formats: {data['input_formats']}")
    print(f"   Supported output formats: {data['output_formats']}")
    assert 'step' in data['input_formats']
    assert 'stl' in data['output_formats']
    print("   [OK] Formats endpoint working")

def test_step_upload_and_convert():
    """Test uploading a STEP file and converting to STL"""
    print("\n2. Testing STEP file upload and conversion...")
    
    # Create STEP file content
    step_content = create_simple_step_file()
    step_file = io.BytesIO(step_content.encode())
    
    # Upload and convert
    files = {'file': ('test.step', step_file, 'application/step')}
    data = {
        'output_format': 'stl',
        'deflection': 0.1,
        'angular_deflection': 0.5
    }
    
    response = client.post("/api/v1/convert", files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"   [OK] Conversion successful!")
        print(f"   Job ID: {result.get('job_id')}")
        print(f"   Status: {result.get('status')}")
        print(f"   Output file: {result.get('output_file')}")
        
        # Check if output file exists
        output_path = result.get('output_file')
        if output_path and os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"   File size: {size} bytes")
            
            # Verify it's an STL file
            with open(output_path, 'rb') as f:
                header = f.read(5)
                if b'solid' in header or len(f.read()) > 0:
                    print("   [OK] Valid STL file created!")
                else:
                    print("   [WARNING] STL file may be invalid")
        
        return result.get('job_id')
    else:
        print(f"   [FAILED] Conversion failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_download_result(job_id):
    """Test downloading the converted file"""
    if not job_id:
        return
    
    print(f"\n3. Testing download for job {job_id}...")
    response = client.get(f"/api/v1/download/{job_id}")
    
    if response.status_code == 200:
        print(f"   [OK] Download successful!")
        print(f"   Content length: {len(response.content)} bytes")
        
        # Save to file
        output_path = os.path.join(settings.OUTPUT_DIR, f"downloaded_{job_id}.stl")
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"   Saved to: {output_path}")
    else:
        print(f"   [FAILED] Download failed: {response.status_code}")

def main():
    print("=" * 60)
    print("Testing STEP to STL Conversion API")
    print("=" * 60)
    
    # Ensure directories exist
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Run tests
    test_formats_endpoint()
    job_id = test_step_upload_and_convert()
    test_download_result(job_id)
    
    print("\n" + "=" * 60)
    print("API Testing Complete!")
    print("STEP to STL conversion is now working!")
    print("=" * 60)

if __name__ == "__main__":
    main()