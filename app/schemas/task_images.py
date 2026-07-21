from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskImageResponse(BaseModel):
    id: int
    task_id: int
    uploader_id: int
    original_filename: str
    content_type: str
    size_bytes: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
