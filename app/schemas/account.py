from pydantic import BaseModel
from datetime import datetime

class AccountCreate(BaseModel):
    name: str
    currency: str = "USD"

class AccountRead(BaseModel):
    id: int
    name: str
    currency: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
