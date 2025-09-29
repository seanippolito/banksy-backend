from pydantic import BaseModel
from datetime import date, datetime
from typing import List

class StatementRequest(BaseModel):
    start_date: date
    end_date: date

class StatementTransaction(BaseModel):
    id: int
    account_id: int
    description: str
    amount: int
    type: str
    created_at: datetime

class StatementResponse(BaseModel):
    account_id: int
    balance: int
    transactions: List[StatementTransaction]
