from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from db import constants
from db.utils import get_default_now

from .base import BaseModel
from .post import Post
from .user import User


class Comment(BaseModel):
    """comment model"""

    creator_id = Column(
        Integer,
        ForeignKey(User.id, ondelete="CASCADE"),
        nullable=False,
        doc="User id",
    )
    post_id = Column(
        Integer,
        ForeignKey(Post.id, ondelete="CASCADE"),
        nullable=False,
        doc="Post id",
    )
    parent_comment_id = Column(
        Integer,
        ForeignKey("comment.id", ondelete="CASCADE"),
        nullable=True,
        doc="Parent comment id (for nested comments)",
    )
    text = Column(
        String(length=constants.MAX_LENGTH_TEXT),
        nullable=True,
        doc="Text of the comment",
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=get_default_now,
        doc="Updated at",
    )
    is_blocked = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Is the post blocked",
    )
    user: Mapped[User] = relationship(User, uselist=False, lazy="joined")
    post: Mapped[Post] = relationship(Post, uselist=False, lazy="joined")
