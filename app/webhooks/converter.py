from .entity import WebhookEntity
from .model import Webhook
from .webhook_id import WebhookId
from ..hooks import HookId


def entity_to_model(entity: WebhookEntity) -> Webhook:
    """
    Convert WebhookEntity (SQLAlchemy model) to Webhook (domain model).
    """
    return Webhook(
        id=WebhookId(value=entity.id),
        hook_id=HookId(value=entity.hook_id),
        payload=entity.payload,
        headers=entity.headers,
        correlation_value=entity.correlation_value,
        created_at=entity.created_at,
    )


def model_to_entity(model: Webhook) -> WebhookEntity:
    """
    Convert Webhook (domain model) to WebhookEntity (SQLAlchemy model).
    """
    return WebhookEntity(
        id=model.id.value,
        hook_id=model.hook_id.value,
        payload=model.payload,
        headers=model.headers,
        correlation_value=model.correlation_value,
        created_at=model.created_at,
    )
