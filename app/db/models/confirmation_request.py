from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import relationship

from app.db.models.base import Base

from app.db.enums.email_confirmation_type_enum import EmailConfirmationTypeEnum


class ConfirmationRequest(Base):
    __tablename__ = "confirmation_requests"

    confirmation_id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=True)
    psychologist_id = Column(Integer, ForeignKey("psychologists.psychologist_id", ondelete="CASCADE"), nullable=True)
    code = Column(String, nullable=False)
    email = Column(String, nullable=False)
    createdAt = Column(DateTime(timezone=True), nullable=False)
    confirmedAt = Column(DateTime(timezone=True), nullable=True)
    type = Column(PgEnum(EmailConfirmationTypeEnum, name="confirmation_type", create_type=False), nullable=False)

    client = relationship("Client", back_populates="confirmation_requests")
    psychologist = relationship("Psychologist", back_populates="confirmation_requests")

    __table_args__ = (
        Index("idx_confirmation_requests_client_id", "client_id"),
        Index("idx_confirmation_requests_psychologist_id", "psychologist_id"),
    )
