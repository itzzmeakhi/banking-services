from sqlalchemy import Column, String, DECIMAL, Enum, TIMESTAMP, func, Integer
from sqlalchemy.orm import declarative_base
import enum
from .database import Base

# --------------------------
# ENUMS (match CSV + schemas.py)
# --------------------------
class AccountType(str, enum.Enum):
    SALARY = "SALARY"
    SAVINGS = "SAVINGS"
    CURRENT = "CURRENT"
    NRE = "NRE"


class AccountStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    CLOSED = "CLOSED"


# --------------------------
# ACCOUNT MODEL
# --------------------------
class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(36), nullable=False)
    account_number = Column(String(20), unique=True, nullable=False)
    account_type = Column(Enum(AccountType, name="account_type_enum"), nullable=False)
    balance = Column(DECIMAL(12, 2), default=0)
    currency = Column(String(5), default="INR")
    status = Column(Enum(AccountStatus, name="account_status_enum"), default=AccountStatus.ACTIVE)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


# --------------------------
# CUSTOMER PROJECTION (Optional View)
# --------------------------
class CustomerProjection(Base):
    __tablename__ = "customer_projection"

    customer_id = Column(String, primary_key=True, index=True)
    name = Column(String(100))
    kyc_status = Column(String(20))
