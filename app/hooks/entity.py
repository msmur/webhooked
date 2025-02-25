from datetime import date, datetime

from sqlalchemy import Column, String, Date, DateTime, Enum
from ..database import Base


class HookEntity(Base):
    __tablename__ = "hooks"

    id: str = Column(String, primary_key=True)

    name: str = Column(String)
    description: str = Column(String)
    status: str = Column(String)
    expires_at: date | None = Column(Date, nullable=True)

    correlation_identifier_location = Column(
        Enum("headers", "payload", name="correlation_location_enum"), nullable=True
    )
    correlation_identifier_field = Column(String, nullable=True)

    created_at: datetime = Column(DateTime, default=datetime.now(), nullable=False)
    updated_at: datetime = Column(DateTime, default=datetime.now(), nullable=False)
