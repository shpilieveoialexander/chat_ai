"""add post is_blocked

Revision ID: 1be81cad4ea0
Revises: 1b2b223e4284
Create Date: 2024-07-28 13:45:32.704420

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1be81cad4ea0"
down_revision = "1b2b223e4284"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("post", sa.Column("is_blocked", sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("post", "is_blocked")
    # ### end Alembic commands ###