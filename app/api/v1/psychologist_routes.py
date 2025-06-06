from fastapi import APIRouter, Depends, Query, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Psychologist
from app.services.psychologist_service import (
    get_psychologist_document, revert_to_client,
    get_psychologist_clients, get_client_notes_for_psychologist,
    search_client_by_login, create_psychologist_request, 
    remove_client_from_psychologist
)
from app.schemas.psychologist import (
    DocumentResponse, PaginatedResponse, 
    ClientBase, NoteResponse, PsychologistRequestResponse
)
from app.dependencies import get_current_user, get_db


router = APIRouter(tags=["Psychologist"])


@router.get("/psychologist/document", response_model=DocumentResponse)
async def get_document(
    db: AsyncSession = Depends(get_db),
    psychologist: Psychologist = Depends(get_current_user)
):
    """Get the psychologist's document."""
    if type(psychologist) is not Psychologist:
        raise HTTPException(status_code=403, detail="Access forbidden: not a psychologist")
    return await get_psychologist_document(psychologist.client_id, db)


@router.patch("/psychologist/revert-to-client", response_model=dict)
async def revert_to_client_endpoint(
    db: AsyncSession = Depends(get_db), 
    psychologist: Psychologist = Depends(get_current_user)
):
    """Revert psychologist status back to client."""
    if type(psychologist) is not Psychologist:
        raise HTTPException(status_code=403, detail="Access forbidden: not a psychologist")
    return await revert_to_client(psychologist.client_id, db)


@router.get("/psychologist/clients", response_model=PaginatedResponse[ClientBase])
async def get_clients(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    psychologist: Psychologist = Depends(get_current_user)
):
    """Get list of clients for the psychologist."""
    if type(psychologist) is not Psychologist:
        raise HTTPException(status_code=403, detail="Access forbidden: not a psychologist")
    return await get_psychologist_clients(psychologist.client_id, db, page, size)


@router.get("/psychologist/clients/{client_id}/notes", response_model=PaginatedResponse[NoteResponse])
async def get_client_notes(
    client_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    psychologist: Psychologist = Depends(get_current_user)
):
    """Get notes of a specific client for the psychologist."""
    if type(psychologist) is not Psychologist:
        raise HTTPException(status_code=403, detail="Access forbidden: not a psychologist")
    return await get_client_notes_for_psychologist(psychologist.client_id, client_id, db, page, size)


@router.get("/psychologist/search-client", response_model=ClientBase)
async def search_client(
    login: str = Query(..., description="Exact login to search for"),
    db: AsyncSession = Depends(get_db),
    psychologist: Psychologist = Depends(get_current_user)
):
    """Search for a client by exact login (case-sensitive)."""
    if type(psychologist) is not Psychologist:
        raise HTTPException(status_code=403, detail="Access forbidden: not a psychologist")
    return await search_client_by_login(login, db)

@router.post("/psychologist/request-client/{client_id}", response_model=PsychologistRequestResponse)
async def create_request(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    psychologist: Psychologist = Depends(get_current_user)
):
    """Create a request to connect with a client."""
    if type(psychologist) is not Psychologist:
        raise HTTPException(status_code=403, detail="Access forbidden: not a psychologist")
    return await create_psychologist_request(psychologist.client_id, client_id, db)


@router.delete("/psychologist/client/{client_id}", response_model=dict)
async def remove_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    psychologist: Psychologist = Depends(get_current_user)
):
    "Remove a client from the psychologist's client list"
    if type(psychologist) is not Psychologist:
        raise HTTPException(status_code=403, detail="Access forbidden: not a psychologist")
    return await remove_client_from_psychologist(psychologist.client_id, client_id, db)
