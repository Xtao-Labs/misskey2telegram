"""user

Revision ID: a89b6e618441
Revises: 
Create Date: 2023-07-29 13:05:51.912893

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = "a89b6e618441"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("STATUS_SUCCESS", "INVALID_TOKEN", name="tokenstatusenum"),
            nullable=True,
        ),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("push_chat_id", sa.BigInteger(), nullable=True),
        sa.Column("host", sqlmodel.AutoString(), nullable=False),
        sa.Column("token", sqlmodel.AutoString(), nullable=False),
        sa.Column("timeline_topic", sa.Integer(), nullable=False),
        sa.Column("notice_topic", sa.Integer(), nullable=False),
        sa.Column("instance_user_id", sqlmodel.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("user_id", "chat_id"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_general_ci",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user")
    # ### end Alembic commands ###
