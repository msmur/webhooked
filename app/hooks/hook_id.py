import uuid
from typing import Any, ClassVar

from pydantic import BaseModel, field_validator, model_serializer


class HookId(BaseModel):
    PREFIX: ClassVar[str] = "hook-"

    value: str

    @classmethod
    def generate(cls) -> "HookId":
        """Generate a new HookId with a UUID v4."""
        return cls(value=f"{cls.PREFIX}{uuid.uuid4()}")

    @field_validator("value", mode="before")
    @classmethod
    def is_valid_hook_id(cls, value: str) -> str:
        """Validate that the value has the correct format."""
        if not isinstance(value, str):  # Ensure it's a string
            raise ValueError(f"Expected a string, but got {type(value)}")
        if not value.startswith(HookId.PREFIX):
            raise ValueError("Invalid prefix for the HookID")
        try:
            uuid_part = value[len(HookId.PREFIX) :]
            uuid.UUID(uuid_part)  # Validate UUID part
        except ValueError:
            raise ValueError("Invalid UUID component for the HookID")

        return value

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: Any) -> bool:
        """Compare equality based on the value."""
        return isinstance(other, HookId) and self.value == other.value

    @model_serializer
    def serialize(self) -> str:
        """Serialize HookId as a plain string."""
        return self.value

    @property
    def get_value(self) -> str:
        """Expose the underlying value."""
        return self.value
