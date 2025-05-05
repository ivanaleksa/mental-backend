from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert

from app.db.models import PsychologistRequest, Psychologist, client_psychologist
from app.db.enums import RequestStatusEnum
from app.schemas.user import PsychologistRequestResponse


async def get_psychologist_requests_service(
    client_id: int,
    db: AsyncSession
) -> list[PsychologistRequestResponse]:
    """
    Get all psychologist requests for a client.
    """
    stmt = (
        select(PsychologistRequest)
        .where(PsychologistRequest.client_id == client_id,
               PsychologistRequest.status == RequestStatusEnum.PENDING)
        .join(PsychologistRequest.psychologist)
    )
    result = await db.execute(stmt)
    requests = result.scalars().all()

    response_data = []
    for request in requests:
        psychologist: Psychologist = request.psychologist
        response_data.append(
            PsychologistRequestResponse(
                login=psychologist.login,
                first_name=psychologist.first_name,
                last_name=psychologist.last_name,
                sex=psychologist.sex,
                psychologist_photo=psychologist.psychologist_photo,
            )
        )

    return response_data


async def update_psychologist_request_status(
    request_id: int,
    status: RequestStatusEnum,
    client_id: int,
    db: AsyncSession
) -> dict:
    """
    Update the status of a psychologist request and handle acceptance.
    """
    stmt = select(PsychologistRequest).where(PsychologistRequest.request_id == request_id)
    result = await db.execute(stmt)
    request = result.scalar_one_or_none()

    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    if request.client_id != client_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this request")
    if request.status != RequestStatusEnum.PENDING:
        raise HTTPException(status_code=400, detail="Request is not pending")

    request.status = status
    await db.commit()
    await db.refresh(request)

    if status == RequestStatusEnum.APPROVED:
        stmt = insert(client_psychologist).values(
            client_id=request.client_id,
            psychologist_id=request.psychologist_id
        )
        await db.execute(stmt)
        await db.commit()

    return {
        "message": "Request status updated successfully",
        "status": request.status
    }
