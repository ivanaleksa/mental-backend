from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from jose import JWTError, jwt

from app.core.config import settings
from app.db.models.client import Client
from app.db.models.psychologist import Psychologist
from app.db.session import get_db
from app.db.enums.user_type_enum import UserTypeEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="app/v1/user/login", scheme_name="UserLogin")


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: AsyncSession = Depends(get_db)) -> Client | Psychologist:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        login: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        if login is None or user_type is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    if user_type == UserTypeEnum.CLIENT:
        stmt = select(Client).where(Client.login == login)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
    elif user_type == UserTypeEnum.PSYCHOLOGIST:
        stmt = select(Psychologist).where(Psychologist.login == login)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user
