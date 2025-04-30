from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import relationship

from app.db.models.base import Base

from app.db.enums.email_confirmation_type_enum import EmailConfirmationTypeEnum


class ConfirmationRequest(Base):
    __tablename__ = "confirmation_requests"

    confirmation_id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=True)
    psychologist_id = Column(Integer, ForeignKey("psychologists.psychologist_id"), nullable=True)
    code = Column(String, nullable=False)
    email = Column(String, nullable=False)
    createdAt = Column(DateTime, nullable=False)
    confirmedAt = Column(DateTime, nullable=True)
    type = Column(PgEnum(EmailConfirmationTypeEnum, name="confirmation_type", create_type=False), nullable=False)

    client = relationship("Client", back_populates="confirmation_requests")
    psychologist = relationship("Psychologist", back_populates="confirmation_requests")
