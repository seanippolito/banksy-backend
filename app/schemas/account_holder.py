from pydantic import BaseModel


class AccountHolderBase(BaseModel):
    user_id: int
    account_id: int
    holder_type: str  # "Primary", "Joint", "Trust", "Business", etc.


class AccountHolderCreate(AccountHolderBase):
    pass


class AccountHolderRead(AccountHolderBase):
    id: int
    account_id: int

    class Config:
        from_attributes = True
