from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import relationship

from app.db.models.base import Base

from app.db.enums.request_status_enum import RequestStatusEnum


class ClientRequest(Base):
    __tablename__ = "client_requests"

    request_id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    document = Column(String, nullable=False)
    status = Column(PgEnum(RequestStatusEnum, name="request_status", create_type=False), nullable=False)
    rejection_reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    client = relationship("Client", back_populates="client_requests")
