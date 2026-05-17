from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.schemas import (
    UserRequest,
    UserResponse,
    AccountRequest,
    AccountResponse,
    AccountsListResponse,
    TransferRequest,
    TransactionResponse,
)

from app.services.crud import (
    create_user, 
    create_account, 
    create_transfer,
    get_user,
    get_accounts,
    get_account,
)
from app.db.database import get_db

router = APIRouter()


@router.post("/users/", response_model=UserResponse, tags=["users"])
async def create_user_endpoint(
    user: UserRequest, 
    db: AsyncSession = Depends(get_db)
):
    return await create_user(db, user)


@router.post("/accounts/", response_model=AccountResponse, tags=["accounts"])
async def create_account_endpoint(
    account: AccountRequest, 
    db: AsyncSession = Depends(get_db),
):
    return await create_account(db, account)


@router.post("/transfers/", response_model=TransactionResponse, tags=["transfers"])
async def create_transfer_endpoint(
    transfer: TransferRequest, 
    db: AsyncSession = Depends(get_db),
):
    return await create_transfer(db, transfer)


@router.get("/users/{user_id}", response_model=UserResponse, tags=["users"])
async def get_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await get_user(db, user_id)


@router.get("/accounts/", response_model=AccountsListResponse, tags=["accounts"])
async def list_accounts(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    return await get_accounts(db, limit, offset)


@router.get("/accounts/{account_id}", response_model=AccountResponse, tags=["accounts"])
async def get_account_endpoint(
    account_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await get_account(db, account_id)
