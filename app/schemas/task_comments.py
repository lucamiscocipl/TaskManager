from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class TaskCommentResponse(BaseModel):
    id: int
    task_id: int
    author_id: int
    created_at: datetime
    content: str

    model_config = ConfigDict(from_attributes=True)
