"""Added correlation identifiers to the Hook object

Revision ID: 0b4c46d1c65c
Revises: 6a5583a5ec48
Create Date: 2025-02-22 08:43:30.319361

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "0b4c46d1c65c"
down_revision: Union[str, None] = "6a5583a5ec48"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Define the ENUM type
correlation_location_enum = postgresql.ENUM(
    "headers", "payload", name="correlation_location_enum", create_type=True
)


def upgrade():
    # Create ENUM type first
    correlation_location_enum.create(op.get_bind(), checkfirst=True)

    # Add the new columns
    op.add_column(
        "hooks",
        sa.Column(
            "correlation_identifier_location", correlation_location_enum, nullable=True
        ),
    )
    op.add_column(
        "hooks", sa.Column("correlation_identifier_field", sa.String(), nullable=True)
    )


def downgrade():
    # Remove the columns first
    op.drop_column("hooks", "correlation_identifier_location")
    op.drop_column("hooks", "correlation_identifier_field")

    # Drop ENUM type after columns are removed
    correlation_location_enum.drop(op.get_bind(), checkfirst=True)
