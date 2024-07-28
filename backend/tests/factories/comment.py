from factory import LazyFunction

from db import models

from .base import BaseFactory
from .utils import fake


class CommentFactory(BaseFactory):
    text = LazyFunction(lambda: fake.text(max_nb_chars=999))
    is_blocked = False

    class Meta:
        model = models.Comment
