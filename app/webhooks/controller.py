from fastapi import (
    APIRouter,
    Depends,
    Request,
    Path,
    Query,
    WebSocket,
    WebSocketDisconnect,
    BackgroundTasks,
)
from jsonpath_ng.exceptions import JsonPathParserError
from sqlalchemy.orm import Session
from jsonpath_ng import parse
from typing import Dict, Set
from loguru import logger

from app.database import get_db
from .model import Webhook, WebhookListResponse, WebhookedSavedResponse
from .repository import (
    insert_webhook,
    get_by_hook_id,
    get_by_correlation_value,
    get_latest_for_hook,
)
from .webhook_id import WebhookId
from ..hooks import HookId
from ..hooks.repository import get_hook_or_throw

router = APIRouter(prefix="/hooks/{hook_id}/webhooks", tags=["Webhooks"])

# Dictionary to track active WebSocket connections per hook ID
active_connections: Dict[str, Set[WebSocket]] = {}


@router.websocket("/events")
async def websocket_endpoint(websocket: WebSocket, hook_id: str):
    await websocket.accept()

    if hook_id not in active_connections:
        active_connections[hook_id] = set()
    active_connections[hook_id].add(websocket)

    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive (optional)
    except WebSocketDisconnect:
        active_connections[hook_id].remove(websocket)
        if not active_connections[hook_id]:
            del active_connections[hook_id]  # Cleanup empty sets


async def notify_websocket_clients(hook_id: str, event_type: str):
    if hook_id in active_connections:
        for websocket in list(
            active_connections[hook_id]
        ):  # Convert to list to avoid mutation issues
            try:
                await websocket.send_json({"event_type": event_type})
            except WebSocketDisconnect:
                active_connections[hook_id].remove(websocket)


@router.post(
    "",
    summary="",
    description="",
    response_model=WebhookedSavedResponse,
)
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    hook_id: str = Path(..., title="The Hook ID"),
    db: Session = Depends(get_db),
) -> WebhookedSavedResponse:
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
            try:
                jsonpath_expr = parse(correlation_field)
                matches = [match.value for match in jsonpath_expr.find(payload)]
                correlation_value = (
                    matches[0] if matches else None
                )  # Take first match or None
            except JsonPathParserError:
                correlation_value = None  # Handle invalid JSONPath cases gracefully
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

    # asyncio.create_task(notify_clients(hook_id))
    background_tasks.add_task(notify_websocket_clients, hook_id, "new_webhook")

    return WebhookedSavedResponse(
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
    correlation_value: str = Query(None, min_length=1, alias="search"),
    db: Session = Depends(get_db),
) -> WebhookListResponse:
    """Fetch paginated webhooks for a given hook"""
    return get_by_hook_id(hook_id, page, limit, correlation_value, db)


@router.get("/latest", summary="", description="", response_model=Webhook)
def get_latest_webhook(hook_id: str, db: Session = Depends(get_db)) -> Webhook:
    return get_latest_for_hook(hook_id, db)
