from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from app.db.enums import EmotionsEnum


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Title of the note")
    body: str | None = Field(None, max_length=2000, description="Body of the note")


class NoteResponse(BaseModel):
    note_id: int = Field(..., description="ID of the note")
    title: str = Field(..., description="Title of the note")
    body: str | None = Field(None, description="Body of the note")
    emotions: list[str] | None = Field(None, description="List of emotions associated with the note")
    createdAt: datetime = Field(..., description="Creation date of the note")

    class Config:
        from_attributes = True


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="Title of the note")
    body: Optional[str] = Field(None, max_length=1000, description="Body of the note")
    emotions: Optional[List[EmotionsEnum]] = Field(None, description="List of emotions (max 3)", max_items=3)

    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    note_id: int = Field(..., description="ID of the note")
    title: str = Field(..., description="Title of the note")
    createdAt: datetime = Field(..., description="Creation date of the note")
    emotions: Optional[List[EmotionsEnum]] = Field(None, description="List of emotions (max 3)")

    class Config:
        from_attributes = True


class NotesResponse(BaseModel):
    notes: List[NoteListResponse]
    total: int = Field(..., description="Total number of notes")


class NoteAnalysisResponse(BaseModel):
    note_id: int = Field(..., description="ID of the analyzed note")
    emotions: List[EmotionsEnum] = Field(..., description="Top 3 predicted emotions", max_items=3)

    class Config:
        from_attributes = True
