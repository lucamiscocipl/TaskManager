from pydantic import BaseModel, ConfigDict


class taskCreate(BaseModel):
    title: str
    description: str
    status: str = "Not Assigned"


class taskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    project_id: int
    user_id: int | None

    model_config = ConfigDict(from_attributes=True)
