"""Seed a demo admin account for viewing the admin panel.

Revision ID: a7d3c9e1f2b4
Revises: 49c0ef330aa2
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a7d3c9e1f2b4"
down_revision: Union[str, Sequence[str], None] = "49c0ef330aa2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEMO_ADMIN_EMAIL = "demo.admin@example.com"
# bcrypt hash only; the password itself is not stored in the repository.
DEMO_ADMIN_PASSWORD_HASH = "$2b$12$ed67yngK84KHRdKlzSAELem4luECABo6rO/5ydMzC41POE.wKmR7i"


def upgrade() -> None:
    op.get_bind().execute(
        sa.text(
            "INSERT INTO users (email, password_hash, role, is_active, is_verified, is_deleted) "
            "VALUES (:email, :hash, 'admin', true, true, false) "
            "ON CONFLICT (email) DO NOTHING"
        ),
        {"email": DEMO_ADMIN_EMAIL, "hash": DEMO_ADMIN_PASSWORD_HASH},
    )


def downgrade() -> None:
    op.get_bind().execute(
        sa.text("DELETE FROM users WHERE email = :email"), {"email": DEMO_ADMIN_EMAIL}
    )
