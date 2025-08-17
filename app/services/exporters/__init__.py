from typing import Protocol
from app.services.converters import MeshData

class ExporterProtocol(Protocol):
    """Protocol for all file exporters"""
    def can_export(self, format: str) -> bool:
        """Check if this exporter can handle the format"""
        ...
    
    def export(self, mesh_data: MeshData, output_path: str, **kwargs) -> str:
        """Export mesh data to file"""
        ...