from pydantic import BaseModel, Field
from datetime import datetime


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Title of the note")
    body: str | None = Field(None, max_length=2000, description="Body of the note")


class NoteResponse(BaseModel):
    note_id: int = Field(..., description="ID of the note")
    title: str = Field(..., description="Title of the note")
    body: str | None = Field(None, description="Body of the note")
    createdAt: datetime = Field(..., description="Creation date of the note")

    class Config:
        from_attributes = True
