from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

from app.db.models.base import Base
from app.db.models.association_tables import client_psychologist

from app.db.enums.sex_enum import SexEnum


class Client(Base):
    __tablename__ = "clients"

    client_id = Column(Integer, primary_key=True)
    login = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birthAt = Column(DateTime, nullable=False)
    sex = Column(PgEnum(SexEnum, name="sex", create_type=False), nullable=False)
    client_photo = Column(String, nullable=True)

    psychologists = relationship(
        "Psychologist",
        secondary=client_psychologist,
        back_populates="clients"
    )

    notes = relationship("Note", back_populates="client")
    confirmation_requests = relationship("ConfirmationRequest", back_populates="client")
    psychologist_requests = relationship("PsychologistRequest", back_populates="client")
    client_requests = relationship("ClientRequest", back_populates="client")
