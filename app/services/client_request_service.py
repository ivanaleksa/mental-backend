import os
import uuid

from fastapi import HTTPException, UploadFile

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import ClientRequest, Client, Psychologist
from app.schemas.client_request import ClientRequestUpdate
from app.db.enums import RequestStatusEnum
from app.core import settings, send_client_request_notification


async def create_psychologist_application(
    client_id: int,
    document: UploadFile,
    db: AsyncSession
) -> dict:
    """
    Create a psychologist application for a client.
    """
    stmt = select(ClientRequest).where(
        ClientRequest.client_id == client_id,
        ClientRequest.status == ClientRequest.PENDING
    )
    result = await db.execute(stmt)
    existing_application = result.scalar_one_or_none()

    if existing_application:
        raise HTTPException(status_code=400, detail="You already have a pending application")

    file_extension = os.path.splitext(document.filename.lower())[1]
    if file_extension not in settings.ALLOWED_REQUEST_EXTENTIONS:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use .pdf")

    unique_filename = f"{uuid.uuid4()}_{client_id}{file_extension}"
    file_path = os.path.join(settings.DOCUMENTS_DIRECTORY, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await document.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save document: {str(e)}")

    application = ClientRequest(
        client_id=client_id,
        document=file_path,
        status=RequestStatusEnum.PENDING
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)

    return {
        "message": "Application submitted successfully",
        "application_id": application.request_id,
        "status": application.status
    }


async def get_client_request_status(client_id: int, db: AsyncSession) -> dict:
    """
    Get the status of the client's psychologist application.
    """
    stmt = select(ClientRequest).where(
        ClientRequest.client_id == client_id
    ).order_by(ClientRequest.created_at.desc())
    result = await db.execute(stmt)
    application = result.scalar_one_or_none()

    if not application:
        return {
            "has_application": False,
            "status": None,
            "rejection_reason": None
        }

    return {
        "has_application": True,
        "status": application.status,
        "rejection_reason": application.rejection_reason
    }


async def update_client_request(request_id: int, update_data: ClientRequestUpdate, db: AsyncSession) -> dict:
    """
    Update the status of a psychologist application (admin only).
    """
    stmt = select(ClientRequest).where(ClientRequest.request_id == request_id)
    result = await db.execute(stmt)
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if application.status != RequestStatusEnum.PENDING:
        raise HTTPException(status_code=400, detail="Application is already processed")

    application.status = update_data.status
    if update_data.status == RequestStatusEnum.REJECTED:
        if not update_data.rejection_reason:
            raise HTTPException(status_code=400, detail="Rejection reason is required")
        application.rejection_reason = update_data.rejection_reason

    if update_data.status == RequestStatusEnum.APPROVED:
        stmt = select(Client).where(Client.client_id == application.client_id)
        result = await db.execute(stmt)
        client = result.scalar_one_or_none()

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        if not client.is_verified:
            raise HTTPException(status_code=400, detail="Client is not verified")

        psychologist = Psychologist(
            login=client.login,
            password=client.password,
            email=client.email,
            first_name=client.first_name,
            last_name=client.last_name,
            birthAt=client.birthAt,
            sex=client.sex,
            psychologist_photo=client.client_photo,
            is_verified=True
        )
        db.add(psychologist)
        await db.commit()
        await db.refresh(psychologist)

        await db.delete(client)

    await db.commit()
    await db.refresh(application)

    if update_data.status == RequestStatusEnum.APPROVED:
        await send_client_request_notification(
            email=client.email,
            subject="Your Psychologist Application Has Been Approved",
            body="Congratulations! Your application to become a psychologist has been approved. You can now access your new dashboard."
        )
    elif update_data.status == RequestStatusEnum.REJECTED:
        await send_client_request_notification(
            email=client.email,
            subject="Your Psychologist Application Has Been Rejected",
            body=f"We're sorry, but your application to become a psychologist has been rejected. Reason: {update_data.rejection_reason}"
        )

    return {
        "message": "Application updated successfully",
        "status": application.status,
        "rejection_reason": application.rejection_reason
    }
