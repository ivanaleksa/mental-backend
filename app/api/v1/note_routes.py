from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.note_service import create_note, delete_note, update_note
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate
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


@router.delete("/note/delete/{note_id}")
async def delete_note_by_id(
    note_id: int,
    current_user: Client = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a note by its ID for the authenticated client.
    """
    return await delete_note(note_id, current_user.client_id, db)


@router.patch("/note/update/{note_id}", response_model=NoteResponse)
async def update_note_by_id(
    note_id: int,
    update_data: NoteUpdate,
    current_user: Client = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a note by its ID for the authenticated client.
    """
    return await update_note(note_id, current_user.client_id, update_data, db)
