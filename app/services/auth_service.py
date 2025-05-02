from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.db.models.client import Client
from app.db.models.confirmation_request import ConfirmationRequest
from app.db.enums.email_confirmation_type_enum import EmailConfirmationTypeEnum


async def confirm_email_service(db: AsyncSession, code: str, client_id: int) -> dict:
    stmt = select(ConfirmationRequest).where(ConfirmationRequest.code == code)
    result = await db.execute(stmt)
    confirmation_request = result.scalar_one_or_none()
    
    if not confirmation_request:
        raise HTTPException(status_code=400, detail="Invalid confirmation code")
    
    if confirmation_request.confirmedAt:
        raise HTTPException(status_code=400, detail="Code already used")

    if confirmation_request.client_id != client_id:
        raise HTTPException(status_code=403, detail="Unauthorized: This code is not for your account")
    
    expiration_time = confirmation_request.createdAt + timedelta(minutes=settings.CODE_EXPIRE_MINUTES)
    if datetime.now(timezone.utc) > expiration_time:
        raise HTTPException(status_code=400, detail="Confirmation code expired")

    confirmation_request.confirmedAt = datetime.now(timezone.utc)
    
    if confirmation_request.type == EmailConfirmationTypeEnum.REGISTRATION:
        stmt = select(Client).where(Client.client_id == confirmation_request.client_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.is_verified = True
        await db.commit()
        return {"message": "Email verified successfully"}
    
    raise HTTPException(status_code=400, detail="Invalid confirmation type")
