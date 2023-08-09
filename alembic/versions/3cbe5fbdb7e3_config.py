"""config

Revision ID: 3cbe5fbdb7e3
Revises: fcdaa7ac5975
Create Date: 2023-08-09 14:36:48.093192

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3cbe5fbdb7e3"
down_revision = "fcdaa7ac5975"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user_config",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("timeline_spoiler", sa.Boolean(), nullable=False),
        sa.Column("push_spoiler", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_general_ci",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user_config")
    # ### end Alembic commands ###
