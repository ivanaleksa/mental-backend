from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import Psychologist, client_psychologist
from app.schemas.user import PsychologistInfoResponse


async def get_client_psychologists_service(
    client_id: int,
    db: AsyncSession
) -> list[PsychologistInfoResponse]:
    """
    Get all psychologists linked to a client via the client_psychologist table.
    """
    stmt = (
        select(Psychologist)
        .join(
            client_psychologist,
            client_psychologist.c.psychologist_id == Psychologist.psychologist_id
        )
        .where(client_psychologist.c.client_id == client_id)
    )
    result = await db.execute(stmt)
    psychologists = result.scalars().all()

    response_data = []
    for psychologist in psychologists:
        response_data.append(
            PsychologistInfoResponse(
                login=psychologist.login,
                first_name=psychologist.first_name,
                last_name=psychologist.last_name,
                sex=psychologist.sex,
                psychologist_photo=psychologist.psychologist_photo
            )
        )

    return response_data
