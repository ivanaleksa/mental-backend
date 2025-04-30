from sqlalchemy import Table, Column, Integer, ForeignKey
from app.db.models.base import Base


# Secondary table for the many-to-many relationship between clients and psychologists
client_psychologist = Table(
    "client_psychologist",
    Base.metadata,
    Column("relation_id", Integer, primary_key=True),
    Column("client_id", Integer, ForeignKey("clients.client_id"), nullable=False),
    Column("psychologist_id", Integer, ForeignKey("psychologists.psychologist_id"), nullable=False),
)
