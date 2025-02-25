from datetime import datetime
from fastapi import FastAPI, Depends, Path
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from app.database import get_db
from sqlalchemy.orm import Session

from app.hooks import router as hooks_router
from app.webhooks import router as webhooks_router
from app.hooks.repository import get_all_hooks

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")


def format_datetime(value):
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value.strftime("%Y %b %d - %-I:%M %p")  # Example: "2025 Feb 21 - 7:52 AM"


templates.env.filters["format_datetime"] = format_datetime  # Register filter


@app.get("/hooks")
async def display_hooks(request: Request, db: Session = Depends(get_db)):
    hooks = get_all_hooks(db)
    return templates.TemplateResponse(
        "hooks.html", {"request": request, "hooks": hooks}
    )


@app.get("/hooks/{hook_id}")
async def display_webhooks(
    request: Request,
    hook_id: str = Path(..., title="The Hook ID"),
):
    return templates.TemplateResponse(
        "webhooks.html",
        {"request": request, "hook_id": hook_id},
    )


app.include_router(hooks_router, prefix="/api")

app.include_router(webhooks_router, prefix="/api")
