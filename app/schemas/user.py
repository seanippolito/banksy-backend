from pydantic import BaseModel
from datetime import datetime

class UserRead(BaseModel):
    id: int
    clerk_user_id: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
