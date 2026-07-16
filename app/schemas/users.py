from pydantic import BaseModel, ConfigDict, Field


class userCreate(BaseModel):
    username: str = Field(min_length=3, max_length=25)
    password: str = Field(min_length=5, max_length=100)


class userLogin(BaseModel):
    username: str
    password: str


class userResponse(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class tokenResponse(BaseModel):
    access_token: str
    token_type: str
