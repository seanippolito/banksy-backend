from pydantic import BaseModel
from datetime import datetime

class ErrorLogRead(BaseModel):
    id: int
    user_id: int | None
    error_code: int | None
    message: str
    location: str | None
    created_at: datetime

    class Config:
        from_attributes = True
