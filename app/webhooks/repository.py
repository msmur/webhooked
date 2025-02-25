from sqlalchemy.orm import Session

from .converter import model_to_entity, entity_to_model
from .entity import WebhookEntity
from .model import Webhook, WebhookListResponse


def insert_webhook(db: Session, webhook: Webhook) -> Webhook:
    entity = model_to_entity(webhook)

    db.add(entity)
    db.commit()
    db.refresh(entity)

    return entity_to_model(entity)


def get_by_hook_id(
    hook_id: str, page: int, limit: int, search: str | None, db: Session
) -> WebhookListResponse:
    query = db.query(WebhookEntity).filter(WebhookEntity.hook_id == hook_id)

    if search:
        query = query.filter(WebhookEntity.correlation_value.icontains(search))

    total_count = query.count()

    webhooks = (
        query.order_by(WebhookEntity.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit + 1)
        .all()
    )

    has_more = len(webhooks) > limit
    webhooks = webhooks[:limit]

    return WebhookListResponse(
        data=[entity_to_model(webhook) for webhook in webhooks],
        count=total_count,
        has_more=has_more,
    )


def get_latest_for_hook(hook_id: str, db: Session) -> Webhook | None:
    webhook: WebhookEntity | None = (
        db.query(WebhookEntity)
        .filter(WebhookEntity.hook_id == hook_id)
        .order_by(WebhookEntity.created_at.desc())
        .first()
    )
    return entity_to_model(webhook) if webhook else None


def get_by_correlation_value(
    hook_id: str, correlation_value: str, db: Session
) -> list[Webhook]:
    webhooks: list[WebhookEntity] = (
        db.query(WebhookEntity)
        .filter(WebhookEntity.hook_id == hook_id)
        .filter(WebhookEntity.correlation_value == correlation_value)
        .all()
    )
    return [entity_to_model(webhook) for webhook in webhooks]
