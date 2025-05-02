from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserResponse, UserLogin, UserUpdatePassword
from app.db.session import get_db
from app.db.models.client import Client
from app.services.user_service import register_user_service, login_user_service, update_password_service
from app.services.auth_service import confirm_email_service
from app.dependencies import get_current_user

router = APIRouter()


@router.get("/healthcheck")
async def hello_world():
    return {"message": "Hello, world!"}


@router.post("/user/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user and return their info with a JWT token.
    """
    try:
        return await register_user_service(user_data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/user/login", response_model=UserResponse)
async def login_user(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Login a user and return their info with a JWT token.
    """
    try:
        return await login_user_service(login_data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/user/change-password", response_model=UserResponse)
async def change_password(update_info: UserUpdatePassword, db: AsyncSession = Depends(get_db)):
    """
    Change the password of a user.
    """
    try:
        return await update_password_service(update_info, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/email/confirm/{code}")
async def confirm_email(code: str, current_user: Client = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    """
    Confirm the email of a user using a confirmation code.
    """
    try:
        return await confirm_email_service(db, code, current_user.client_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/email/send-new")
async def send_new_email_confirmation(current_user: Client = Depends(get_current_user),
                                      db: AsyncSession = Depends(get_db)):
    """
    Send a new email confirmation email in the case of needing one more (for example, the previous is expired)
    """
    pass
