from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from . import models, schemas, database
from .database import engine, get_db
import requests
import os
import random
import json

app = FastAPI(title="Account Service")

# Base URL for Customer Service
CUSTOMER_SERVICE_URL = os.getenv("CUSTOMER_SERVICE_URL", "http://customer-service:5001/api/customers")

# Create DB tables if they don't exist
models.Base.metadata.create_all(bind=engine)

# ---------------------------------
# CREATE ACCOUNT (Integrated with Customer Service)
# ---------------------------------
@app.post("/accounts", response_model=schemas.AccountResponse)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    """
    1️⃣ Validate customer via Customer Service  
    2️⃣ Create new account with default balance and currency
    """
    # Verify customer existence via Customer Service
    try:
        customer_url = f"{CUSTOMER_SERVICE_URL}/{account.customer_id}"
        print(f"🔍 Checking customer at: {customer_url}") 
        response = requests.get(customer_url)

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Customer {account.customer_id} not found in Customer Service")

        elif response.status_code != 200:
            raise HTTPException(status_code=500, detail="Customer Service unavailable")

                # ✅ Parse the customer data
        customer_data = response.json()
        print("🧾 Customer Data Received from Customer Service:")
        print(json.dumps(customer_data, indent=2))

        # ✅ Ensure KYC is verified
        kyc_status = customer_data.get("data", {}).get("kyc_status", "").upper()
        if kyc_status != "VERIFIED":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot create account: KYC status for customer {account.customer_id} is '{kyc_status}'"
            )

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Customer Service: {str(e)}")

    # Generate a random 12-digit account number
    account_number = str(random.randint(10**11, 10**12 - 1))

    db_account = models.Account(
        customer_id=account.customer_id,
        account_type=account.account_type.value,
        balance=0.0,
        currency="INR",
        status=schemas.AccountStatus.ACTIVE.value,
        account_number=account_number,
    )

    db.add(db_account)
    db.commit()
    db.refresh(db_account)

    return db_account


# ---------------------------------
# GET ACCOUNT BY ID
# ---------------------------------
@app.get("/accounts/{account_id}", response_model=schemas.AccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.account_id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


# ---------------------------------
# GET ALL ACCOUNTS
# ---------------------------------
@app.get("/accounts", response_model=list[schemas.AccountResponse])
def get_all_accounts(db: Session = Depends(get_db)):
    return db.query(models.Account).all()


# ---------------------------------
# UPDATE ACCOUNT STATUS
# ---------------------------------
@app.put("/accounts/{account_id}/status", response_model=schemas.AccountResponse)
def update_account_status(account_id: int, update: schemas.AccountUpdateStatus, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.account_id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.status = update.status.value
    db.commit()
    db.refresh(account)
    return account

# ---------------------------------
# UPDATE ANY ACCOUNT FIELD
# ---------------------------------
@app.patch("/accounts/{account_id}", response_model=schemas.AccountResponse)
def update_account_fields(account_id: int, update_data: dict, db: Session = Depends(get_db)):
    """
    Dynamically update one or more fields of an account.
    Example:
    PATCH /accounts/5
    {
      "balance": 150000.75,
      "currency": "USD",
      "status": "ACTIVE"
    }
    """
    account = db.query(models.Account).filter(models.Account.account_id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    allowed_fields = {"account_type", "balance", "currency", "status"}  # Safe fields only
    for field, value in update_data.items():
        if field in allowed_fields:
            setattr(account, field, value)
        else:
            raise HTTPException(status_code=400, detail=f"Field '{field}' cannot be updated")

    db.commit()
    db.refresh(account)
    return account

# ---------------------------------
# DELETE / CLOSE ACCOUNT
# ---------------------------------
@app.delete("/accounts/{account_id}")
def close_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.account_id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.status = schemas.AccountStatus.CLOSED.value
    db.commit()
    return {"detail": f"Account {account_id} closed successfully"}
