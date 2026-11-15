import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestUserApi:
    def test_create_user_success(self, api_client):
        url = reverse("user:create")
        payload = {"email": "newuser@example.com", "password": "securepassword123"}
        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert "email" in response.data
        assert response.data["email"] == payload["email"]
        assert "password" not in response.data

    def test_retrieve_user_profile_authenticated(self, api_client):
        User = get_user_model()
        user = User.objects.create_user(
            email="profile@example.com", password="password123"
        )
        api_client.force_authenticate(user=user)

        url = reverse("user:manage_user")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email

    def test_retrieve_user_profile_unauthenticated(self, api_client):
        url = reverse("user:manage_user")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
