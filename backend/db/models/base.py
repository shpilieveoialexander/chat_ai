from typing import Any, Dict

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase

from db.crud.base import BaseCRUD
from db.utils import get_default_now
from service.utils import camel_to_snake


class BaseModel(BaseCRUD, DeclarativeBase):
    """Base model"""

    id = Column(Integer, primary_key=True, index=True, doc="Unique element's ID or PK")
    created_at = Column(
        DateTime,
        nullable=False,
        default=get_default_now,
        doc="Created at",
    )

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return camel_to_snake(cls.__name__)

    def as_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
