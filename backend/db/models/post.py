from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from db import constants
from db.utils import get_default_now

from .base import BaseModel
from .user import User


class Post(BaseModel):
    """Post model"""

    user_id = Column(
        Integer,
        ForeignKey(User.id, ondelete="CASCADE"),
        nullable=False,
        doc="User id",
    )
    text = Column(
        String(length=constants.MAX_LENGTH_TEXT),
        nullable=True,
        doc="Text of the post",
    )
    is_blocked = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Is the post blocked",
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=get_default_now,
        doc="Updated at",
    )
    user: Mapped[User] = relationship(User, uselist=False, lazy="joined")
