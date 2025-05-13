from pydantic import BaseModel, Field
from datetime import datetime
from app.db.enums import SexEnum, RequestStatusEnum
from typing import Optional, List, TypeVar, Generic


class UserBase(BaseModel):
    login: str
    email: str
    first_name: str
    last_name: str
    birthAt: datetime
    sex: SexEnum


class ClientResponse(UserBase):
    client_id: int
    client_photo: Optional[str] = None
    is_verified: bool


class PsychologistResponse(UserBase):
    psychologist_id: int
    psychologist_photo: Optional[str] = None


class AdminResponse(BaseModel):
    admin_id: int
    login: str


class AdminLoginRequest(BaseModel):
    login: str
    password: str

class AdminLoginResponse(AdminResponse):
    jwt_token: str


T = TypeVar("T")
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")

    class Config:
        from_attributes = True


class ClientRequestResponse(BaseModel):
    request_id: int
    client_id: int
    document: str
    status: RequestStatusEnum
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AdminCreate(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

    class Config:
        from_attributes = True
