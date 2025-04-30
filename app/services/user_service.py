from datetime import datetime

from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas.user import UserCreate, UserResponse
from app.core.security import hash_password, create_jwt_token
from app.db.models.client import Client


async def register_user_service(user_data: UserCreate, db: AsyncSession) -> UserResponse:
    """
    Register a new user in the database.

    Args:
        user_data (UserCreate): The data of the user to be registered.
        db (AsyncSession): The database session.

    Returns:
        UserResponse: An object containing the registered user's data.
    """
    
    stmt_email = select(Client).where(Client.email == user_data.email)
    result_email = await db.execute(stmt_email)
    if result_email.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    stmt_login = select(Client).where(Client.login == user_data.login)
    result_login = await db.execute(stmt_login)
    if result_login.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Login already taken")
    
    hashed_password = hash_password(user_data.password)

    # Convert the birth date string to a datetime object
    try:
        birth_date = datetime.fromisoformat(user_data.birthAt)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid birthAt format. Use ISO format (yyyy-mm-dd)")

    user = Client(
        login=user_data.login,
        email=user_data.email,
        password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        birthAt=birth_date,
        sex=user_data.sex
    )

    jwt_token = create_jwt_token({"user_id": user.client_id})

    user_response = UserResponse(
        user_id=user.client_id,
        login=user.login,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        birthAt=user_data.birthAt,
        jwt_token=jwt_token
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user_response
