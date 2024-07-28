from better_profanity import profanity
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import PositiveInt
from sqlalchemy import select

from db import models
from db.session import DBSession
from service.core.dependencies import get_current_user, get_session
from service.schemas import v1 as schemas_v1

router = APIRouter()
profanity.load_censor_words()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas_v1.Post)
async def create_posts(
    input_data: schemas_v1.PostCreate,
    current_user: models.User = Depends(get_current_user),
    session: DBSession = Depends(get_session),
) -> models.Post:
    """
    Return Post  info\n
    Responses:\n
    `201` CREATED - Everything is good (SUCCESS Response)\n
    `400` BAD_REQUEST - Post contains inappropriate language.\n
    `401` UNAUTHORIZED - You have not provided authorization token\n
    `403` FORBIDDEN - Invalid authorization\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    if profanity.contains_profanity(input_data.text):
        post = models.Post(
            user_id=current_user.id, text=input_data.text, is_blocked=True
        )
        with session() as db:
            db.add(post)
            db.commit()
            db.refresh(post)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post contains inappropriate language.",
        )

    post = models.Post(user_id=current_user.id, text=input_data.text, is_blocked=False)
    with session() as db:
        db.add(post)
        db.commit()
        db.refresh(post)

    return post


@router.put("/{post_id}", response_model=schemas_v1.Post)
async def update_post(
    post_id: PositiveInt,
    input_data: schemas_v1.PostCreate,
    current_user: models.User = Depends(get_current_user),
    session: DBSession = Depends(get_session),
) -> models.Post:
    """
    Return Post  info\n
    Responses:\n
    `200` OK - Everything is good (SUCCESS Response)\n
    `400` BAD_REQUEST - Post contains inappropriate language.\n
    `400` BAD_REQUEST - Post not found or you can't edit it.\n
    `401` UNAUTHORIZED - You have not provided authorization token\n
    `403` FORBIDDEN - Invalid authorization\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    post_query = select(models.Post).where(
        models.Post.id == post_id, models.Post.user_id == current_user.id
    )
    with session() as db:
        post = db.scalars(post_query).unique().one_or_none()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post not found or you can't edit it.",
        )
    if profanity.contains_profanity(input_data.text):
        post.text = input_data.text
        post.is_blocked = True
        with session() as db:
            db.add(post)
            db.commit()
            db.refresh(post)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post contains inappropriate language.",
        )
    post.text = input_data.text
    with session() as db:
        db.add(post)
        db.commit()
        db.refresh(post)

    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: PositiveInt,
    current_user: models.User = Depends(get_current_user),
    session: DBSession = Depends(get_session),
) -> None:
    """
    Delete post\n
    Obtain  post_id and delete it\n
    Responses:\n
    `204` OK - Everything is good (SUCCESS Response)\n
    `401` UNAUTHORIZED - You have not provided authorization token\n
    """
    delete_query = models.Post.delete().where(
        models.Post.id == post_id, models.Post.user_id == current_user.id
    )
    with session() as db:
        db.execute(delete_query)
        db.commit()
    return


@router.get("/{post_id}", response_model=schemas_v1.Post)
async def get_post_by_id(
    post_id: PositiveInt,
    _: models.User = Depends(get_current_user),
    session: DBSession = Depends(get_session),
) -> models.Post:
    """
    Return Post  info\n
    Responses:\n
    `200` OK - Everything is good (SUCCESS Response)\n
    `404` NOT_FOUND - Post not found\n
    `401` UNAUTHORIZED - You have not provided authorization token\n
    `403` FORBIDDEN - Invalid authorization\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    post_query = select(models.Post).where(models.Post.id == post_id)
    with session() as db:
        post = db.scalars(post_query).unique().one_or_none()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    return post


@router.get("/", response_model=Page[schemas_v1.Post])
async def get_posts_list(
    session: DBSession = Depends(get_session),
    _: models.Post = Depends(get_current_user),
):
    """
    Get  Post List\n
    Responses:\n
    `200` OK - Everything is good (SUCCESS Response)\n
    `401` UNAUTHORIZED - You have not provided authorization token\n
    """
    post_list_query = select(models.Post)

    with session() as db:
        return paginate(db, post_list_query)
