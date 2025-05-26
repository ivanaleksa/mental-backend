from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, TypeVar, Generic
from app.db.enums import SexEnum


class DocumentResponse(BaseModel):
    document_path: str


class ClientBase(BaseModel):
    client_id: int
    login: str
    email: str
    first_name: str
    last_name: str
    birthAt: datetime
    sex: SexEnum
    client_photo: Optional[str] = None


class NoteResponse(BaseModel):
    note_id: int
    title: str
    body: Optional[str] = None
    createdAt: datetime
    emotions: Optional[List[str]] = None


T = TypeVar("T")
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")

    class Config:
        from_attributes = True
