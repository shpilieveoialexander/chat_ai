from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, PositiveInt

from db import constants

from .post import Post
from .user import UserBase


class CommentCreate(BaseModel):
    text: str = Field(max_length=constants.MAX_LENGTH_TEXT)
    post_id: PositiveInt
    parent_id: Optional[PositiveInt] = None


class Comment(BaseModel):
    id: int
    text: str
    is_blocked: bool
    post_id: PositiveInt
    parent_id: Optional[PositiveInt] = None
    updated_at: datetime
    created_at: datetime
    user: UserBase
    post: Post


class CommentUpdate(BaseModel):
    text: str = Field(max_length=constants.MAX_LENGTH_TEXT)


class DailyCommentStats(BaseModel):
    date: date
    blocked_count: int
    unblocked_count: int


class CommentsDailyBreakdownResponse(BaseModel):
    breakdown: List[DailyCommentStats]
