from fastapi import APIRouter, Depends

from db import models
from db.session import DBSession
from service.core.dependencies import (get_access_token, get_current_user,
                                       get_session)
from service.schemas import v1 as schemas_v1

router = APIRouter()


@router.get("/me/", response_model=schemas_v1.UserBase)
async def user_me(
    token_payload: schemas_v1.JWTTokenPayload = Depends(get_access_token),
    session: DBSession = Depends(get_session),
    user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Return User me info\n
    Responses:\n
    `200` OK - Everything is good (SUCCESS Response)\n
    `401` UNAUTHORIZED - You have not provided authorization token\n
    `403` FORBIDDEN - Invalid authorization\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    return user
