from datetime import date

from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.hooks.hook_id import HookId
from app.hooks.repository import insert_hook
from app.hooks.model import Hook, HookCreate
from fastapi import APIRouter, HTTPException, Body

# Initialize router with a prefix
router = APIRouter(prefix="/hooks", tags=["Hooks"])


# Route for creating a hook
@router.post(
    "",
    summary="Create a Webhook",
    description="Create a new webhook with the given details.",
    response_model=Hook,
)
async def create_hook(
    hook: HookCreate = Body(..., title="Hook Creation Params"),
    db: Session = Depends(get_db),
) -> Hook:
    """
    Endpoint to create a new webhook.

    - **name**: The name of the webhook.
    - **description**: A description of the webhook.
    - **expiry**: The expiration date (optional).
    """
    # Simulate saving the webhook
    if hook.expires_at and hook.expires_at < date.today():
        raise HTTPException(
            status_code=400, detail="Expiry date cannot be in the past."
        )

        # try:
    hook_model = Hook(
        **hook.model_dump(), id=HookId.generate()
    )  # This creates the domain object (with validation)
    # except ValueError as e:
    #     raise HTTPException(status_code=400, detail=str(e))

    return insert_hook(db, hook_model)
