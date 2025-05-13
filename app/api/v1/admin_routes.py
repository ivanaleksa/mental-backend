from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.client_request import ClientRequestUpdate
from app.schemas.admin import (
    PaginatedResponse, ClientResponse, 
    PsychologistResponse, ClientRequestResponse,
    AdminResponse, AdminCreate
)
from app.services.client_request_service import update_client_request
from app.services.admin_service import (
    get_all_clients, get_all_psychologists, 
    delete_client, delete_psychologist, get_all_confirmation_requests,
    get_all_admins, create_admin
)
from app.dependencies import get_db, get_current_admin

router = APIRouter(tags=["Admin"])


@router.patch("/admin/client-request/{application_id}")
async def update_psychologist_application_status(
        application_id: int,
        update_data: ClientRequestUpdate,
        admin_user=Depends(get_current_admin),
        db: AsyncSession = Depends(get_db)
):
    """
    Update the status of a psychologist application (admin only).
    """
    return await update_client_request(application_id, update_data, db)


@router.get("/admin/clients", response_model=PaginatedResponse[ClientResponse])
async def get_clients(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    admin_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get all clients with pagination."""
    return await get_all_clients(db, page, size)


@router.get("/admin/psychologists", response_model=PaginatedResponse[PsychologistResponse])
async def get_psychologists(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    admin_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get all psychologists with pagination."""
    return await get_all_psychologists(db, page, size)


@router.delete("/admin/client/delete/{user_id}")
async def delete_client_endpoint(
    user_id: int,
    admin_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete a user (client, psychologist, or admin)."""
    return await delete_client(user_id, db)


@router.delete("/admin/psychologist/delete/{user_id}")
async def delete_psychologist_endpoint(
    user_id: int,
    admin_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete a user (client, psychologist, or admin)."""
    return await delete_psychologist(user_id, db)


@router.get("/admin/client-requests", response_model=PaginatedResponse[ClientRequestResponse])
async def get_confirmation_requests(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    admin_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get all confirmation requests with pagination."""
    return await get_all_confirmation_requests(db, page, size)


@router.get("/admin/admins", response_model=PaginatedResponse[AdminResponse])
async def get_admins(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    admin_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get all admins with pagination."""
    return await get_all_admins(db, page, size)


@router.post("/admin/create", response_model=AdminResponse)
async def create_admin_endpoint(
    admin: AdminCreate,
    admin_user=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new admin."""
    return await create_admin(admin.login, admin.password, db)
