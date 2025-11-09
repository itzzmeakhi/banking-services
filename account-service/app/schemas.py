from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import enum


# ---------------------------
# ENUMS
# ---------------------------
class AccountType(str, enum.Enum):
    SALARY = "SALARY"
    SAVINGS = "SAVINGS"
    CURRENT = "CURRENT"
    NRE = "NRE"


class AccountStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    CLOSED = "CLOSED"


# ---------------------------
# REQUEST SCHEMAS
# ---------------------------
class AccountCreate(BaseModel):
    customer_id: str
    account_type: AccountType


class AccountUpdateStatus(BaseModel):
    status: AccountStatus


# ---------------------------
# RESPONSE SCHEMA
# ---------------------------
class AccountResponse(BaseModel):
    account_id: int
    customer_id: str
    account_number: str
    account_type: AccountType
    balance: float
    currency: str
    status: AccountStatus
    created_at: datetime

    class Config:
        orm_mode = True
