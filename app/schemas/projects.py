from pydantic import BaseModel, ConfigDict

class projectCreate(BaseModel):
    title: str
    description: str | None = None


class projectUpdate(BaseModel):
    title: str
    description: str | None


class projectResponse(BaseModel):
    id: int
    title: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)
