from pydantic import BaseModel, EmailStr, Field
from app.db.enums.sex_enum import SexEnum


class UserCreate(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    birthAt: str  # ISO format date yyyy-mm-dd
    sex: SexEnum

    class Config:
        use_enum_values = True


class UserResponse(BaseModel):
    user_id: int
    login: str
    email: EmailStr
    first_name: str
    last_name: str
    birthAt: str  # ISO format date yyyy-mm-dd
    jwt_token: str
