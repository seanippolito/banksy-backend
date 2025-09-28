from pydantic import BaseModel
from datetime import datetime

class TransactionRead(BaseModel):
    id: int
    account_id: int
    amount: int
    type: str
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True
