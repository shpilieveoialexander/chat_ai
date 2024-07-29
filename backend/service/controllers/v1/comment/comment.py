from datetime import date

from better_profanity import profanity
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import PositiveInt
from sqlalchemy import select

from db import models
from db.session import DBSession
from service.core.dependencies import get_current_user, get_session
from service.schemas import v1 as schemas_v1

from .utils import get_comments_breakdown

router = APIRouter()
profanity.load_censor_words()


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas_v1.Comment
)
async def create_comment(
    input_data: schemas_v1.CommentCreate,
    current_user: models.User = Depends(get_current_user),
    session: DBSession = Depends(get_session),
) -> models.Comment:
    """
    Obtains a new comment from the input data.
    Return Comment  info\n
    Responses:\n
    `201` CREATED - Everything is good (SUCCESS Response)\n
    `400` BAD_REQUEST - Comment contains inappropriate language.\n
    `401` UNAUTHORIZED - You have not provided authorization token\n
    `403` FORBIDDEN - Invalid authorization\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    post_query = select(models.Post).where(models.Post.id == input_data.post_id)
    with session() as db:
        post = db.scalars(post_query).unique().one_or_none()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    if input_data.parent_id:
        comment = models.Comment(
            creator_id=current_user.id,
            text=input_data.text,
            parent_comment_id=input_data.parent_id,
            post_id=input_data.post_id,
        )
    comment = models.Comment(
        creator_id=current_user.id, text=input_data.text, post_id=input_data.post_id
    )
    if profanity.contains_profanity(input_data.text):
        comment.is_blocked = True
        with session() as db:
            db.add(comment)
            db.commit()
            db.refresh(comment)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment contains inappropriate language.",
        )

    comment.is_blocked = False
    with session() as db:
        db.add(comment)
        db.commit()
        db.refresh(comment)

    return comment


@router.put("/{comment_id}", response_model=schemas_v1.Comment)
async def update_comment(
    comment_id: PositiveInt,
    input_data: schemas_v1.CommentUpdate,
    current_user: models.User = Depends(get_current_user),
    session: DBSession = Depends(get_session),
) -> models.Comment:
    """
    Updates a comment from the input data.
    Return Comment  info\n
    Responses:\n
    `201` CREATED - Everything is good (SUCCESS Response)\n
    `400` BAD_REQUEST - Comment not found or you can't edit it.\n
    `400` BAD_REQUEST - Comment contains inappropriate language.\n
    `401` UNAUTHORIZED - You have not provided authorization token\n
    `403` FORBIDDEN - Invalid authorization\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    comment_query = select(models.Comment).where(
        models.Comment.id == comment_id,
        models.Comment.creator_id == current_user.id,
    )
    with session() as db:
        comment = db.scalars(comment_query).unique().one_or_none()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment not found or you can't edit it",
        )
    if profanity.contains_profanity(input_data.text):
        comment.is_blocked = True
        comment.text = input_data.text
        with session() as db:
            db.add(comment)
            db.commit()
            db.refresh(comment)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment contains inappropriate language.",
        )
    comment.text = input_data.text
    with session() as db:
        db.add(comment)
        db.commit()
        db.refresh(comment)
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: PositiveInt,
    current_user: models.User = Depends(get_current_user),
    session: DBSession = Depends(get_session),
) -> None:
    """
    Delete comment\n
    Obtain  comment_id and delete it\n
    Responses:\n
    `204` OK - Everything is good (SUCCESS Response)\n
    `401` UNAUTHORIZED - You have not provided authorization token\n
    """
    delete_query = models.Comment.delete().where(
        models.Comment.id == comment_id, models.Comment.creator_id == current_user.id
    )
    with session() as db:
        db.execute(delete_query)
        db.commit()
    return


@router.get("/{comment_id}", response_model=schemas_v1.Comment)
async def get_comment_by_id(
    comment_id: PositiveInt,
    current_user: models.User = Depends(get_current_user),
    session: DBSession = Depends(get_session),
) -> models.Comment:
    """
     Return Comment  info\n
    Responses:\n
    `200` OK - Everything is good (SUCCESS Response)\n
    `404` NOT_FOUND - Post not found\n
    `401` UNAUTHORIZED - You have not provided authorization token\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """

    comment_query = select(models.Comment).where(models.Comment.id == comment_id)
    with session() as db:
        comment = db.scalars(comment_query).unique().one_or_none()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    return comment


@router.get("/daily-breakdown/", response_model=schemas_v1.DailyCommentStatsResponse)
def get_comments_daily_breakdown(
    date_from: date = Query(...),
    date_to: date = Query(...),
    current_user: models.User = Depends(get_current_user),
    session: DBSession = Depends(get_session),
):
    """
     Return Comment  info\n
    Responses:\n
    `200` OK - Everything is good (SUCCESS Response)\n
    `404` NOT_FOUND - Post not found\n
    `401` UNAUTHORIZED - You have not provided authorization token\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    return get_comments_breakdown(session, date_from, date_to)
