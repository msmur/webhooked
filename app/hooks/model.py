from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, Literal

from pydantic_core.core_schema import ValidationInfo

from .hook_id import HookId


class HookBase(BaseModel):
    name: str
    description: str
    status: str
    expires_at: Optional[date] = None
    correlation_identifier_location: Optional[Literal["headers", "payload"]] = None
    correlation_identifier_field: Optional[str] = None

    @field_validator("correlation_identifier_field", mode="before")
    def validate_correlation_identifier_field(cls, value: str, info: ValidationInfo):
        """
        If correlation_identifier_location is 'headers', ensure that
        correlation_identifier_field is in lowercase since HTTP headers are case-insensitive.
        """
        location = info.data["correlation_identifier_location"]
        if location == "headers" and value:
            return value.lower()
        return value


class HookCreate(HookBase):
    pass


class Hook(HookBase):
    id: HookId
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
