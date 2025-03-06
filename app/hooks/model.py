from datetime import date, datetime

from jsonpath_ng.exceptions import JsonPathParserError
from pydantic import BaseModel, ConfigDict, field_validator, computed_field
from typing import Optional, Literal
from jsonpath_ng import parse

from pydantic_core.core_schema import ValidationInfo

from .hook_id import HookId
from ..config import BASE_URL


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

        if location == "payload" and value:
            try:
                parse(value)
            except JsonPathParserError:
                raise ValueError(f"Invalid JSONPath expression: {value}")

        return value


class HookCreate(HookBase):
    pass


class Hook(HookBase):
    id: HookId
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @computed_field()
    @property
    def webhooks_url(self) -> str:
        return f"{BASE_URL}/api/hooks/{self.id.value}/webhooks"  # Generates the webhook URL

    model_config = ConfigDict(from_attributes=True)
