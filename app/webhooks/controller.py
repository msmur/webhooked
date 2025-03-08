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
import asyncio
from typing import Dict, Set
from loguru import logger

from app.database import get_db
from .model import Webhook, WebhookListResponse, WebhookResponse
from .repository import insert_webhook, get_by_hook_id, get_by_correlation_value
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


# connected_clients: Dict[str, Dict[str, asyncio.Queue]] = {}
#
#
# async def event_generator(queue: asyncio.Queue, hook_id: str, client_id: str):
#     try:
#         while True:
#             await queue.get()  # Wait for new webhook data
#             yield f"Received new webhooks!"
#     except asyncio.CancelledError:
#         logger.warning("Client disconnected, stopping event stream.")
#     except Exception as e:
#         logger.error(f"Unhandled exception in event generator: {e}")
#     finally:
#         # Remove the client from the connected clients list
#         logger.info(f"Removing client {client_id} from hook {hook_id}")
#         if hook_id in connected_clients:
#             if client_id in connected_clients[hook_id]:
#                 del connected_clients[hook_id][client_id]
#
#
# @router.get("/{client_id}/events")
# async def sse(
#     hook_id: str = Path(...),
#     client_id: str = Path(...),
# ):
#     """Endpoint for clients to listen for new webhook events."""
#     queue = asyncio.Queue()
#
#     # Store client in the dictionary
#     if hook_id not in connected_clients:
#         connected_clients[hook_id] = {}
#     connected_clients[hook_id][client_id] = queue
#
#     return EventSourceResponse(
#         event_generator(queue, hook_id, client_id),
#         headers={
#             "x-accel-buffering": "no",
#             "content-type": "text/event-stream",
#             "cache-control": "no-cache",
#             "Connection": "keep-alive",
#         },
#     )
#
#
# async def notify_clients(hook_id: str, event_data: str = "New webhook received!"):
#     """Send events only to clients subscribed to the specific hook ID."""
#     if hook_id in connected_clients:
#         logger.info(
#             f"Notifying clients for hook {hook_id}: {list(connected_clients[hook_id].keys())}"
#         )
#         # Iterate through all clients subscribed to this hook_id
#         for client_id, queue in connected_clients[hook_id].items():
#             try:
#                 await queue.put(event_data)  # Send event to the client's queue
#             except Exception as e:
#                 logger.error(f"Error notifying client {client_id}: {e}")


@router.post(
    "",
    summary="",
    description="",
    response_model=WebhookResponse,
)
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
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
