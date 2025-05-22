from sqlalchemy import Column, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import relationship

from app.db.models.base import Base

from app.db.enums.request_status_enum import RequestStatusEnum


class PsychologistRequest(Base):
    __tablename__ = "psychologist_requests"

    request_id = Column(Integer, primary_key=True)
    psychologist_id = Column(Integer, ForeignKey("psychologists.client_id", ondelete="CASCADE"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)
    status = Column(PgEnum(RequestStatusEnum, name="request_status", create_type=False), nullable=False)

    psychologist = relationship("Psychologist", back_populates="psychologist_requests")
    client = relationship("Client", back_populates="psychologist_requests")

    __table_args__ = (
        Index("idx_psychologist_requests_client_id", "client_id"),
        Index("idx_psychologist_requests_psychologist_id", "psychologist_id"),
    )
