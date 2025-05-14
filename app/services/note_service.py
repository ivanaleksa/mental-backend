from datetime import datetime, timezone
from typing import Optional
import asyncio

from fastapi import HTTPException, Depends

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Note
from app.schemas.note import (
    NoteCreate, NoteResponse, NoteAnalysisResponse,
    NoteUpdate, NotesResponse, NoteListResponse
)
from app.ml_service import ThreadSafeModelHandler

async def create_note(
    client_id: int,
    note_data: NoteCreate,
    db: AsyncSession
) -> dict:
    """
    Create a new note for the client.
    """
    note = Note(
        title=note_data.title,
        body=note_data.body,
        client_id=client_id
    )

    db.add(note)
    await db.commit()
    await db.refresh(note)

    response = NoteResponse(
        note_id=note.note_id,
        title=note.title,
        body=note.body,
        createdAt=note.createdAt,
        emotions=note.emotions if note.emotions else []
    )

    return response


async def delete_note(
    note_id: int,
    client_id: int,
    db: AsyncSession
) -> dict:
    """
    Delete a note by its ID if it belongs to the client.
    """
    stmt = select(Note).where(Note.note_id == note_id)
    result = await db.execute(stmt)
    note = result.scalar_one_or_none()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.client_id != client_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this note")

    await db.delete(note)
    await db.commit()

    return {"message": "Note deleted successfully"}


async def update_note(
    note_id: int,
    client_id: int,
    update_data: NoteUpdate,
    db: AsyncSession
) -> NoteResponse:
    """
    Update a note by its ID if it belongs to the client.
    """
    stmt = select(Note).where(Note.note_id == note_id)
    result = await db.execute(stmt)
    note = result.scalar_one_or_none()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.client_id != client_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this note")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(note, key, value)

    await db.commit()
    await db.refresh(note)

    return NoteResponse(
        note_id=note.note_id,
        title=note.title,
        body=note.body,
        emotions=note.emotions if note.emotions else [],
        createdAt=note.createdAt
    )


async def get_client_notes_service(
    client_id: int,
    db: AsyncSession,
    sort_by: str = "createdAt",
    sort_order: str = "desc",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None
) -> NotesResponse:
    """
    Get all notes for a client with sorting, filtering, and search.
    """
    stmt = select(Note).where(Note.client_id == client_id)

    if start_date and end_date:
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)
        stmt = stmt.where(Note.createdAt.between(start_date, end_date))
    elif start_date:
        stmt = stmt.where(Note.createdAt >= start_date)
    elif end_date:
        stmt = stmt.where(Note.createdAt <= end_date)

    if search:
        search_pattern = f"%{search}%"
        stmt = stmt.where(Note.title.ilike(search_pattern))

    valid_sort_by = {"createdAt", "title"}
    if sort_by not in valid_sort_by:
        sort_by = "createdAt"
    valid_sort_order = {"asc", "desc"}
    if sort_order not in valid_sort_order:
        sort_order = "desc"

    stmt = stmt.order_by(getattr(Note, sort_by).asc() if sort_order == "asc" else getattr(Note, sort_by).desc())

    result = await db.execute(stmt)
    notes = result.scalars().all()

    response_notes = [
        NoteListResponse(
            note_id=note.note_id,
            title=note.title,
            createdAt=note.createdAt,
            emotions=note.emotions if note.emotions else []
        )
        for note in notes
    ]

    return NotesResponse(notes=response_notes, total=len(response_notes))


async def get_note_by_id_service(
    note_id: int,
    client_id: int,
    db: AsyncSession
) -> NoteResponse:
    """
    Get a specific note by its ID if it belongs to the client.
    """
    stmt = select(Note).where(Note.note_id == note_id)
    result = await db.execute(stmt)
    note = result.scalar_one_or_none()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.client_id != client_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this note")

    return NoteResponse(
        note_id=note.note_id,
        title=note.title,
        body=note.body,
        createdAt=note.createdAt,
        emotions=note.emotions if note.emotions else []
    )


async def analyze_note(
    note_id: int,
    client_id: int,
    db: AsyncSession,
    model_handler: ThreadSafeModelHandler = Depends()
) -> NoteAnalysisResponse:
    """
    Analyze a note by its ID using RoBertaModel and return the top 3 emotions.
    """
    stmt = select(Note).where(Note.note_id == note_id)
    result = await db.execute(stmt)
    note = result.scalar_one_or_none()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.client_id != client_id:
        raise HTTPException(status_code=403, detail="Not authorized to analyze this note")

    if not note.body or not note.body.strip():
        raise HTTPException(status_code=400, detail="Note body is empty or invalid")

    try:
        predicted_emotions = await asyncio.to_thread(model_handler.predict, note.body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    return NoteAnalysisResponse(
        note_id=note.note_id,
        emotions=predicted_emotions
    )
