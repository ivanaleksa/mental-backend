from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserResponse, UserLogin, UserUpdatePassword
from app.db.session import get_db
from app.services.user_service import register_user_service, login_user_service, update_password_service

router = APIRouter()


@router.get("/healthcheck")
async def hello_world():
    return {"message": "Hello, world!"}


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Refister a new user and return their info with a JWT token.
    """
    try:
        return await register_user_service(user_data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=UserResponse)
async def login_user(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Login a user and return their info with a JWT token.
    """
    try:
        return await login_user_service(login_data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/change-password", response_model=UserResponse)
async def change_password(update_info: UserUpdatePassword, db: AsyncSession = Depends(get_db)):
    """
    Change the password of a user.
    """
    try:
        return await update_password_service(update_info, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
