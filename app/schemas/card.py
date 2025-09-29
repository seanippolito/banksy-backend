from pydantic import BaseModel
from typing import Optional


class CardBase(BaseModel):
    account_id: int
    card_number_last4: str
    card_type: str        # "Debit", "Credit", "Virtual"
    expiration_month: int
    expiration_year: int
    status: Optional[str] = "Active"


class CardCreate(CardBase):
    pass


class CardRead(CardBase):
    id: int

    class Config:
        from_attributes = True
