import re

from service.core import settings


def camel_to_snake(name):
    """Change `camelCase` to `snake_case`"""
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub("__([A-Z])", r"_\1", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def is_test_session(session) -> bool:
    """Check DB session"""
    uri = session.session_factory.__dict__["kw"]["bind"].url
    current_db = uri.__str__().split("/")[-1]
    return current_db == settings.PSQL_TEST_DB_NAME
