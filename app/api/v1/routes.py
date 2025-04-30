from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserResponse
from app.db.session import get_db
from app.services.user_service import register_user_service


router = APIRouter()


@router.get("/healthcheck")
async def hello_world():
    return {"message": "Hello, world!"}


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await register_user_service(user_data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
