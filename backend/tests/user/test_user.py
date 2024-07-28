from fastapi import status

from tests import factories
from tests.conftests import TestCase
from tests.utils import get_headers


class UserMeTestCase(TestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/user/me/"

    def test_success_get_user_me(self) -> None:
        user = factories.UserFactory()
        response = self.client.get(self.url, headers=get_headers(user.id))
        resp_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert resp_data["id"] == user.id

    def test_fail_get_user_me_without_authorization(self) -> None:
        factories.UserFactory()
        response = self.client.get(self.url)
        resp_data = response.json()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp_data["detail"] == "Not authenticated"
