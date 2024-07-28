import random

from fastapi import status

from tests import factories
from tests.conftests import TestCase
from tests.factories.utils import fake
from tests.utils import get_headers


class CreateCommentTestCase(TestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/comment/"

    def test_success_create_comment(self) -> None:
        user = factories.UserFactory()
        post = factories.PostFactory(user_id=user.id)
        body = {"text": fake.text(), "post_id": post.id, "parent_id": None}
        response = self.client.post(self.url, json=body, headers=get_headers(user.id))
        response.json()
        assert response.status_code == status.HTTP_201_CREATED

    def test_success_create_comment_for_comment(self) -> None:
        user_1 = factories.UserFactory()
        user_2 = factories.UserFactory()
        post = factories.PostFactory(user_id=user_1.id)
        comment = factories.CommentFactory(post_id=post.id, creator_id=user_2.id)
        body = {"text": fake.text(), "post_id": post.id, "parent_id": comment.id}
        response = self.client.post(self.url, json=body, headers=get_headers(user_2.id))
        response.json()
        assert response.status_code == status.HTTP_201_CREATED

    def test_invalid_create_comment_empty_post_id(self) -> None:
        user = factories.UserFactory()
        post = factories.PostFactory(user_id=user.id)
        body = {"text": fake.text(), "parent_id": None}
        response = self.client.post(self.url, json=body, headers=get_headers(user.id))
        response.json()
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_create_comment_empty_text(self) -> None:
        user = factories.UserFactory()
        post = factories.PostFactory(user_id=user.id)
        body = {"parent_id": None, "post_id": post.id}
        response = self.client.post(self.url, json=body, headers=get_headers(user.id))
        response.json()
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_create_comment_invalid_post_id(self) -> None:
        user = factories.UserFactory()
        post = factories.PostFactory(user_id=user.id)
        body = {
            "text": fake.text(),
            "post_id": random.randint(99, 9999),
            "parent_id": None,
        }
        response = self.client.post(self.url, json=body, headers=get_headers(user.id))
        resp_data = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert resp_data["detail"] == "Post not found"

    def test_invalid_create_comment_inappropriate_language(self) -> None:
        user = factories.UserFactory()
        post = factories.PostFactory(user_id=user.id)
        body = {"text": "some bitch", "post_id": post.id, "parent_id": None}
        response = self.client.post(self.url, json=body, headers=get_headers(user.id))
        resp_data = response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert resp_data["detail"] == "Comment contains inappropriate language."


class UpdateCommentTestCase(TestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/comment/"

    def test_success_update_comment(self) -> None:
        user = factories.UserFactory()
        post = factories.PostFactory(user_id=user.id)
        comment = factories.CommentFactory(post_id=post.id, creator_id=user.id)
        url = f"{self.url}{comment.id}"
        body = {"text": fake.text()}
        response = self.client.put(url, json=body, headers=get_headers(user.id))
        response.json()
        assert response.status_code == status.HTTP_200_OK

    def test_invalid_update_comment_empty_comment_id(self) -> None:
        user = factories.UserFactory()
        post = factories.PostFactory(user_id=user.id)
        url = f"/api/v1/comment/{random.randint(99, 9999)}"
        body = {"text": fake.text()}
        response = self.client.put(url, json=body, headers=get_headers(user.id))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Comment not found or you can't edit it"

    def test_invalid_update_comment_empty_body(self) -> None:
        user = factories.UserFactory()
        post = factories.PostFactory(user_id=user.id)
        comment = factories.CommentFactory(post_id=post.id, creator_id=user.id)
        url = f"/api/v1/comment/{comment.id}"
        body = {}
        response = self.client.put(url, json=body, headers=get_headers(user.id))
        response.json()
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_update_comment_inappropriate_language(self) -> None:
        user = factories.UserFactory()
        post = factories.PostFactory(user_id=user.id)
        comment = factories.CommentFactory(post_id=post.id, creator_id=user.id)
        url = f"/api/v1/comment/{comment.id}"
        body = {"text": "some shit"}
        response = self.client.put(url, json=body, headers=get_headers(user.id))
        response.json()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Comment contains inappropriate language."


class DeleteCommentTestCase(TestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/comment/"

    def test_success_delete_comment(self) -> None:
        user = factories.UserFactory()
        post = factories.PostFactory(user_id=user.id)
        comment = factories.CommentFactory(post_id=post.id, creator_id=user.id)
        url = f"{self.url}{comment.id}"
        response = self.client.delete(url, headers=get_headers(user.id))
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_invalid_delete_comment_invalid_comment_id(self) -> None:
        user = factories.UserFactory()
        url = f"{self.url}{random.randint(99, 9999)}"
        response = self.client.delete(url, headers=get_headers(user.id))
        assert response.status_code == status.HTTP_204_NO_CONTENT


class GetCommentByIdTestCase(TestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/comment/"

    def test_success_get_comment(self) -> None:
        user = factories.UserFactory()
        post = factories.PostFactory(user_id=user.id)
        comment = factories.CommentFactory(post_id=post.id, creator_id=user.id)
        url = f"{self.url}{comment.id}"
        response = self.client.get(url, headers=get_headers(user.id))
        assert response.status_code == status.HTTP_200_OK

    def test_invalid_get_comment_invalid_comment_id(self) -> None:
        user = factories.UserFactory()
        url = f"{self.url}{random.randint(99, 9999)}"
        response = self.client.get(url, headers=get_headers(user.id))
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Comment not found"
