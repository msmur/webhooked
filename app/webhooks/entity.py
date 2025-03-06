from datetime import datetime, UTC
from sqlalchemy import Column, String, JSON, DateTime

from ..database import Base


class WebhookEntity(Base):
    __tablename__ = "webhooks"

    id: str = Column(String, primary_key=True)

    hook_id = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    headers = Column(JSON, nullable=False)

    correlation_value = Column(String, nullable=True, index=True)

    created_at: datetime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )
