"""fcm

Revision ID: fcdaa7ac5975
Revises: a89b6e618441
Create Date: 2023-08-03 16:45:44.084709

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fcdaa7ac5975"
down_revision = "a89b6e618441"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user", sa.Column("fcm_token", sa.String(), nullable=True, default="")
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "fcm_token")
    # ### end Alembic commands ###
