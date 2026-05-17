from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True

class AccountRequest(BaseModel):
    user_id: int
    account_number: str
    balance: float
    currency: str = "RUB"

class AccountResponse(BaseModel):
    id: int
    account_number: str
    balance: float
    currency: str
    class Config:
        from_attributes = True


AccountsListResponse = list[AccountResponse]


class TransferRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float
    currency: str = "RUB"

class TransactionResponse(BaseModel):
    id: int
    from_account_id: Optional[int]
    to_account_id: Optional[int]
    amount: float
    currency: str
    timestamp: datetime
    status: str
    class Config:
        from_attributes = True
