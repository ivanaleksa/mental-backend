from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Note
from app.schemas.note import NoteCreate
from app.db.enums import EmotionsEnum


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

    return {
        "message": "Note created successfully",
        "note_id": note.note_id,
        "title": note.title,
        "body": note.body,
        "createdAt": note.createdAt
    }
