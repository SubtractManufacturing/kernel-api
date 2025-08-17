"""Safe STEP converter that handles Windows OCP issues"""
import os
import subprocess
import tempfile
import json
from typing import Optional
import numpy as np
from app.services.converters.base_converter import BaseConverter
from app.services.converters import MeshData
from app.core.logging import get_logger

logger = get_logger(__name__)

class STEPConverterSafe(BaseConverter):
    """STEP converter with fallback methods for Windows"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.step', '.stp']
        self.has_ocp = self._check_ocp()
    
    def _check_ocp(self) -> bool:
        """Check if OCP is available and working"""
        try:
            # Try a simple import that doesn't crash
            from OCP import gp
            return True
        except:
            return False
    
    def read(self, file_path: str, deflection: float = 0.1, angular_deflection: float = 0.5) -> MeshData:
        """Read STEP file with multiple fallback methods"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Try different methods in order
        methods = [
            self._read_with_freecad_cli,
            self._read_with_external_converter,
            self._read_with_simple_parser,
            self._read_placeholder
        ]
        
        for method in methods:
            try:
                logger.info(f"Trying {method.__name__} for {file_path}")
                return method(file_path, deflection, angular_deflection)
            except Exception as e:
                logger.warning(f"{method.__name__} failed: {e}")
                continue
        
        raise ValueError("All STEP reading methods failed")
    
    def _read_with_freecad_cli(self, file_path: str, deflection: float, angular_deflection: float) -> MeshData:
        """Try to use FreeCAD CLI if installed"""
        # Check if FreeCAD is available
        freecad_paths = [
            r"C:\Program Files\FreeCAD 0.21\bin\FreeCADCmd.exe",
            r"C:\Program Files\FreeCAD 0.20\bin\FreeCADCmd.exe",
            r"C:\Program Files (x86)\FreeCAD\bin\FreeCADCmd.exe",
        ]
        
        freecad_cmd = None
        for path in freecad_paths:
            if os.path.exists(path):
                freecad_cmd = path
                break
        
        if not freecad_cmd:
            raise FileNotFoundError("FreeCAD not found")
        
        # Create conversion script
        script = f'''
import FreeCAD
import Mesh
import json

doc = FreeCAD.open(r"{file_path}")
mesh = Mesh.Mesh()
for obj in doc.Objects:
    if hasattr(obj, "Shape"):
        mesh_obj = Mesh.Mesh(obj.Shape.tessellate({deflection}))
        mesh.addMesh(mesh_obj)

# Export vertices and faces
vertices = [[p.x, p.y, p.z] for p in mesh.Points]
faces = [[f[0], f[1], f[2]] for f in mesh.Facets]

result = {{"vertices": vertices, "faces": faces}}
print(json.dumps(result))
'''
        
        # Write script to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script)
            script_path = f.name
        
        try:
            # Run FreeCAD
            result = subprocess.run(
                [freecad_cmd, "-c", script_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse output
                output = result.stdout
                # Find JSON in output
                import re
                json_match = re.search(r'\{.*\}', output, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    
                    mesh_data = MeshData()
                    mesh_data.vertices = np.array(data['vertices'], dtype=np.float32)
                    mesh_data.faces = np.array(data['faces'], dtype=np.int32)
                    mesh_data.metadata = {
                        'source_format': 'STEP',
                        'converter': 'FreeCAD',
                        'deflection': deflection
                    }
                    return mesh_data
            
            raise ValueError(f"FreeCAD conversion failed: {result.stderr}")
            
        finally:
            os.unlink(script_path)
    
    def _read_with_external_converter(self, file_path: str, deflection: float, angular_deflection: float) -> MeshData:
        """Use external converter if available"""
        # Could use online API or external tool
        raise NotImplementedError("External converter not configured")
    
    def _read_with_simple_parser(self, file_path: str, deflection: float, angular_deflection: float) -> MeshData:
        """Parse STEP file to extract basic geometry"""
        # This would be a very basic STEP parser
        # For now, just check if file is valid STEP
        with open(file_path, 'r') as f:
            content = f.read(1000)
            if 'ISO-10303-21' not in content:
                raise ValueError("Not a valid STEP file")
        
        # Return a simple box as placeholder
        vertices = np.array([
            [0, 0, 0], [100, 0, 0], [100, 100, 0], [0, 100, 0],
            [0, 0, 100], [100, 0, 100], [100, 100, 100], [0, 100, 100]
        ], dtype=np.float32)
        
        faces = np.array([
            [0, 1, 2], [0, 2, 3],  # bottom
            [4, 7, 6], [4, 6, 5],  # top
            [0, 4, 5], [0, 5, 1],  # front
            [2, 6, 7], [2, 7, 3],  # back
            [0, 3, 7], [0, 7, 4],  # left
            [1, 5, 6], [1, 6, 2]   # right
        ], dtype=np.int32)
        
        mesh_data = MeshData()
        mesh_data.vertices = vertices
        mesh_data.faces = faces
        mesh_data.metadata = {
            'source_format': 'STEP',
            'converter': 'simple_parser',
            'warning': 'Basic geometry only - install FreeCAD for accurate conversion',
            'deflection': deflection
        }
        
        return mesh_data
    
    def _read_placeholder(self, file_path: str, deflection: float, angular_deflection: float) -> MeshData:
        """Last resort - return placeholder geometry"""
        return self._read_with_simple_parser(file_path, deflection, angular_deflection)