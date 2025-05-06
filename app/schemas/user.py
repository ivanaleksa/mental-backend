from typing import Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.db.enums import SexEnum, UserTypeEnum


class UserSchema(BaseModel):
    user_id: int
    login: str
    email: EmailStr
    first_name: str
    last_name: str
    birthAt: str  # ISO format date yyyy-mm-dd
    sex: SexEnum
    client_photo: str | None
    is_verified: bool
    user_type: UserTypeEnum

    class Config:
        use_enum_values = True


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
    is_verified: bool
    sex: SexEnum
    user_type: UserTypeEnum
    client_photo: str | None
    jwt_token: str


class UserLogin(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    user_type: UserTypeEnum = UserTypeEnum.CLIENT
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdatePassword(BaseModel):
    user_id: int
    user_type: UserTypeEnum = UserTypeEnum.CLIENT
    old_password: str = Field(..., min_length=8, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=100)


class UserResetPass(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    user_type: UserTypeEnum


class UserResetPassConfirm(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    user_type: UserTypeEnum
    code: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    birthAt: Optional[str] = None  # ISO (yyyy-mm-dd)

    class Config:
        from_attributes = True

    @staticmethod
    def validate_birth_at(value: Optional[str]) -> Optional[datetime]:
        if value is None:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Invalid birthAt format. Use ISO format (yyyy-mm-dd)")

    @classmethod
    def validate(cls, values):
        if "birthAt" in values:
            values["birthAt"] = cls.validate_birth_at(values["birthAt"])
        return values


class PsychologistInfoResponse(BaseModel):
    request_id: int
    login: str
    first_name: str
    last_name: str
    sex: str
    psychologist_photo: Optional[str] = None

    class Config:
        from_attributes = True
