from datetime import datetime, timezone, timedelta
import secrets

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from app.schemas import (
    UserCreate, UserResponse, UserLogin,
    UserUpdatePassword, UserResetPass, UserResetPassConfirm
)
from app.db.session import get_db
from app.db.models import Client, Psychologist, ConfirmationRequest
from app.db.enums.email_confirmation_type_enum import EmailConfirmationTypeEnum
from app.services.user_service import register_user_service, login_user_service, update_password_service, \
    reset_password_service
from app.services.auth_service import confirm_email_service, pass_reset_confirmation_service
from app.dependencies import get_current_user
from app.core import send_confirmation_email, settings

router = APIRouter(tags=["UserAuthentication"])


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


@router.post("/user/reset-password")
async def reset_password(reset_data: UserResetPass, db: AsyncSession = Depends(get_db)):
    """
    Reset the password of a user.
    """
    try:
        return await reset_password_service(reset_data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/user/reset-password/confirm")
async def confirm_reset_password(reset_data: UserResetPassConfirm,
                                 db: AsyncSession = Depends(get_db)):
    """
    Confirm the password reset using a confirmation code.
    """
    try:
        return await pass_reset_confirmation_service(reset_data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/user/change-password", response_model=UserResponse)
async def change_password(update_info: UserUpdatePassword,
                          current_user: Client | Psychologist = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    """
    Change the password of a user.
    """
    try:
        return await update_password_service(update_info, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/email/confirm/{code}")
async def confirm_email(code: str, current_user: Client | Psychologist = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    """
    Confirm the email of a user using a confirmation code.
    """
    try:
        return await confirm_email_service(db, code, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/email/send-new")
async def send_new_email_confirmation(current_user: Client | Psychologist = Depends(get_current_user),
                                      db: AsyncSession = Depends(get_db)):
    """
    Send a new email confirmation email in the case of needing one more (for example, the previous is expired).
        - If no confirmation code exists, a new one is generated and sent.
        - If a code exists and has not expired, returns an error.
        - If a code exists and has expired, the old one is deleted, a new one is generated, and sent.
    """
    if current_user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified.")

    stmt = select(ConfirmationRequest).where(
        ConfirmationRequest.client_id == current_user.client_id,
        ConfirmationRequest.type == EmailConfirmationTypeEnum.REGISTRATION,
        ConfirmationRequest.confirmedAt.is_(None)
    )
    result = await db.execute(stmt)
    confirmation_request = result.scalar_one_or_none()

    if confirmation_request:
        expiration_time = confirmation_request.createdAt + timedelta(minutes=settings.CODE_EXPIRE_MINUTES)
        if datetime.now(timezone.utc) <= expiration_time:
            raise HTTPException(status_code=400, detail="Previous confirmation code has not expired yet.")
        else:
            await db.execute(
                delete(ConfirmationRequest).where(ConfirmationRequest.client_id == confirmation_request.client_id))
            await db.commit()

    confirmation_code = secrets.token_hex(8)
    new_confirmation_request = ConfirmationRequest(
        client_id=current_user.client_id,  # Because psychologist won't be able to send this confirmation
        psychologist_id=None,
        code=confirmation_code,
        email=current_user.email,
        createdAt=datetime.now(timezone.utc),
        confirmedAt=None,
        type=EmailConfirmationTypeEnum.REGISTRATION
    )

    try:
        await send_confirmation_email(current_user.email, confirmation_code, "registration")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send confirmation email")

    db.add(new_confirmation_request)
    await db.commit()

    return {"message": "Confirmation email sent."}
