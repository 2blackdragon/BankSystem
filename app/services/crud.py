import random
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from datetime import datetime

from app.chaos.failures import inject_random_failure
from app.db.models import User, Account, Transaction
from app.schemas.schemas import (
    UserRequest, 
    AccountRequest, 
    TransferRequest
)


logger = logging.getLogger(__name__)


async def create_user(db: AsyncSession, user: UserRequest) -> User:
    # Исправлено: select вместо query
    result = await db.execute(
        select(User).where(User.username == user.username)
    )
    user_exist = result.scalar_one_or_none()
    
    if user_exist:
        logger.warning("user_creation_rejected_duplicate_username", extra={
            "event": "user_creation_rejected",
            "error_type": "duplicate_username",
            "username": user.username,
        })
        raise HTTPException(status_code=409, detail="Username already exists")

    db_user = User(
        username=user.username,
        hashed_password=user.password  # в реальном проекте хешировать!
    )
    db.add(db_user)  # убрал await, т.к. add не асинхронный

    try:
        await db.commit()
        await db.refresh(db_user)
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.error("user_creation_database_failure", extra={
            "event": "user_creation_failed",
            "error_type": "database_error",
            "username": user.username,
            "db_error": str(exc),
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Database error")

    logger.info("user_created", extra={
        "event": "user_created",
        "user_id": db_user.id,
        "username": db_user.username,
    })
    return db_user


async def create_account(db: AsyncSession, account: AccountRequest) -> Account:
    # Исправлено: select вместо query
    result = await db.execute(
        select(User).where(User.id == account.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        logger.warning("account_creation_rejected_user_not_found", extra={
            "event": "account_creation_rejected",
            "error_type": "user_not_found",
            "user_id": account.user_id,
            "account_number": account.account_number,
        })
        raise HTTPException(status_code=404, detail="User not found")

    db_account = Account(
        user_id=account.user_id,
        account_number=account.account_number,
        balance=account.balance,
        currency=account.currency
    )
    db.add(db_account)  # убрал await

    try:
        await db.commit()
        await db.refresh(db_account)  # добавил await
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.error("account_creation_database_failure", extra={
            "event": "account_creation_failed",
            "error_type": "database_error",
            "user_id": account.user_id,
            "account_number": account.account_number,
            "db_error": str(exc),
        }, exc_info=True)
        if "unique" in str(exc).lower() and "account_number" in str(exc).lower():
            raise HTTPException(status_code=409, detail="Account number already exists")
        raise HTTPException(status_code=500, detail="Database error")

    logger.info("account_created", extra={
        "event": "account_created",
        "account_id": db_account.id,
        "account_number": db_account.account_number,
        "user_id": account.user_id,
        "currency": db_account.currency,
        "initial_balance": db_account.balance,
    })

    if random.random() < 0.12:
        logger.warning("account_created_with_low_balance", extra={
            "event": "low_initial_balance_warning",
            "account_id": db_account.id,
            "balance": db_account.balance,
            "currency": db_account.currency,
        })

    return db_account


async def create_transfer(db: AsyncSession, transfer: TransferRequest) -> Transaction:
    # Исправлено: select вместо query
    result = await db.execute(
        select(Account).where(Account.id == transfer.from_account_id)
    )
    from_acc = result.scalar_one_or_none()
    
    if not from_acc:
        logger.warning("transfer_rejected_source_account_not_found", extra={
            "event": "transfer_rejected",
            "error_type": "source_account_not_found",
            "from_account_id": transfer.from_account_id,
        })
        raise HTTPException(status_code=404, detail="Source account not found")

    # Исправлено: select вместо query
    result = await db.execute(
        select(Account).where(Account.id == transfer.to_account_id)
    )
    to_acc = result.scalar_one_or_none()
    
    if not to_acc:
        logger.warning("transfer_rejected_destination_account_not_found", extra={
            "event": "transfer_rejected",
            "error_type": "destination_account_not_found",
            "to_account_id": transfer.to_account_id,
        })
        raise HTTPException(status_code=404, detail="Destination account not found")

    if from_acc.currency != transfer.currency or to_acc.currency != transfer.currency:
        logger.warning("transfer_rejected_currency_mismatch", extra={
            "event": "transfer_rejected",
            "error_type": "currency_mismatch",
            "transfer_currency": transfer.currency,
            "from_currency": from_acc.currency,
            "to_currency": to_acc.currency,
        })
        raise HTTPException(status_code=400, detail="Currency mismatch")

    if from_acc.balance < transfer.amount:
        logger.warning("transfer_rejected_insufficient_funds", extra={
            "event": "transfer_rejected",
            "error_type": "insufficient_funds",
            "from_account_id": from_acc.id,
            "balance": from_acc.balance,
            "requested_amount": transfer.amount,
        })
        raise HTTPException(status_code=400, detail="Insufficient funds")

    db_tx = Transaction(
        from_account_id=transfer.from_account_id,
        to_account_id=transfer.to_account_id,
        amount=transfer.amount,
        currency=transfer.currency,
        timestamp=datetime.utcnow(),
        status="completed"
    )

    from_acc.balance -= transfer.amount
    to_acc.balance += transfer.amount

    db.add(db_tx)  # убрал await

    inject_random_failure()

    try:
        await db.commit()
        await db.refresh(db_tx)
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.error("transfer_database_failure", extra={
            "event": "transfer_failed",
            "error_type": "database_error",
            "from_account_id": transfer.from_account_id,
            "to_account_id": transfer.to_account_id,
            "amount": transfer.amount,
            "db_error": str(exc),
        }, exc_info=True)
        raise HTTPException(status_code=500, detail="Database error")

    logger.info("transfer_completed", extra={
        "event": "transfer_completed",
        "transaction_id": db_tx.id,
        "from_account_id": transfer.from_account_id,
        "to_account_id": transfer.to_account_id,
        "amount": transfer.amount,
        "currency": transfer.currency,
    })

    return db_tx


async def get_user(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404, "User not found")

    return user


async def get_account(db: AsyncSession, account_id: int) -> Account:
    result = await db.execute(
        select(Account).where(Account.id == account_id)
    )
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(404, "Account not found")

    return account


async def get_accounts(
    db: AsyncSession,
    limit: int = 100,
    offset: int = 0,
) -> list[Account]:
    stmt = (
        select(Account)
        .order_by(Account.id)
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
