import os
import shutil
from typing import Dict, Optional
from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.conversion import ConversionStatus, ConversionResponse

logger = get_logger(__name__)

class ConversionService:
    def __init__(self):
        self.jobs: Dict[str, ConversionResponse] = {}
    
    def convert_sync(
        self,
        input_path: str,
        output_format: str,
        deflection: float,
        angular_deflection: float
    ) -> str:
        logger.info(f"Starting sync conversion: {input_path} -> {output_format}")
        
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_filename = f"{base_name}.{output_format}"
        output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
        
        if settings.ENABLE_OPENCASCADE:
            logger.warning("OpenCascade integration not yet implemented")
            raise NotImplementedError("OpenCascade conversion not yet implemented")
        else:
            with open(output_path, "w") as f:
                f.write(f"# Placeholder {output_format.upper()} file\n")
                f.write(f"# Source: {os.path.basename(input_path)}\n")
                f.write(f"# Deflection: {deflection}\n")
                f.write(f"# Angular Deflection: {angular_deflection}\n")
                f.write("# OpenCascade integration pending\n")
        
        logger.info(f"Conversion completed: {output_path}")
        return output_path
    
    async def convert_async(
        self,
        job_id: str,
        input_path: str,
        output_format: str,
        deflection: float,
        angular_deflection: float
    ):
        logger.info(f"Starting async conversion for job {job_id}")
        
        self.jobs[job_id] = ConversionResponse(
            job_id=job_id,
            status=ConversionStatus.IN_PROGRESS,
            message="Conversion in progress"
        )
        
        try:
            output_path = self.convert_sync(
                input_path,
                output_format,
                deflection,
                angular_deflection
            )
            
            self.jobs[job_id] = ConversionResponse(
                job_id=job_id,
                status=ConversionStatus.COMPLETED,
                output_file=output_path,
                message="Conversion completed successfully"
            )
        except Exception as e:
            logger.error(f"Async conversion failed for job {job_id}: {str(e)}")
            self.jobs[job_id] = ConversionResponse(
                job_id=job_id,
                status=ConversionStatus.FAILED,
                error=str(e),
                message="Conversion failed"
            )
    
    def get_job_status(self, job_id: str) -> Optional[ConversionResponse]:
        return self.jobs.get(job_id)