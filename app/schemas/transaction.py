from pydantic import BaseModel, Field
from datetime import datetime


class TransactionCreate(BaseModel):
    account_id: int
    amount: int = Field(..., gt=0)     # positive integer cents
    type: str = Field(..., pattern="^(DEBIT|CREDIT)$")
    description: str | None = None

class TransactionRead(BaseModel):
    id: int
    account_id: int
    amount: int
    type: str
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True
