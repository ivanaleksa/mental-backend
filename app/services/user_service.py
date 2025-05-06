from datetime import datetime, timezone
import secrets
import os

from fastapi import HTTPException, status, UploadFile

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas.user import (
    UserCreate, UserResponse, UserLogin,
    UserUpdatePassword, UserResetPass,
    UserUpdate, UserSchema
)
from app.db.models import Client, Psychologist, ConfirmationRequest
from app.db.enums import EmailConfirmationTypeEnum, UserTypeEnum
from app.core import (
    settings, send_confirmation_email,
    hash_password, verify_password, create_jwt_token
)


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
    await db.flush()  # get user_id but without commiting
    await db.refresh(user)

    jwt_token = create_jwt_token(data={"sub": user.login, "user_type": UserTypeEnum.CLIENT})

    user_response = UserResponse(
        user_id=user.client_id,
        login=user.login,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        birthAt=user_data.birthAt,
        is_verified=False,
        sex=user_data.sex,
        user_type=UserTypeEnum.CLIENT,
        client_photo=user.client_photo,
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

    try:
        await send_confirmation_email(user_data.email, confirmation_code, "registration")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to send confirmation email")

    db.add(confirmation_code_request)
    await db.commit()

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

    if login_data.user_type == UserTypeEnum.CLIENT:
        stmt = select(Client).where(Client.login == login_data.login)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
    else:
        stmt = select(Psychologist).where(Psychologist.login == login_data.login)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid login or password",
                            headers={"WWW-Authenticate": "Bearer"})

    jwt_token = create_jwt_token(data={"sub": user.login, "user_type": login_data.user_type})

    user_response = UserResponse(
        user_id=user.client_id if login_data.user_type == UserTypeEnum.CLIENT else user.psychologist_id,
        login=user.login,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        birthAt=user.birthAt.isoformat(),
        is_verified=user.is_verified,
        sex=user.sex,
        user_type=login_data.user_type,
        client_photo=user.client_photo,
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

    if update_info.user_type == UserTypeEnum.CLIENT:
        stmt = select(Client).where(Client.client_id == update_info.user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
    else:
        stmt = select(Psychologist).where(Psychologist.psychologist_id == update_info.user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

    if not user or not verify_password(update_info.old_password, user.password):
        raise HTTPException(status_code=401, detail="Invalid old password")

    user.password = hash_password(update_info.new_password)
    await db.commit()
    await db.refresh(user)

    jwt_token = create_jwt_token(data={"sub": user.login, "user_type": update_info.user_type})

    user_response = UserResponse(
        user_id=user.client_id if update_info.user_type == UserTypeEnum.CLIENT else user.psychologist_id,
        login=user.login,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        birthAt=user.birthAt.isoformat(),
        is_verified=user.is_verified,
        client_photo=user.client_photo,
        jwt_token=jwt_token
    )

    return user_response


async def reset_password_service(reset_data: UserResetPass, db: AsyncSession) -> UserResponse:
    """
    Reset the user's password.

    Args:
        reset_data (UserResetPass): The information needed to reset the password.
        db (AsyncSession): The database session.

    Returns:
        UserResponse: An object containing the updated user's data.
    """

    if reset_data.user_type == UserTypeEnum.CLIENT:
        stmt = select(Client).where(Client.login == reset_data.login, Client.email == reset_data.email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
    else:
        stmt = select(Psychologist).where(Psychologist.login == reset_data.login,
                                          Psychologist.email == reset_data.email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Send confirmation code
    confirmation_code = secrets.token_hex(8)
    confirmation_code_request = ConfirmationRequest(
        client_id=user.client_id if reset_data.user_type == UserTypeEnum.CLIENT else None,
        psychologist_id=user.psychologist_id if reset_data.user_type == UserTypeEnum.PSYCHOLOGIST else None,
        code=confirmation_code,
        email=user.email,
        createdAt=datetime.now(timezone.utc),
        confirmedAt=None,
        type=EmailConfirmationTypeEnum.PASSWORD_RESET
    )

    try:
        await send_confirmation_email(reset_data.email, confirmation_code, "password_reset")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send confirmation email")

    db.add(confirmation_code_request)
    await db.commit()

    return {"message": "Email message with the confirmation code is sent."}


async def update_user_profile_service(user_login: str, update_data: UserUpdate, db: AsyncSession) -> UserSchema:
    """
    Update the user's profile information.

    Args:
        user_login (str): The login of the user to be updated.
        update_data (UserUpdate): The new data for the user.
        db (AsyncSession): The database session.

    Returns:
        UserResponse: An object containing the updated user's data.
    """
    stmt = select(Client).where(Client.login == user_login)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if update_data.first_name is not None:
        user.first_name = update_data.first_name
    if update_data.last_name is not None:
        user.last_name = update_data.last_name
    if update_data.birthAt is not None:
        try:
            birth_date = datetime.fromisoformat(update_data.birthAt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid birthAt format. Use ISO format (yyyy-mm-dd)")

        user.birthAt = birth_date

    await db.commit()
    await db.refresh(user)

    user_response = UserSchema(
        user_id=user.client_id,
        login=user.login,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        birthAt=user.birthAt.isoformat(),
        sex=user.sex,
        client_photo=user.client_photo,
        is_verified=user.is_verified,
        user_type=UserTypeEnum.CLIENT
    )

    return user_response


async def update_user_photo(
        user_login: str,
        update_data: dict,
        db: AsyncSession
) -> dict:
    """
    Update the user's profile photo.
    """

    photo: UploadFile = update_data.get("photo")

    if update_data["user_type"] == UserTypeEnum.CLIENT:
        stmt = select(Client).where(Client.login == user_login)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
    else:
        stmt = select(Psychologist).where(Psychologist.login == user_login)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not photo:
        raise HTTPException(status_code=400, detail="No photo file provided")

    file_extension = os.path.splitext(photo.filename)[1]  # .jpg, .png etc.
    unique_filename = f"{user.login}{file_extension}"
    file_path = os.path.join(settings.MEDIA_DIRECTORY, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await photo.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save photo: {str(e)}")

    user.client_photo = unique_filename
    await db.commit()
    await db.refresh(user)

    return {
        "message": "Profile photo updated successfully",
        "client_photo": user.client_photo
    }
