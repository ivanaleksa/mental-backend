from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.note_service import create_note
from app.schemas.note import NoteCreate, NoteResponse
from app.dependencies import get_current_user, get_db
from app.db.models import Client


router = APIRouter(tags=["Note"])

@router.post("/note/create", response_model=NoteResponse)
async def create_new_note(
    note_data: NoteCreate,
    current_user: Client = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new note for the authenticated client.
    """
    return await create_note(current_user.client_id, note_data, db)
