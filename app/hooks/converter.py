from .hook_id import HookId
from .model import Hook
from .entity import HookEntity


def entity_to_model(hook_entity: HookEntity) -> Hook:
    """
    Convert HookEntity (SQLAlchemy model) to Hook domain model.
    """
    return Hook(
        id=HookId(value=hook_entity.id),
        name=hook_entity.name,
        description=hook_entity.description,
        status=hook_entity.status,
        expires_at=hook_entity.expires_at,
        created_at=hook_entity.created_at,
        updated_at=hook_entity.updated_at,
        correlation_identifier_field=hook_entity.correlation_identifier_field,
        correlation_identifier_location=hook_entity.correlation_identifier_location,
    )


def model_to_entity(hook: Hook) -> HookEntity:
    """
    Convert Hook domain model to HookEntity (SQLAlchemy model).
    """
    return HookEntity(
        id=hook.id.value,
        name=hook.name,
        description=hook.description,
        status=hook.status,
        expires_at=hook.expires_at,
        created_at=hook.created_at,
        updated_at=hook.updated_at,
        correlation_identifier_field=hook.correlation_identifier_field,
        correlation_identifier_location=hook.correlation_identifier_location,
    )
