import sys
from datetime import datetime
from fastapi import FastAPI, Depends, Path
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

from alembic import command
from alembic.config import Config

from app.config import DB_CONNECTION_STRING
from app.database import get_db
from sqlalchemy.orm import Session

from app.hooks import router as hooks_router
from app.webhooks import router as webhooks_router
from app.healthcheck import router as healthcheck_router
from app.hooks.repository import get_all_hooks
from app.logger import configure_logging

from contextlib import asynccontextmanager

from loguru import logger


# Alembic configuration
ALEMBIC_CONFIG = Config("alembic.ini")
ALEMBIC_CONFIG.set_main_option("sqlalchemy.url", DB_CONNECTION_STRING)


# Function to run migrations
def run_migrations():
    command.upgrade(ALEMBIC_CONFIG, "head")
    logger.info("Migrations ran successfully.")


# Create a lifespan function for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    yield
    logger.info("Application is shutting down.")


configure_logging()


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Received request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


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


app.include_router(healthcheck_router, prefix="/api")

app.include_router(hooks_router, prefix="/api")

app.include_router(webhooks_router, prefix="/api")
