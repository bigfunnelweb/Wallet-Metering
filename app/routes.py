
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account, Transaction

router = APIRouter()

CONSUME_FEE = 10  # ₹0.10 in paise


class TopUpRequest(BaseModel):
    amount_paise: int = Field(gt=0)


@router.post("/accounts", status_code=201)
def create_account(db: Session = Depends(get_db)):
    account = Account(balance=0)
    db.add(account)
    db.commit()
    db.refresh(account)

    return {
        "account_id": account.id,
        "balance_paise": account.balance,
        "balance_rupees": "0.00",
    }


@router.post("/accounts/{account_id}/topup")
def top_up(
    account_id: int,
    request: TopUpRequest,
    db: Session = Depends(get_db),
):
    with db.begin():
        result = db.execute(
            update(Account)
            .where(Account.id == account_id)
            .values(balance=Account.balance + request.amount_paise)
        )

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Account not found")

        account = db.execute(
            select(Account).where(Account.id == account_id)
        ).scalar_one()

        transaction = Transaction(
            account_id=account_id,
            transaction_type="topup",
            amount=request.amount_paise,
            balance_after=account.balance,
        )
        db.add(transaction)

    return {
        "account_id": account_id,
        "credited_paise": request.amount_paise,
        "balance_paise": account.balance,
    }


@router.post("/accounts/{account_id}/consume")
def consume(
    account_id: int,
    db: Session = Depends(get_db),
):
    with db.begin():
        result = db.execute(
            update(Account)
            .where(
                Account.id == account_id,
                Account.balance >= CONSUME_FEE,
            )
            .values(balance=Account.balance - CONSUME_FEE)
        )

        if result.rowcount == 0:
            account = db.get(Account, account_id)

            if account is None:
                raise HTTPException(
                    status_code=404,
                    detail="Account not found",
                )

            raise HTTPException(
                status_code=409,
                detail="Insufficient balance",
            )

        account = db.execute(
            select(Account).where(Account.id == account_id)
        ).scalar_one()

        transaction = Transaction(
            account_id=account_id,
            transaction_type="consume",
            amount=-CONSUME_FEE,
            balance_after=account.balance,
        )
        db.add(transaction)

    return {
        "account_id": account_id,
        "consumed_paise": CONSUME_FEE,
        "balance_paise": account.balance,
        "message": "API call successful",
    }


@router.get("/accounts/{account_id}/balance")
def check_balance(
    account_id: int,
    db: Session = Depends(get_db),
):
    account = db.get(Account, account_id)

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    return {
        "account_id": account_id,
        "balance_paise": account.balance,
    }


@router.get("/accounts/{account_id}/transactions")
def transaction_history(
    account_id: int,
    db: Session = Depends(get_db),
):
    account = db.get(Account, account_id)

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    transactions = db.execute(
        select(Transaction)
        .where(Transaction.account_id == account_id)
        .order_by(Transaction.id)
    ).scalars().all()

    return {
        "account_id": account_id,
        "transactions": [
            {
                "transaction_id": tx.id,
                "type": tx.transaction_type,
                "amount_paise": tx.amount,
                "balance_after_paise": tx.balance_after,
                "created_at": tx.created_at,
            }
            for tx in transactions
        ],
    }