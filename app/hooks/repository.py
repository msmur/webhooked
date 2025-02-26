from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List
from app.hooks.converter import model_to_entity, entity_to_model
from app.hooks.entity import HookEntity
from app.hooks.model import Hook


def insert_hook(db: Session, hook: Hook) -> Hook:
    entity = model_to_entity(hook)

    db.add(entity)
    db.commit()
    db.refresh(entity)

    return entity_to_model(entity)


# Helper function to check if the hook exists in the database
def get_hook_or_throw(hook_id: str, db: Session) -> Hook:
    hook: HookEntity | None = (
        db.query(HookEntity).where(HookEntity.id == hook_id).first()
    )

    if not hook:
        raise HTTPException(status_code=404, detail="Hook not found")
    return entity_to_model(hook)


def get_all_hooks(db: Session) -> List[Hook]:
    hooks: List[HookEntity] = (
        db.query(HookEntity).order_by(HookEntity.created_at.desc()).all()
    )
    return [entity_to_model(hook) for hook in hooks]
