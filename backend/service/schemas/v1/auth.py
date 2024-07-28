from fastapi import Form
from fastapi.exceptions import ValidationException
from pydantic import EmailStr

from db import constants


class Auth:
    def __init__(
        self,
        email: EmailStr = Form(...),
        password: str = Form(
            ..., min_length=constants.PASSWORD_MIN, max_length=constants.PASSWORD_MAX
        ),
    ):
        self.email = email
        self.password = password


class SignUp(Auth):
    def __init__(
        self,
        name: str = Form(...),
        email: EmailStr = Form(...),
        password: str = Form(
            ..., min_length=constants.PASSWORD_MIN, max_length=constants.PASSWORD_MAX
        ),
        password_confirm: str = Form(
            ..., min_length=constants.PASSWORD_MIN, max_length=constants.PASSWORD_MAX
        ),
    ):
        if password != password_confirm:
            raise ValidationException("Password missmatch")
        super().__init__(email, password)
        self.name = name
        self.password_confirm = password_confirm
