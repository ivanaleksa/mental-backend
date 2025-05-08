from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.note_service import (
    create_note, delete_note, 
    update_note, get_client_notes_service, 
    get_note_by_id_service, analyze_note
)
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate, NotesResponse, NoteAnalysisResponse
from app.dependencies import get_current_user, get_db
from app.db.models import Client
from app.ml_service import ThreadSafeModelHandler


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


@router.get("/notes/get", response_model=NotesResponse)
async def get_client_notes(
    current_user: Client = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    sort_by: str = "createdAt",
    sort_order: str = "desc",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None
):
    """
    Get all notes for the authenticated client with sorting, filtering, and search.
    - sort_by: 'createdAt' or 'title'
    - sort_order: 'asc' or 'desc'
    - start_date: Filter notes created after this date (ISO format)
    - end_date: Filter notes created before this date (ISO format)
    - search: Search term in title
    """
    return await get_client_notes_service(
        current_user.client_id, db, sort_by, sort_order, start_date, end_date, search
    )


@router.get("/note/{note_id}", response_model=NoteResponse)
async def get_note_by_id(
    note_id: int,
    current_user: Client = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific note by its ID for the authenticated client.
    """
    return await get_note_by_id_service(note_id, current_user.client_id, db)


@router.get("/note/{note_id}/analyze", response_model=NoteAnalysisResponse)
async def analyze_note_by_id(
    note_id: int,
    current_user: Client = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    model_handler: ThreadSafeModelHandler = Depends()
):
    """
    Analyze a specific note by its ID and return the top 3 predicted emotions.
    """
    return await analyze_note(note_id, current_user.client_id, db, model_handler)
