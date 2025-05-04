from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.db.models.client import Client
from app.db.models.psychologist import Psychologist
from app.db.models.confirmation_request import ConfirmationRequest
from app.db.enums.email_confirmation_type_enum import EmailConfirmationTypeEnum
from app.db.enums.user_type_enum import UserTypeEnum
from app.schemas.user import UserResetPassConfirm
from app.core.security import hash_password


async def confirm_email_service(db: AsyncSession, code: str, user: Client) -> dict:
    stmt = select(ConfirmationRequest).where(ConfirmationRequest.code == code)
    result = await db.execute(stmt)
    confirmation_request = result.scalar_one_or_none()

    if not confirmation_request:
        raise HTTPException(status_code=400, detail="Invalid confirmation code")

    if confirmation_request.confirmedAt:
        raise HTTPException(status_code=400, detail="Code already used")

    if confirmation_request.client_id != user.client_id:
        raise HTTPException(status_code=403, detail="Unauthorized: This code is not for your account")

    expiration_time = confirmation_request.createdAt + timedelta(minutes=settings.CODE_EXPIRE_MINUTES)
    if datetime.now(timezone.utc) > expiration_time:
        raise HTTPException(status_code=400, detail="Confirmation code expired")

    confirmation_request.confirmedAt = datetime.now(timezone.utc)

    if confirmation_request.type == EmailConfirmationTypeEnum.REGISTRATION:
        # Email confirmation is available only for CLIENT type, psychology type can be aligned only after confirmation
        stmt = select(Client).where(Client.client_id == confirmation_request.client_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.is_verified = True
        await db.commit()
        return {"message": "Email verified successfully"}

    raise HTTPException(status_code=400, detail="Invalid confirmation type")


async def pass_reset_confirmation_service(reset_data: UserResetPassConfirm, db: AsyncSession) -> dict:
    if reset_data.new_password != reset_data.confirm_password:
        raise HTTPException(status_code=400, detail="New password and confirm password do not match")

    if reset_data.user_type == UserTypeEnum.CLIENT:
        stmt = select(Client).where(Client.login == reset_data.login)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
    else:
        stmt = select(Psychologist).where(Psychologist.login == reset_data.login)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stmt = select(ConfirmationRequest).where(ConfirmationRequest.code == reset_data.code)
    result = await db.execute(stmt)
    confirmation_request = result.scalar_one_or_none()

    if not confirmation_request:
        raise HTTPException(status_code=400, detail="Invalid confirmation code")

    if confirmation_request.confirmedAt:
        raise HTTPException(status_code=400, detail="Code already used")

    if type(user) is Client and confirmation_request.client_id != user.client_id:
        raise HTTPException(status_code=403, detail="Unauthorized: This code is not for your account")
    if type(user) is Psychologist and confirmation_request.psychologist_id != user.psychologist_id:
        raise HTTPException(status_code=403, detail="Unauthorized: This code is not for your account")

    expiration_time = confirmation_request.createdAt + timedelta(minutes=settings.CODE_EXPIRE_MINUTES)
    if datetime.now(timezone.utc) > expiration_time:
        raise HTTPException(status_code=400, detail="Confirmation code expired")

    if confirmation_request.type != EmailConfirmationTypeEnum.PASSWORD_RESET:
        raise HTTPException(status_code=400, detail="Invalid confirmation type for password reset")

    confirmation_request.confirmedAt = datetime.now(timezone.utc)

    user.password = hash_password(reset_data.new_password)
    await db.commit()

    return {"message": "Password reset successfully"}
