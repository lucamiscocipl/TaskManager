from pydantic import BaseModel, ConfigDict

class projectCreate(BaseModel):
    title: str
    description: str | None = None
    model_config = ConfigDict(from_attributes=True)

class projectUpdate(projectCreate):
    pass

class projectResponse(projectCreate):
    id: int