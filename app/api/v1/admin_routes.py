from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.client_request import ClientRequestUpdate
from app.services.client_request_service import update_client_request
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
