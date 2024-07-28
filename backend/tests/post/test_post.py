import random

from fastapi import status

from tests import factories
from tests.conftests import TestCase
from tests.factories.utils import fake
from tests.utils import get_headers


class CreatePostTestCase(TestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/post/"

    def test_success_create_post(self) -> None:
        user = factories.UserFactory()
        response = self.client.post(
            self.url, json={"text": fake.text()}, headers=get_headers(user.id)
        )
        response.json()
        assert response.status_code == status.HTTP_201_CREATED

    def test_invalid_create_post_contain_inappropriate_language(self) -> None:
        user = factories.UserFactory()
        text = "some fucking test"
        response = self.client.post(
            self.url, json={"text": text}, headers=get_headers(user.id)
        )
        resp_data = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert resp_data["detail"] == "Post contains inappropriate language."

    def test_invalid_create_post_without_text(self) -> None:
        user = factories.UserFactory()
        response = self.client.post(self.url, headers=get_headers(user.id))
        response.json()
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_create_post_without_user_token(self) -> None:
        factories.UserFactory()
        text = fake.text()
        response = self.client.post(
            self.url,
            json={"text": text},
        )
        response.json()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class UpdatePostTestCase(TestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/post/"

    def test_success_update_post(self) -> None:
        user = factories.UserFactory()
        post = factories.PostFactory(user_id=user.id)
        url = f"{self.url}{post.id}"
        response = self.client.put(
            url, json={"text": fake.text()}, headers=get_headers(user.id)
        )
        response.json()
        assert response.status_code == status.HTTP_200_OK

    def test_invalid_update_post_contain_inappropriate_language(self) -> None:
        user = factories.UserFactory()
        post = factories.PostFactory(user_id=user.id)
        url = f"{self.url}{post.id}"
        response = self.client.put(
            url, json={"text": "some bitch, fuck"}, headers=get_headers(user.id)
        )
        resp_data = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert resp_data["detail"] == "Post contains inappropriate language."

    def test_invalid_update_post_empty_body(self) -> None:
        user = factories.UserFactory()
        post = factories.PostFactory(user_id=user.id)
        url = f"{self.url}{post.id}"
        response = self.client.put(url, json={}, headers=get_headers(user.id))
        response.json()
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_update_post_post_id_does_not_exists(self) -> None:
        user = factories.UserFactory()
        post = factories.PostFactory(user_id=user.id)
        url = f"{self.url}{random.randint(99, 9999)}"
        response = self.client.put(
            url, json={"text": fake.text()}, headers=get_headers(user.id)
        )
        resp_data = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert resp_data["detail"] == "Post not found or you can't edit it."

        def test_invalid_update_post_created_by_another_user(self) -> None:
            user_1 = factories.UserFactory()
            user_2 = factories.UserFactory()
            post = factories.PostFactory(user_id=user_1.id)
            url = f"{self.url}{post.id}"
            response = self.client.put(
                url, json={"text": fake.text()}, headers=get_headers(user_2.id)
            )
            resp_data = response.json()
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert resp_data["detail"] == "Post not found or you can't edit it."


class DeletePostTestCase(TestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/post/"

    def test_success_delete_post(self) -> None:
        user = factories.UserFactory()
        post = factories.PostFactory(user_id=user.id)
        url = f"{self.url}{post.id}"
        response = self.client.delete(url, headers=get_headers(user.id))
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_invalid_delete_post_post_id_does_not_exists(self) -> None:
        user = factories.UserFactory()
        url = f"{self.url}{random.randint(99, 9999)}"
        response = self.client.delete(url, headers=get_headers(user.id))
        assert response.status_code == status.HTTP_204_NO_CONTENT


class GetPostByIdTestCase(TestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/post/"

    def test_success_get_post_by_id(self) -> None:
        user = factories.UserFactory()
        post = factories.PostFactory(user_id=user.id)
        url = f"{self.url}{post.id}"
        response = self.client.get(url, headers=get_headers(user.id))
        assert response.status_code == status.HTTP_200_OK

    def test_invalid_get_post_by_id_invalid_id(self) -> None:
        user = factories.UserFactory()
        post = factories.PostFactory(user_id=user.id)
        url = f"{self.url}{random.randint(99, 9999)}"
        response = self.client.get(url, headers=get_headers(user.id))
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Post not found"
