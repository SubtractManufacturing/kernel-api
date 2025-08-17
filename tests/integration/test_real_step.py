import os
import numpy as np
from app.core.config import settings
from app.services.conversion_pipeline import ConversionPipeline

def create_real_step_file(file_path: str):
    """Create a real STEP file with a simple cube geometry"""
    step_content = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('A simple cube in STEP format'),'2;1');
FILE_NAME('cube.step','2024-01-01T00:00:00',('Author'),('Organization'),
  'STEP Processor','','');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));
ENDSEC;
DATA;
#1 = CARTESIAN_POINT('',(-10.,-10.,-10.));
#2 = CARTESIAN_POINT('',(10.,-10.,-10.));
#3 = CARTESIAN_POINT('',(10.,10.,-10.));
#4 = CARTESIAN_POINT('',(-10.,10.,-10.));
#5 = CARTESIAN_POINT('',(-10.,-10.,10.));
#6 = CARTESIAN_POINT('',(10.,-10.,10.));
#7 = CARTESIAN_POINT('',(10.,10.,10.));
#8 = CARTESIAN_POINT('',(-10.,10.,10.));
#9 = VERTEX_POINT('',#1);
#10 = VERTEX_POINT('',#2);
#11 = VERTEX_POINT('',#3);
#12 = VERTEX_POINT('',#4);
#13 = VERTEX_POINT('',#5);
#14 = VERTEX_POINT('',#6);
#15 = VERTEX_POINT('',#7);
#16 = VERTEX_POINT('',#8);
#17 = DIRECTION('',(1.,0.,0.));
#18 = DIRECTION('',(0.,1.,0.));
#19 = DIRECTION('',(0.,0.,1.));
#20 = DIRECTION('',(-1.,0.,0.));
#21 = DIRECTION('',(0.,-1.,0.));
#22 = DIRECTION('',(0.,0.,-1.));
#23 = VECTOR('',#17,20.);
#24 = VECTOR('',#18,20.);
#25 = VECTOR('',#19,20.);
#26 = LINE('',#1,#23);
#27 = LINE('',#2,#24);
#28 = LINE('',#3,#20);
#29 = LINE('',#4,#21);
#30 = LINE('',#1,#25);
#31 = LINE('',#2,#25);
#32 = LINE('',#3,#25);
#33 = LINE('',#4,#25);
#34 = EDGE_CURVE('',#9,#10,#26,.T.);
#35 = EDGE_CURVE('',#10,#11,#27,.T.);
#36 = EDGE_CURVE('',#11,#12,#28,.T.);
#37 = EDGE_CURVE('',#12,#9,#29,.T.);
#38 = EDGE_CURVE('',#13,#14,#26,.T.);
#39 = EDGE_CURVE('',#14,#15,#27,.T.);
#40 = EDGE_CURVE('',#15,#16,#28,.T.);
#41 = EDGE_CURVE('',#16,#13,#29,.T.);
#42 = EDGE_CURVE('',#9,#13,#30,.T.);
#43 = EDGE_CURVE('',#10,#14,#31,.T.);
#44 = EDGE_CURVE('',#11,#15,#32,.T.);
#45 = EDGE_CURVE('',#12,#16,#33,.T.);
#46 = ORIENTED_EDGE('',*,*,#34,.T.);
#47 = ORIENTED_EDGE('',*,*,#35,.T.);
#48 = ORIENTED_EDGE('',*,*,#36,.T.);
#49 = ORIENTED_EDGE('',*,*,#37,.T.);
#50 = EDGE_LOOP('',(#46,#47,#48,#49));
#51 = FACE_OUTER_BOUND('',#50,.T.);
#52 = PLANE('',#100);
#53 = ADVANCED_FACE('',(#51),#52,.F.);
#54 = ORIENTED_EDGE('',*,*,#38,.T.);
#55 = ORIENTED_EDGE('',*,*,#39,.T.);
#56 = ORIENTED_EDGE('',*,*,#40,.T.);
#57 = ORIENTED_EDGE('',*,*,#41,.T.);
#58 = EDGE_LOOP('',(#54,#55,#56,#57));
#59 = FACE_OUTER_BOUND('',#58,.T.);
#60 = PLANE('',#101);
#61 = ADVANCED_FACE('',(#59),#60,.T.);
#62 = ORIENTED_EDGE('',*,*,#34,.T.);
#63 = ORIENTED_EDGE('',*,*,#43,.T.);
#64 = ORIENTED_EDGE('',*,*,#38,.F.);
#65 = ORIENTED_EDGE('',*,*,#42,.F.);
#66 = EDGE_LOOP('',(#62,#63,#64,#65));
#67 = FACE_OUTER_BOUND('',#66,.T.);
#68 = PLANE('',#102);
#69 = ADVANCED_FACE('',(#67),#68,.T.);
#70 = ORIENTED_EDGE('',*,*,#35,.T.);
#71 = ORIENTED_EDGE('',*,*,#44,.T.);
#72 = ORIENTED_EDGE('',*,*,#39,.F.);
#73 = ORIENTED_EDGE('',*,*,#43,.F.);
#74 = EDGE_LOOP('',(#70,#71,#72,#73));
#75 = FACE_OUTER_BOUND('',#74,.T.);
#76 = PLANE('',#103);
#77 = ADVANCED_FACE('',(#75),#76,.T.);
#78 = ORIENTED_EDGE('',*,*,#36,.T.);
#79 = ORIENTED_EDGE('',*,*,#45,.T.);
#80 = ORIENTED_EDGE('',*,*,#40,.F.);
#81 = ORIENTED_EDGE('',*,*,#44,.F.);
#82 = EDGE_LOOP('',(#78,#79,#80,#81));
#83 = FACE_OUTER_BOUND('',#82,.T.);
#84 = PLANE('',#104);
#85 = ADVANCED_FACE('',(#83),#84,.T.);
#86 = ORIENTED_EDGE('',*,*,#37,.T.);
#87 = ORIENTED_EDGE('',*,*,#42,.T.);
#88 = ORIENTED_EDGE('',*,*,#41,.F.);
#89 = ORIENTED_EDGE('',*,*,#45,.F.);
#90 = EDGE_LOOP('',(#86,#87,#88,#89));
#91 = FACE_OUTER_BOUND('',#90,.T.);
#92 = PLANE('',#105);
#93 = ADVANCED_FACE('',(#91),#92,.T.);
#94 = CLOSED_SHELL('',(#53,#61,#69,#77,#85,#93));
#95 = MANIFOLD_SOLID_BREP('Cube',#94);
#96 = SHAPE_DEFINITION_REPRESENTATION(#110,#111);
#97 = PRODUCT_DEFINITION_SHAPE('','',#112);
#98 = PRODUCT_DEFINITION('','',#113,#114);
#99 = PRODUCT('Cube','Cube','',(#115));
#100 = AXIS2_PLACEMENT_3D('',#1,#22,#17);
#101 = AXIS2_PLACEMENT_3D('',#5,#19,#17);
#102 = AXIS2_PLACEMENT_3D('',#1,#21,#22);
#103 = AXIS2_PLACEMENT_3D('',#2,#17,#19);
#104 = AXIS2_PLACEMENT_3D('',#3,#18,#17);
#105 = AXIS2_PLACEMENT_3D('',#4,#20,#22);
#106 = AXIS2_PLACEMENT_3D('',#200,#19,#17);
#107 = AXIS2_PLACEMENT_3D('',#200,#19,#17);
#108 = SHAPE_REPRESENTATION('',(#106,#95),#109);
#109 = ( GEOMETRIC_REPRESENTATION_CONTEXT(3) 
GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#116)) 
GLOBAL_UNIT_ASSIGNED_CONTEXT((#117,#118,#119)) 
REPRESENTATION_CONTEXT('Context','3D') );
#110 = PRODUCT_DEFINITION_SHAPE('','',#98);
#111 = ADVANCED_BREP_SHAPE_REPRESENTATION('',(#95,#107),#109);
#112 = PRODUCT_DEFINITION_SHAPE('','',#98);
#113 = PRODUCT('','','',(#115));
#114 = PRODUCT_DEFINITION_CONTEXT('',#120,'design');
#115 = PRODUCT_CONTEXT('',#120,'mechanical');
#116 = UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),#117,
  'distance_accuracy_value','confusion accuracy');
