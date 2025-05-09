from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import relationship

from app.db.models.base import Base

from app.db.enums.request_status_enum import RequestStatusEnum


class PsychologistRequest(Base):
    __tablename__ = "psychologist_requests"

    request_id = Column(Integer, primary_key=True)
    psychologist_id = Column(Integer, ForeignKey("psychologists.psychologist_id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    status = Column(PgEnum(RequestStatusEnum, name="request_status", create_type=False), nullable=False)

    psychologist = relationship("Psychologist", back_populates="psychologist_requests")
    client = relationship("Client", back_populates="psychologist_requests")
