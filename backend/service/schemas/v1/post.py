from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from db import constants

from .user import UserBase


class PostCreate(BaseModel):
    text: str = Field(max_length=constants.MAX_LENGTH_TEXT)


class Post(BaseModel):
    id: int
    text: str
    updated_at: datetime
    created_at: datetime
    user: UserBase
    model_config = ConfigDict(arbitrary_types_allowed=True)
