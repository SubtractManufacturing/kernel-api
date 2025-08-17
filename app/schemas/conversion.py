from pydantic import BaseModel
from enum import Enum
from typing import Optional

class ConversionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class ConversionRequest(BaseModel):
    input_format: str
    output_format: str
    deflection: Optional[float] = 0.1
    angular_deflection: Optional[float] = 0.5
    async_processing: Optional[bool] = False

class ConversionResponse(BaseModel):
    job_id: str
    status: ConversionStatus
    message: Optional[str] = None
    output_file: Optional[str] = None
    error: Optional[str] = None