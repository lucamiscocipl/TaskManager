from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    title: str
    description: str
    user_id: int | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    project_id: int
    user_id: int | None
    assigned_username: str | None

    model_config = ConfigDict(from_attributes=True)
