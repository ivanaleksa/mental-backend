from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from jose import JWTError, jwt

from app.core.config import settings
from app.db.models.client import Client
from app.db.session import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="app/v1/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print(f"Received token: {token}")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"Decoded payload: {payload}")
        login: str = payload.get("sub")
        if login is None:
            print("Token payload does not contain 'sub'")
            raise credentials_exception
        print(f"Extracted login: {login}")
    except JWTError as e:
        print(f"JWT decode error: {str(e)}")
        raise credentials_exception
    
    stmt = select(Client).where(Client.login == login)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        print(f"User with login {login} not found in database")
        raise credentials_exception
    print(f"Found user: {user.client_id}")
    return user
