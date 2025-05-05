from typing import Optional
from pydantic import BaseModel

from app.db.enums import RequestStatusEnum


class ClientRequestUpdate(BaseModel):
    status: RequestStatusEnum
    rejection_reason: Optional[str] = None

    class Config:
        from_attributes = True
