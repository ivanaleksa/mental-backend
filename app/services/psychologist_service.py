import os

from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, delete, func

from app.db.enums import RequestStatusEnum
from app.db.models import Client, Psychologist, Note, PsychologistRequest, client_psychologist
from app.schemas.user import PsychologistInfoResponse
from app.schemas.psychologist import ( 
    DocumentResponse, ClientBase, PaginatedResponse,
    NoteResponse, PsychologistRequestResponse
)
from app.core.config import settings


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
            client_psychologist.c.psychologist_id == Psychologist.client_id
        )
        .where(client_psychologist.c.client_id == client_id)
    )
    result = await db.execute(stmt)
    psychologists = result.scalars().all()

    response_data = []
    for psychologist in psychologists:
        response_data.append(
            PsychologistInfoResponse(
                psychologist_id=psychologist.client_id,
                login=psychologist.login,
                first_name=psychologist.first_name,
                last_name=psychologist.last_name,
                sex=psychologist.sex,
                psychologist_photo=psychologist.client_photo
            )
        )

    return response_data


async def remove_psychologist_from_client_service(
        client_id: int,
        psychologist_id: int,
        db: AsyncSession
) -> dict:
    """
    Remove the relationship between a client and a psychologist.
    """
    stmt = delete(client_psychologist).where(
        and_(
            client_psychologist.c.client_id == client_id,
            client_psychologist.c.psychologist_id == psychologist_id
        )
    )
    result = await db.execute(stmt)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Relationship not found")

    return {"message": "Psychologist removed successfully"}


async def get_psychologist_document(
    psychologist_id: int,
    db: AsyncSession
) -> DocumentResponse:
    stmt = select(Psychologist).where(Psychologist.client_id == psychologist_id)
    result = await db.execute(stmt)
    psychologist = result.scalar_one_or_none()

    if not psychologist:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse(document_path=psychologist.psychologist_docs if psychologist.psychologist_docs else "")


async def revert_to_client(
    psychologist_id: int,
    db: AsyncSession
) -> dict:
    stmt = select(Psychologist).where(Psychologist.client_id == psychologist_id)
    result = await db.execute(stmt)
    psychologist = result.scalar_one_or_none()

    if not psychologist:
        raise HTTPException(status_code=404, detail="Psychologist not found")

    if psychologist.psychologist_docs and os.path.exists(os.path.join(settings.DOCUMENTS_DIRECTORY, psychologist.psychologist_docs)):
        os.remove(os.path.join(settings.DOCUMENTS_DIRECTORY, psychologist.psychologist_docs))

    client = Client(
        login=psychologist.login,
        password=psychologist.password,
        email=psychologist.email,
        first_name=psychologist.first_name,
        last_name=psychologist.last_name,
        birthAt=psychologist.birthAt,
        sex=psychologist.sex,
        client_photo=psychologist.client_photo,
        is_verified=True
    )
    db.add(client)
    await db.commit()
    await db.refresh(client)

    await db.delete(psychologist)
    await db.commit()

    return {"message": "Psychologist reverted to client successfully", "client_id": client.client_id}


async def get_psychologist_clients(
    psychologist_id: int,
    db: AsyncSession,
    page: int = 1,
    size: int = 10
) -> PaginatedResponse[ClientBase]:
    offset = (page - 1) * size

    stmt = (
        select(Client)
        .join(client_psychologist)
        .where(client_psychologist.c.psychologist_id == psychologist_id)
        .offset(offset)
        .limit(size)
    )
    result = await db.execute(stmt)
    clients = result.scalars().all()

    total_stmt = (
        select(func.count())
        .select_from(client_psychologist)
        .where(client_psychologist.c.psychologist_id == psychologist_id)
    )
    total_result = await db.execute(total_stmt)
    total = total_result.scalar()

    client_responses = [
        ClientBase(
            client_id=c.client_id,
            login=c.login,
            email=c.email,
            first_name=c.first_name,
            last_name=c.last_name,
            birthAt=c.birthAt,
            sex=c.sex,
            client_photo=c.client_photo,
            is_verified=c.is_verified
        )
        for c in clients
    ]

    return PaginatedResponse[ClientBase](items=client_responses, total=total, page=page, size=size)


