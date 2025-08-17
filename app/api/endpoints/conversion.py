from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional
import uuid
import os
from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.conversion import ConversionRequest, ConversionResponse, ConversionStatus
from app.services.conversion import ConversionService

router = APIRouter()
logger = get_logger(__name__)
conversion_service = ConversionService()

@router.post("/convert", response_model=ConversionResponse)
async def convert_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    output_format: str = "stl",
    deflection: Optional[float] = None,
    angular_deflection: Optional[float] = None,
    async_processing: bool = False
):
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes"
        )
    
    file_extension = os.path.splitext(file.filename)[1].lower().replace(".", "")
    if file_extension not in settings.SUPPORTED_INPUT_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported input format: {file_extension}"
        )
    
    if output_format not in settings.SUPPORTED_OUTPUT_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported output format: {output_format}"
        )
    
    job_id = str(uuid.uuid4())
    input_path = os.path.join(settings.UPLOAD_DIR, f"{job_id}_{file.filename}")
    
    try:
        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)
        
        if async_processing:
            background_tasks.add_task(
                conversion_service.convert_async,
                job_id,
                input_path,
                output_format,
                deflection or settings.DEFAULT_DEFLECTION,
                angular_deflection or settings.DEFAULT_ANGULAR_DEFLECTION
            )
            
            return ConversionResponse(
                job_id=job_id,
                status=ConversionStatus.PENDING,
                message="Conversion job queued for processing"
            )
        else:
            output_path = conversion_service.convert_sync(
                input_path,
                output_format,
                deflection or settings.DEFAULT_DEFLECTION,
                angular_deflection or settings.DEFAULT_ANGULAR_DEFLECTION
            )
            
            return ConversionResponse(
                job_id=job_id,
                status=ConversionStatus.COMPLETED,
                output_file=output_path,
                message="Conversion completed successfully"
            )
            
    except Exception as e:
        logger.error(f"Conversion failed for job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@router.get("/status/{job_id}", response_model=ConversionResponse)
async def get_conversion_status(job_id: str):
    status = conversion_service.get_job_status(job_id)
    
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return status

@router.get("/download/{job_id}")
async def download_result(job_id: str):
    status = conversion_service.get_job_status(job_id)
    
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if status.status != ConversionStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed. Current status: {status.status}"
        )
    
    if not status.output_file or not os.path.exists(status.output_file):
        raise HTTPException(status_code=404, detail="Output file not found")
    
    return FileResponse(
        path=status.output_file,
        filename=os.path.basename(status.output_file),
        media_type="application/octet-stream"
    )