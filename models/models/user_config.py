import sqlalchemy as sa
from sqlmodel import SQLModel, Field, Column


class UserConfig(SQLModel, table=True):
    __tablename__ = "user_config"
    __table_args__ = dict(mysql_charset="utf8mb4", mysql_collate="utf8mb4_general_ci")

    user_id: int = Field(sa_column=Column(sa.BigInteger, primary_key=True))
    timeline_spoiler: bool = Field(default=False)
    push_spoiler: bool = Field(default=False)
