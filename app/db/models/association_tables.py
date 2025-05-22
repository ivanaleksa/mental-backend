from sqlalchemy import Table, Column, Integer, ForeignKey, Index
from app.db.models.base import Base

# Secondary table for the many-to-many relationship between clients and psychologists
client_psychologist = Table(
    "client_psychologist",
    Base.metadata,
    Column("relation_id", Integer, primary_key=True),
    Column("client_id", Integer, ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False),
    Column("psychologist_id", Integer, ForeignKey("psychologists.client_id", ondelete="CASCADE"), nullable=False),
    Index("idx_client_psychologist_client_id", "client_id"),
    Index("idx_client_psychologist_psychologist_id", "psychologist_id")
)
