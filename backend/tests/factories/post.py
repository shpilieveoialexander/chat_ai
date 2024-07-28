from factory import LazyFunction

from db import models

from .base import BaseFactory
from .utils import fake


class PostFactory(BaseFactory):
    text = LazyFunction(lambda: fake.text(max_nb_chars=999))

    class Meta:
        model = models.Post
