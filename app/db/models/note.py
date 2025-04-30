from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

from app.db.models.base import Base

from app.db.enums.emotions_enum import EmotionsEnum


class Note(Base):
    __tablename__ = "notes"

    note_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    body = Column(String, nullable=True)
    createdAt = Column(DateTime, nullable=False)
    updatedAt = Column(DateTime, nullable=False)
    emotions = Column(PgEnum(EmotionsEnum, name="emotions", create_type=False), nullable=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)

    client = relationship("Client", back_populates="notes")
