from datetime import datetime, timezone
import secrets

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas.user import UserCreate, UserResponse, UserLogin, UserUpdatePassword
from app.core.security import hash_password, create_jwt_token, verify_password
from app.db.models.client import Client
from app.db.models.confirmation_request import ConfirmationRequest
from app.db.enums.email_confirmation_type_enum import EmailConfirmationTypeEnum
from app.core.email import send_confirmation_email


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

    # Convert the birthdate string to a datetime object
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
        sex=user_data.sex,
        is_verified=False
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    jwt_token = create_jwt_token({"user_id": user.client_id})

    user_response = UserResponse(
        user_id=user.client_id,
        login=user.login,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        birthAt=user_data.birthAt,
        is_verified=False,
        jwt_token=jwt_token
    )

    # Send confirmation code
    confirmation_code = secrets.token_hex(8)
    confirmation_code_request = ConfirmationRequest(
        client_id=user.client_id,
        psychologist_id=None,
        code=confirmation_code,
        email=user.email,
        createdAt=datetime.now(timezone.utc),
        confirmedAt=None,
        type=EmailConfirmationTypeEnum.REGISTRATION
    )
    db.add(confirmation_code_request)
    await db.commit()

    await send_confirmation_email(user_data.email, confirmation_code, "registration")

    return user_response


async def login_user_service(login_data: UserLogin, db: AsyncSession) -> UserResponse:
    """
    Authenticate a user and return their data.

    Args:
        login_data (UserLogin): The login credentials of the user.
        db (AsyncSession): The database session.

    Returns:
        UserResponse: An object containing the authenticated user's data.
    """

    stmt = select(Client).where(Client.login == login_data.login)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid login or password",
                            headers={"WWW-Authenticate": "Bearer"})

    jwt_token = create_jwt_token(data={"sub": user.login})

    user_response = UserResponse(
        user_id=user.client_id,
        login=user.login,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        birthAt=user.birthAt.isoformat(),
        is_verified=user.is_verified,
        jwt_token=jwt_token
    )

    return user_response


async def update_password_service(update_info: UserUpdatePassword, db: AsyncSession) -> UserResponse:
    """
    Update the user's password.

    Args:
        update_info (UserUpdatePassword): The information needed to update the password.
        db (AsyncSession): The database session.

    Returns:
        UserResponse: An object containing the updated user's data.
    """

    stmt = select(Client).where(Client.client_id == update_info.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(update_info.old_password, user.password):
        raise HTTPException(status_code=401, detail="Invalid old password")

    user.password = hash_password(update_info.new_password)
    await db.commit()
    await db.refresh(user)

    jwt_token = create_jwt_token(data={"sub": user.login})

    user_response = UserResponse(
        user_id=user.client_id,
        login=user.login,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        birthAt=user.birthAt.isoformat(),
        jwt_token=jwt_token
    )

    return user_response
