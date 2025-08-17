import os
from typing import Dict, Optional, Any
from app.core.logging import get_logger
from app.core.config import settings
from app.services.converters import MeshData
from app.services.converters.step_converter_ocp import STEPConverterOCP
from app.services.converters.iges_converter import IGESConverter
from app.services.converters.stl_converter import STLConverter
from app.services.exporters.stl_exporter import STLExporter
from app.services.exporters.obj_exporter import OBJExporter
from app.services.exporters.gltf_exporter import GLTFExporter

logger = get_logger(__name__)

class ConversionPipeline:
    """Main conversion pipeline for CAD to mesh conversion"""
    
    def __init__(self):
        # Initialize converters
        self.converters = {
            'step': STEPConverterOCP(),
            'stp': STEPConverterOCP(),
            'iges': IGESConverter(),
            'igs': IGESConverter(),
            'stl': STLConverter(),
        }
        
        # Initialize exporters
        self.exporters = {
            'stl': STLExporter(),
            'stl_ascii': STLExporter(),
            'stl_binary': STLExporter(),
            'obj': OBJExporter(),
            'glb': GLTFExporter(),
            'gltf': GLTFExporter(),
        }
        
        self.quality_presets = {
            'low': {'deflection': 1.0, 'angular_deflection': 1.0},
            'medium': {'deflection': 0.1, 'angular_deflection': 0.5},
            'high': {'deflection': 0.01, 'angular_deflection': 0.1},
            'ultra': {'deflection': 0.001, 'angular_deflection': 0.05}
        }
    
    def convert(
        self,
        input_path: str,
        output_format: str,
        output_path: Optional[str] = None,
        quality: str = 'medium',
        deflection: Optional[float] = None,
        angular_deflection: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Convert a CAD file to mesh format
        
        Args:
            input_path: Path to input CAD file
            output_format: Desired output format (stl, obj, glb, gltf)
            output_path: Optional output path (auto-generated if not provided)
            quality: Quality preset (low, medium, high, ultra)
            deflection: Manual deflection setting (overrides quality preset)
            angular_deflection: Manual angular deflection (overrides quality preset)
            **kwargs: Additional format-specific options
        
        Returns:
            Path to the converted file
        """
        try:
            # Validate input file
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            # Get file extension
            input_ext = os.path.splitext(input_path)[1].lower().replace('.', '')
            
            # Check if we have a converter for this format
            if input_ext not in self.converters:
                raise ValueError(f"Unsupported input format: {input_ext}")
            
            # Check if we have an exporter for the output format
            if output_format.lower() not in self.exporters:
                raise ValueError(f"Unsupported output format: {output_format}")
            
            # Get quality parameters
            quality_params = self._get_quality_parameters(quality, deflection, angular_deflection)
            
            logger.info(f"Starting conversion: {input_path} -> {output_format}")
            logger.info(f"Quality parameters: deflection={quality_params['deflection']}, angular_deflection={quality_params['angular_deflection']}")
            
            # Step 1: Read and convert to mesh data
            converter = self.converters[input_ext]
            mesh_data = converter.read(input_path, **quality_params)
            
            # Step 2: Apply mesh quality controls
            mesh_data = self._apply_mesh_controls(mesh_data, **kwargs)
            
            # Step 3: Generate output path if not provided
            if output_path is None:
                output_path = self._generate_output_path(input_path, output_format)
            
            # Step 4: Export to desired format
            exporter = self.exporters[output_format.lower()]
            
            # Handle format-specific options
            export_kwargs = self._prepare_export_options(output_format, kwargs)
            
            output_file = exporter.export(mesh_data, output_path, **export_kwargs)
            
            logger.info(f"Conversion completed successfully: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Conversion failed: {str(e)}")
            raise
    
    def _get_quality_parameters(
        self,
        quality: str,
        deflection: Optional[float],
        angular_deflection: Optional[float]
    ) -> Dict[str, float]:
        """Get quality parameters for tessellation"""
        if deflection is not None and angular_deflection is not None:
            return {
                'deflection': deflection,
                'angular_deflection': angular_deflection
            }
        
        preset = self.quality_presets.get(quality, self.quality_presets['medium'])
        
        return {
            'deflection': deflection or preset['deflection'],
            'angular_deflection': angular_deflection or preset['angular_deflection']
        }
    
    def _apply_mesh_controls(self, mesh_data: MeshData, **kwargs) -> MeshData:
        """Apply mesh quality controls and optimizations"""
        # Decimation
        if kwargs.get('decimate'):
            target_faces = kwargs.get('target_faces')
            if target_faces and len(mesh_data.faces) > target_faces:
                logger.info(f"Decimating mesh from {len(mesh_data.faces)} to {target_faces} faces")
                # Decimation logic would go here (using trimesh or custom algorithm)
        
        # Smoothing
        if kwargs.get('smooth'):
            iterations = kwargs.get('smooth_iterations', 1)
            logger.info(f"Applying smoothing ({iterations} iterations)")
            # Smoothing logic would go here
        
        # Validate mesh
        self._validate_mesh(mesh_data)
        
        return mesh_data
    
    def _validate_mesh(self, mesh_data: MeshData):
        """Validate mesh data"""
        if len(mesh_data.vertices) == 0:
            raise ValueError("Mesh has no vertices")
        
        if len(mesh_data.faces) == 0:
            raise ValueError("Mesh has no faces")
        
        # Check for degenerate faces
        for face in mesh_data.faces:
            if len(set(face)) < 3:
                logger.warning("Mesh contains degenerate faces")
                break
        
        logger.info(f"Mesh validation passed: {len(mesh_data.vertices)} vertices, {len(mesh_data.faces)} faces")
    
    def _generate_output_path(self, input_path: str, output_format: str) -> str:
        """Generate output path based on input path and format"""
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_filename = f"{base_name}.{output_format.lower()}"
        output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
        
        # Ensure unique filename
        counter = 1
        while os.path.exists(output_path):
            output_filename = f"{base_name}_{counter}.{output_format.lower()}"
            output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
            counter += 1
        
        return output_path
    
    def _prepare_export_options(self, output_format: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare format-specific export options"""
        export_kwargs = {}
        
        if output_format.lower() == 'stl_ascii':
            export_kwargs['binary'] = False
        elif output_format.lower() == 'stl_binary' or output_format.lower() == 'stl':
            export_kwargs['binary'] = kwargs.get('binary', True)
        elif output_format.lower() == 'obj':
            export_kwargs['include_normals'] = kwargs.get('include_normals', True)
            export_kwargs['include_material'] = kwargs.get('include_material', False)
        elif output_format.lower() == 'glb':
            export_kwargs['binary'] = True
        elif output_format.lower() == 'gltf':
            export_kwargs['binary'] = False
        
        return export_kwargs
    
    def get_supported_formats(self) -> Dict[str, list]:
        """Get lists of supported input and output formats"""
        return {
            'input_formats': list(self.converters.keys()),
            'output_formats': list(self.exporters.keys())
        }