from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: int
    event_type: str
    title: str
    message: str
    resource_url: str | None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
