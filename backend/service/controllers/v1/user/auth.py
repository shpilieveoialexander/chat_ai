from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import UJSONResponse

from db import constants, models
from db.session import DBSession
from service.core import settings
from service.core.dependencies import get_refresh_token, get_session
from service.core.security import (create_jwt_token, hash_password,
                                   verify_password)
from service.schemas import v1 as schemas_v1

router = APIRouter()


@router.post("/access-token/", response_model=schemas_v1.JWTTokensResponse)
async def login(
    form_data: schemas_v1.Auth = Depends(), session: DBSession = Depends(get_session)
) -> UJSONResponse:
    """
    Login\n
    Obtain email and password, and return access and refresh tokens for future requests\n
    Responses:\n
    `200` OK - Everything is good (SUCCESS Response)\n
    `403` FORBIDDEN - Invalid password\n
    `404` NOT_FOUND - User is inactive or not found\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    # Get user
    user_query = models.User.get_one(email=form_data.email)
    with session() as db:
        user = db.scalars(user_query).one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    # Verify password
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )
    return UJSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "access_token": create_jwt_token(user.id),
            "refresh_token": create_jwt_token(
                user.id, jwt_type=constants.JWTType.REFRESH
            ),
            "token_type": "Bearer",
            "access_token_lifetime": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_lifetime": settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
        },
    )


@router.post("/refresh-token/", response_model=schemas_v1.JWTTokensResponse)
async def refresh_token(
    token_data: schemas_v1.JWTTokenPayload = Depends(get_refresh_token),
    session: DBSession = Depends(get_session),
) -> UJSONResponse:
    """
    Refresh token\n
    Obtain refresh token  return access tokens and refresh token\n
    Responses:\n
    `200` OK - Everything is good (SUCCESS Response)\n
    `401` UNAUTHORIZED - Not authenticated\n
    `403` FORBIDDEN - Could not validate credentials\n
    `404` NOT_FOUND - User is inactive or not found\n
    """
    # Checking existing user
    exists_query = models.User.exists(
        id=token_data.pk,
    )
    with session() as db:
        user_exists = db.execute(exists_query).scalar()

    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User blocked or not found",
        )
    # Return new JWT tokens
    return UJSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "access_token": create_jwt_token(token_data.pk),
            "refresh_token": create_jwt_token(
                token_data.pk, jwt_type=constants.JWTType.REFRESH
            ),
            "token_type": "Bearer",
            "access_token_lifetime": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_lifetime": settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
        },
    )


@router.post(
    "/user/sign-up/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas_v1.JWTTokensResponse,
)
async def user_sign_up(
    form_data: schemas_v1.SignUp = Depends(),
    session: DBSession = Depends(get_session),
) -> UJSONResponse:
    """
    Sign Up User. Return User\n
    Responses:\n
    `201` CREATED - Everything is good (SUCCESS Response)\n
    `404` NOT_FOUND - Group not found\n
    `409` CONFLICT - User with this email exists\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    email_exists_query = models.User.exists(email=form_data.email)
    with session() as db:
        email_exists = db.execute(email_exists_query).scalar()
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {form_data.email} exists",
        )
    # Create new user
    user = models.User(
        name=form_data.name,
        email=form_data.email,
        password=hash_password(form_data.password),
    )

    with session() as db:
        db.add(user)
        db.commit()
        db.refresh(user)

    # Return JWT tokens
    return UJSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "access_token": create_jwt_token(user.id),
            "refresh_token": create_jwt_token(
                user.id, jwt_type=constants.JWTType.REFRESH
            ),
            "token_type": "Bearer",
            "access_token_lifetime": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_lifetime": settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
        },
    )
