from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

from app.db.models.base import Base
from app.db.models.association_tables import client_psychologist

from app.db.enums.sex_enum import SexEnum


class Psychologist(Base):
    __tablename__ = "psychologists"

    psychologist_id = Column(Integer, primary_key=True)
    login = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birthAt = Column(DateTime, nullable=False)
    sex = Column(PgEnum(SexEnum, name="sex", create_type=False), nullable=False)
    psychologist_photo = Column(String, nullable=True)

    clients = relationship(
        "Client",
        secondary=client_psychologist,
        back_populates="psychologists"
    )

    confirmation_requests = relationship("ConfirmationRequest", back_populates="psychologist")
    psychologist_requests = relationship("PsychologistRequest", back_populates="psychologist")

    __table_args__ = (
        Index("idx_psychologists_login", "login"),
        Index("idx_psychologists_email", "email"),
    )
