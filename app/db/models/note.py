from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

from app.db.models.base import Base

from app.db.enums.emotions_enum import EmotionsEnum


class Note(Base):
    __tablename__ = "notes"

    note_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    body = Column(String, nullable=True)
    createdAt = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updatedAt = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    emotions = Column(ARRAY(PgEnum(EmotionsEnum, name="emotions", create_type=False)), nullable=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)

    client = relationship("Client", back_populates="notes")
