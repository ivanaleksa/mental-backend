import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Client
from app.db.enums import UserTypeEnum, RequestStatusEnum
from app.schemas.user import UserSchema, UserUpdate
from app.services.user_service import update_user_profile_service, update_user_photo
from app.services.client_request_service import create_psychologist_application, get_client_request_status_service
from app.services.psychologist_request_service import get_psychologist_requests_service, \
    update_psychologist_request_status
from app.services.psychologist_service import get_client_psychologists_service, remove_psychologist_from_client_service
from app.dependencies import get_current_user
from app.db.session import get_db
from app.core.config import settings

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


@router.patch("/user/me/photo")
async def update_profile_photo(
        photo: UploadFile = Form(None, description="Profile photo file"),
        user_type: UserTypeEnum = Form(..., description="Type of user (client or psychologist)"),
        current_user: Client = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Update the profile photo of the authenticated user.
    """
    if not photo:
        raise HTTPException(status_code=400, detail="No photo file provided")

    if photo.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400,
                            detail=f"File size exceeds {settings.MAX_FILE_SIZE / (1024 * 1024)}MB limit")

    file_extension = os.path.splitext(photo.filename.lower())[1]
    if file_extension not in settings.ALLOWED_PROFILE_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use .jpg, .jpeg, or .png")

    update_data = {"photo": photo, "user_type": user_type}
    return await update_user_photo(current_user.login, update_data, db)


@router.post("/user/apply-for-psychologist")
async def apply_for_psychologist(
        document: UploadFile = Form(..., description="Document proving psychologist qualification"),
        current_user: Client = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if not document:
        raise HTTPException(status_code=400, detail="No document file provided")

    if document.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400,
                            detail=f"File size exceeds {settings.MAX_FILE_SIZE / (1024 * 1024)}MB limit")

    return await create_psychologist_application(current_user.client_id, document, db)


@router.get("/user/client-request-status")
async def get_client_request_status(
        current_user: Client = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Get the status of the client's psychologist application.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return await get_client_request_status_service(current_user.client_id, db)


@router.get("/user/psychologist-request")
async def get_psychologist_requests(
        current_user: Client = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Get all psychologist requests for the authenticated client.
    """
    requests = await get_psychologist_requests_service(current_user.client_id, db)
    if not requests:
        return {"message": "No psychologist requests found", "requests": []}
    return {"requests": requests}


@router.patch("/user/psychologist-request/{request_id}/reject")
async def reject_psychologist_request(
        request_id: int,
        current_user: Client = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Reject a psychologist request.
    """
    return await update_psychologist_request_status(request_id, RequestStatusEnum.REJECTED, current_user.client_id, db)


@router.patch("/user/psychologist-request/{request_id}/accept")
async def accept_psychologist_request(
        request_id: int,
        current_user: Client = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Accept a psychologist request and link client with psychologist.
    """
    return await update_psychologist_request_status(request_id, RequestStatusEnum.APPROVED, current_user.client_id, db)


@router.get("/user/psychologists")
async def get_client_psychologists(
        current_user: Client = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Get all psychologists linked to the authenticated client.
    """
    psychologists = await get_client_psychologists_service(current_user.client_id, db)
    if not psychologists:
        return {"message": "No psychologists found", "psychologists": []}
    return {"psychologists": psychologists}


@router.delete("/user/{psychologist_id}")
async def remove_client_psychologist(
        psychologist_id: int,
        current_user: Client = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Remove a psychologist from the authenticated client's list.
    """
    return await remove_psychologist_from_client_service(current_user.client_id, psychologist_id, db)
