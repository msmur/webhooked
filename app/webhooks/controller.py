from fastapi import APIRouter, Depends, Request, Body, Path, Query
from sqlalchemy.orm import Session
from app.database import get_db

from .model import Webhook, WebhookListResponse, WebhookResponse
from .repository import insert_webhook, get_by_hook_id, get_by_correlation_value
from .webhook_id import WebhookId
from ..hooks import HookId
from ..hooks.repository import get_hook_or_throw

router = APIRouter(prefix="/hooks/{hook_id}/webhooks", tags=["Webhooks"])


@router.post(
    "",
    summary="",
    description="",
    response_model=WebhookResponse,
)
async def receive_webhook(
    request: Request,
    hook_id: str = Path(..., title="The Hook ID"),
    db: Session = Depends(get_db),
) -> WebhookResponse:
    """Receives a webhook and stores it in the database"""
    hook = get_hook_or_throw(hook_id, db)

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    headers = dict(request.headers)

    correlation_value = None

    if hook.correlation_identifier_location:
        correlation_location = hook.correlation_identifier_location
        correlation_field = hook.correlation_identifier_field
        # Extract correlation identifier based on the location
        if correlation_location == "headers":
            # Get value from headers
            correlation_value = headers.get(correlation_field, None)
        elif correlation_location == "payload":
            # Get value from payload
            correlation_value = payload.get(correlation_field, None)
        else:
            correlation_value = None

    webhook_data = Webhook(
        id=WebhookId.generate(),
        hook_id=HookId(value=hook_id),
        payload=payload,
        headers=headers,
        correlation_value=None if correlation_value is None else str(correlation_value),
    )

    saved_webhook = insert_webhook(db, webhook_data)

    return WebhookResponse(
        id=saved_webhook.id,
        hook_id=saved_webhook.hook_id,
        correlation_value=saved_webhook.correlation_value,
        created_at=saved_webhook.created_at,
    )


@router.get("", summary="", description="", response_model=WebhookListResponse)
def get_webhooks(
    hook_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    search: str = Query(None, min_length=1),
    db: Session = Depends(get_db),
) -> WebhookListResponse:
    """Fetch paginated webhooks for a given hook"""
    return get_by_hook_id(hook_id, page, limit, search, db)


@router.get(
    "/{correlation_value}",
    summary="",
    description="",
    response_model=list[Webhook],
)
def get_webhooks_by_correlation_value(
    hook_id: str,
    correlation_value: str,
    db: Session = Depends(get_db),
) -> list[Webhook]:
    """Fetch paginated webhook by a correlation value"""
    return get_by_correlation_value(hook_id, correlation_value, db)
