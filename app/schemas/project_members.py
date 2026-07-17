from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectMemberCreate(BaseModel):
    user_id: int
    model_config = ConfigDict(from_attributes=True)


class ProjectMemberResponse(ProjectMemberCreate):
    project_id: int
    joined_at: datetime | None = None
