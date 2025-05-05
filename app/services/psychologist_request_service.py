from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import PsychologistRequest, Psychologist
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
        .where(PsychologistRequest.client_id == client_id, PsychologistRequest.status == RequestStatusEnum.PENDING)
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
