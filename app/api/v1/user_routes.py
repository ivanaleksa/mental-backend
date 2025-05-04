from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.client import Client
from app.schemas.user import UserSchema, UserUpdate
from app.services.user_service import update_user_profile_service
from app.dependencies import get_current_user
from app.db.session import get_db


router = APIRouter(tags=["User"])


@router.get("/user/me", response_model=UserSchema)
async def get_user_me(current_user: Client = Depends(get_current_user)) -> UserSchema:
    """
    Get the current user's information.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_info = UserSchema(
        login=current_user.login,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        birthAt=current_user.birthAt.isoformat(),
        is_verified=current_user.is_verified,
        sex=current_user.sex,
        client_photo=current_user.client_photo,
    )
    
    return user_info


@router.patch("/user/me", response_model=UserSchema)
async def update_profile(
    update_data: UserUpdate,
    current_user: Client = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)):
    """
    Update the current user's profile information.
    """
    try:
        return await update_user_profile_service(current_user.login, update_data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