async def get_client_notes_for_psychologist(
    psychologist_id: int,
    client_id: int,
    db: AsyncSession,
    page: int = 1,
    size: int = 10
) -> PaginatedResponse[NoteResponse]:
    offset = (page - 1) * size

    stmt_check = (
        select(client_psychologist)
        .where(client_psychologist.c.psychologist_id == psychologist_id)
        .where(client_psychologist.c.client_id == client_id)
    )
    result_check = await db.execute(stmt_check)
    if not result_check.first():
        raise HTTPException(status_code=403, detail="Client is not assigned to this psychologist")

    total_stmt = (
        select(func.count())
        .select_from(Note)
        .where(Note.client_id == client_id)
    )
    total_result = await db.execute(total_stmt)
    total = total_result.scalar()

    stmt = (
        select(Note)
        .where(Note.client_id == client_id)
        .offset(offset)
        .limit(size)
    )
    result = await db.execute(stmt)
    notes = result.scalars().all()

    note_responses = [
        NoteResponse(
            note_id=n.note_id,
            title=n.title,
            body=n.body,
            createdAt=n.createdAt,
            emotions=n.emotions if n.emotions else []
        )
        for n in notes
    ]

    return PaginatedResponse[NoteResponse](items=note_responses, total=total, page=page, size=size)


async def search_client_by_login(
    login: str,
    db: AsyncSession
) -> ClientBase:
    stmt = select(Client).where(Client.login == login)
    result = await db.execute(stmt)
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return ClientBase(
        client_id=client.client_id,
        login=client.login,
        email=client.email,
        first_name=client.first_name,
        last_name=client.last_name,
        birthAt=client.birthAt,
        sex=client.sex,
        client_photo=client.client_photo,
        is_verified=client.is_verified
    )

async def create_psychologist_request(
    psychologist_id: int,
    client_id: int,
    db: AsyncSession
) -> PsychologistRequestResponse:
    stmt = select(Client).where(Client.client_id == client_id)
    result = await db.execute(stmt)
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    stmt = select(Psychologist).where(Psychologist.client_id == psychologist_id)
    result = await db.execute(stmt)
    psychologist = result.scalar_one_or_none()
    if not psychologist:
        raise HTTPException(status_code=404, detail="Psychologist not found")

    stmt = (
        select(PsychologistRequest)
        .where(PsychologistRequest.psychologist_id == psychologist_id)
        .where(PsychologistRequest.client_id == client_id)
        .where(PsychologistRequest.status == RequestStatusEnum.PENDING)
    )
    result = await db.execute(stmt)
    existing_request = result.scalar_one_or_none()
    if existing_request:
        raise HTTPException(status_code=400, detail="Request already exists")

    stmt = (
        select(client_psychologist)
        .where(client_psychologist.c.psychologist_id == psychologist_id)
        .where(client_psychologist.c.client_id == client_id)
    )
    result = await db.execute(stmt)
    if result.first():
        raise HTTPException(status_code=400, detail="Client is already assigned to this psychologist")

    request = PsychologistRequest(
        psychologist_id=psychologist_id,
        client_id=client_id,
        status=RequestStatusEnum.PENDING
    )
    db.add(request)
    await db.commit()
    await db.refresh(request)

    return PsychologistRequestResponse(
        request_id=request.request_id,
        psychologist_id=request.psychologist_id,
        client_id=request.client_id,
        status=request.status
    )


async def remove_client_from_psychologist(
    psychologist_id: int,
    client_id: int,
    db: AsyncSession
) -> dict:
    """
    Remove a client from the psychologist's client list by deleting the many-to-many relationship.
    """
    stmt_psych = select(Psychologist).where(Psychologist.client_id == psychologist_id)
    result_psych = await db.execute(stmt_psych)
    psychologist = result_psych.scalar_one_or_none()
    if not psychologist:
        raise HTTPException(status_code=404, detail="Psychologist not found")

    stmt_client = select(Client).where(Client.client_id == client_id)
    result_client = await db.execute(stmt_client)
    client = result_client.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    stmt_relation = (
        select(client_psychologist)
        .where(client_psychologist.c.psychologist_id == psychologist_id)
        .where(client_psychologist.c.client_id == client_id)
    )
    result_relation = await db.execute(stmt_relation)
    relation = result_relation.first()
    if not relation:
        raise HTTPException(status_code=400, detail="No relationship exists between psychologist and client")

    await db.execute(
        delete(client_psychologist)
        .where(client_psychologist.c.psychologist_id == psychologist_id)
        .where(client_psychologist.c.client_id == client_id)
    )
    await db.commit()

    return {"message": "Client removed from psychologist's client list successfully", "client_id": client_id}
