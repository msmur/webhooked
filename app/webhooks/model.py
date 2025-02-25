from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional

from .webhook_id import WebhookId
from ..hooks import HookId


class WebhookBase(BaseModel):
    hook_id: HookId
    payload: Dict[str, Any]
    headers: Dict[str, Any]
    correlation_value: Optional[str] = None


class WebhookCreate(WebhookBase):
    pass


class Webhook(WebhookBase):
    id: WebhookId
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Enables SQLAlchemy to Pydantic conversion


class WebhookListResponse(BaseModel):
    data: list[Webhook]
    count: int
    has_more: bool


class WebhookResponse(BaseModel):
    id: WebhookId
    hook_id: HookId
    correlation_value: Optional[str] = None
    created_at: Optional[datetime] = None
