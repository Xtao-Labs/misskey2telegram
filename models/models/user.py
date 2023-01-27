import enum

from sqlmodel import SQLModel, Field, Enum, Column


class TokenStatusEnum(int, enum.Enum):
    STATUS_SUCCESS = 0
    INVALID_TOKEN = 1


class User(SQLModel, table=True):
    __table_args__ = dict(mysql_charset="utf8mb4", mysql_collate="utf8mb4_general_ci")

    user_id: int = Field(primary_key=True)
    token: str = Field(default="")
    status: TokenStatusEnum = Field(sa_column=Column(Enum(TokenStatusEnum)))
    chat_id: int = Field(default=0)
    timeline_topic: int = Field(default=0)
    notice_topic: int = Field(default=0)
