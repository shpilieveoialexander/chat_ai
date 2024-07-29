from fastapi import APIRouter
from fastapi_pagination import add_pagination

from .comment import comment
from .post import post
from .user import auth, user

router_v1 = APIRouter()


add_pagination(router_v1)


router_v1.include_router(auth.router, tags=["Auth"], prefix="/auth")
router_v1.include_router(user.router, tags=["User"], prefix="/user")
router_v1.include_router(post.router, tags=["Post"], prefix="/post")
router_v1.include_router(comment.router, tags=["Comment"], prefix="/comment")
