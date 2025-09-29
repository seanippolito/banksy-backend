from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.schemas.transaction import TransactionRead

class MoneyTransferCreate(BaseModel):
    sender_account_id: int
    recipient_account_id: int
    amount: int = Field(..., gt=0, description="Amount in cents")
    description: str | None = None

class MoneyTransferRead(BaseModel):
    transfer_id: str
    sender_account_id: int
    recipient_account_id: int
    amount: int
    description: Optional[str]
    created_at: datetime
    transactions: list[TransactionRead]