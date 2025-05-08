from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Note
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate


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
        emotions=[emotion.value for emotion in note.emotions] if note.emotions else None
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
        emotions=[emotion.value for emotion in note.emotions] if note.emotions else None,
        createdAt=note.createdAt
    )
