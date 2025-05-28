from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.models import Admin, Client, Psychologist, ClientRequest
from app.schemas.admin import (
    PaginatedResponse, ClientResponse, PsychologistResponse, AdminResponse,
    ClientRequestResponse, AdminLoginRequest, AdminLoginResponse
)
from app.core.security import verify_password, hash_password, create_jwt_token


async def get_all_clients(
    db: AsyncSession,
    page: int = 1,
    size: int = 10
) -> PaginatedResponse:
    offset = (page - 1) * size

    total_stmt = select(func.count()).select_from(Client)
    total_result = await db.execute(total_stmt)
    total = total_result.scalar()

    stmt = select(Client).offset(offset).limit(size)
    result = await db.execute(stmt)
    clients = result.scalars().all()

    client_responses = [
        ClientResponse(
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

    return PaginatedResponse(items=client_responses, total=total, page=page, size=size)


async def get_all_psychologists(
    db: AsyncSession,
    page: int = 1,
    size: int = 10
) -> PaginatedResponse:
    offset = (page - 1) * size

    total_stmt = select(func.count()).select_from(Psychologist)
    total_result = await db.execute(total_stmt)
    total = total_result.scalar()

    stmt = select(Psychologist).offset(offset).limit(size)
    result = await db.execute(stmt)
    psychologists = result.scalars().all()

    psychologist_responses = [
        PsychologistResponse(
            psychologist_id=p.client_id,
            login=p.login,
            email=p.email,
            first_name=p.first_name,
            last_name=p.last_name,
            birthAt=p.birthAt,
            sex=p.sex,
            psychologist_photo=p.client_photo,
            psychologist_docs=p.psychologist_docs
        )
        for p in psychologists
    ]

    return PaginatedResponse(items=psychologist_responses, total=total, page=page, size=size)


async def delete_client(
    user_id: int,
    db: AsyncSession
) -> dict:
    stmt = select(Client).where(Client.client_id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Client not found")
    await db.delete(user)

    await db.commit()
    return {"message": f"{user.login} deleted successfully"}


async def delete_psychologist(
    user_id: int,
    db: AsyncSession
) -> dict:
    stmt = select(Psychologist).where(Psychologist.psychologist_id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Psychologist not found")
    await db.delete(user)

    await db.commit()
    return {"message": f"{user.login} deleted successfully"}


async def get_all_confirmation_requests(
    db: AsyncSession,
    page: int = 1,
    size: int = 10
) -> PaginatedResponse:
    offset = (page - 1) * size

    total_stmt = select(func.count()).select_from(ClientRequest)
    total_result = await db.execute(total_stmt)
    total = total_result.scalar()

    stmt = select(ClientRequest).offset(offset).limit(size)
    result = await db.execute(stmt)
    requests = result.scalars().all()

    request_responses = [
        ClientRequestResponse(
            request_id=r.request_id,
            client_id=r.client_id,
            document=r.document,
            status=r.status,
            rejection_reason=r.rejection_reason,
            created_at=r.created_at,
            updated_at=r.updated_at
        )
        for r in requests
    ]

    return PaginatedResponse(items=request_responses, total=total, page=page, size=size)


async def get_all_admins(
    db: AsyncSession,
    page: int = 1,
    size: int = 10
) -> PaginatedResponse:
    offset = (page - 1) * size

    total_stmt = select(func.count()).select_from(Admin)
    total_result = await db.execute(total_stmt)
    total = total_result.scalar()

    stmt = select(Admin).offset(offset).limit(size)
    result = await db.execute(stmt)
    admins = result.scalars().all()

    admin_responses = [AdminResponse(admin_id=a.admin_id, login=a.login) for a in admins]

    return PaginatedResponse(items=admin_responses, total=total, page=page, size=size)

async def create_admin(
    login: str,
    password: str,
    db: AsyncSession
) -> AdminResponse:
    stmt = select(Admin).where(Admin.login == login)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Admin with this login already exists")

    new_admin = Admin(login=login, password=hash_password(password))
    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)

    return AdminResponse(admin_id=new_admin.admin_id, login=new_admin.login)


async def login_admin_service(login_data: AdminLoginRequest, db: AsyncSession) -> AdminLoginResponse:
    stmt = select(Admin).where(Admin.login == login_data.login)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid login or password",
                            headers={"WWW-Authenticate": "Bearer"})

    jwt_token = create_jwt_token(data={"sub": user.login})

    user_response = AdminLoginResponse(
        admin_id=user.admin_id,
        login=user.login,
        jwt_token=jwt_token
    )

    return user_response