#117 = (LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));
#118 = (NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));
#119 = (NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());
#120 = APPLICATION_CONTEXT('automotive design');
#200 = CARTESIAN_POINT('',(0.,0.,0.));
ENDSEC;
END-ISO-10303-21;"""
    
    with open(file_path, 'w') as f:
        f.write(step_content)
    print(f"Created STEP file: {file_path}")
    return file_path

def test_step_to_stl():
    """Test actual STEP to STL conversion"""
    print("=" * 60)
    print("Testing REAL STEP to STL Conversion with OpenCascade")
    print("=" * 60)
    
    # Ensure directories exist
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    
    # Create STEP file
    step_file = os.path.join(settings.TEMP_DIR, "cube.step")
    create_real_step_file(step_file)
    
    # Initialize pipeline
    pipeline = ConversionPipeline()
    
    print("\n1. Converting STEP to STL...")
    try:
        output_stl = pipeline.convert(
            input_path=step_file,
            output_format='stl',
            deflection=0.1,
            angular_deflection=0.5
        )
        
        print(f"   ✓ Conversion successful: {output_stl}")
        print(f"   File size: {os.path.getsize(output_stl)} bytes")
        
        # Verify STL content
        with open(output_stl, 'rb') as f:
            header = f.read(80)
            if b'solid' in header[:5] or len(header) == 80:
                print("   ✓ Valid STL file generated")
                
                # Try to load with trimesh to verify
                import trimesh
                mesh = trimesh.load(output_stl)
                print(f"   Mesh stats: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
                print(f"   Bounding box: {mesh.bounds.tolist()}")
            else:
                print("   ⚠ STL file may be invalid")
        
        # Test different quality settings
        print("\n2. Testing quality settings...")
        for quality in ['low', 'medium', 'high']:
            output = pipeline.convert(
                input_path=step_file,
                output_format='stl',
                quality=quality
            )
            size = os.path.getsize(output)
            mesh = trimesh.load(output)
            print(f"   {quality:8} - Size: {size:6} bytes, Faces: {len(mesh.faces):5}")
        
        # Convert to other formats
        print("\n3. Converting to other formats...")
        for format in ['obj', 'glb']:
            output = pipeline.convert(
                input_path=step_file,
                output_format=format
            )
            size = os.path.getsize(output)
            print(f"   STEP → {format.upper():4} - {output} ({size} bytes)")
        
        print("\n" + "=" * 60)
        print("SUCCESS! STEP conversion is working with OpenCascade!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        
        print("\nTroubleshooting:")
        print("1. Make sure OCP is properly installed")
        print("2. Check if the STEP file is valid")
        print("3. Try with different deflection values")

def test_iges_conversion():
    """Test IGES conversion"""
    print("\n" + "=" * 60)
    print("Testing IGES to STL Conversion")
    print("=" * 60)
    
    # Create a simple IGES file
    iges_file = os.path.join(settings.TEMP_DIR, "test.igs")
    iges_content = """                                                                        S      1
1H,,1H;,4HTEST,4HTEST,16HIGES Test File  ,                            G      1
16HTest Generator  ,32,38,6,38,15,4HTEST,1.0,1,4HINCH,32768,0.0,      G      2
15H20240101.000000,0.001,10.0,4HUser,4HOrg ,11,0,                     G      3
15H20240101.000000;                                                    G      4
     110       1       0       0       0       0       0       000000000D      1
     110       0       0       1       0                               0D      2
110,0.,0.,0.,10.,0.,0.,10.,10.,0.,0.,10.,0.,0.,0.,0.,10.,0.,10.,       1P      1
10.,10.,10.,0.,10.,10.,0.,0.,10.;                                      1P      2
S      1G      4D      2P      2                                        T      1"""
    
    with open(iges_file, 'w') as f:
        f.write(iges_content)
    
    pipeline = ConversionPipeline()
    
    try:
        output = pipeline.convert(
            input_path=iges_file,
            output_format='stl'
        )
        print(f"✓ IGES conversion successful: {output}")
    except Exception as e:
        print(f"✗ IGES conversion failed: {e}")

if __name__ == "__main__":
    test_step_to_stl()
    test_iges_conversion()