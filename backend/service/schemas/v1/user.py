from typing import Optional

from pydantic import BaseModel, EmailStr, PositiveInt


class UserBase(BaseModel):
    """Base User fields"""

    id: PositiveInt
    email: EmailStr
    name: Optional[str]
