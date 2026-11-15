from decimal import Decimal
from unittest.mock import patch, MagicMock

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from payments.models import Payment
from payments.services import create_stripe_session


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def basic_setup(db):
    from django.contrib.auth import get_user_model
    from books.models import Book
    from borrowings.models import Borrowing
    from datetime import date, timedelta

    User = get_user_model()
    user = User.objects.create_user(email="user@example.com", password="password123")
    admin = User.objects.create_superuser(
        email="admin@example.com", password="password123"
    )
    book = Book.objects.create(
        title="Python Book", daily_fee=Decimal("10.00"), inventory=10
    )

    borrowing = Borrowing.objects.create(
        user=user,
        book=book,
        borrow_date=date.today(),
        expected_return_date=date.today() + timedelta(days=2),
    )
    return {"user": user, "admin": admin, "borrowing": borrowing}


@pytest.mark.django_db
class TestPaymentViewSetLight:
    def test_user_sees_only_their_payments(self, api_client, basic_setup):
        Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            borrowing=basic_setup["borrowing"],
            session_url="url",
            session_id="sess_1",
            money_to_pay=Decimal("20.00"),
        )

        api_client.force_authenticate(user=basic_setup["user"])
        response = api_client.get(reverse("payments:payment-list"))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1


@pytest.mark.django_db
class TestPaymentViewsLight:
    def test_payment_cancel(self, api_client):
        response = api_client.get(reverse("payments:cancel"))
        assert response.status_code == status.HTTP_200_OK
        assert "canceled" in response.data["message"]

    def test_success_missing_session_id(self, api_client):
        response = api_client.get(reverse("payments:success"))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Session ID is required"

    @patch("stripe.checkout.Session.retrieve")
    def test_payment_success_flow(self, mock_stripe_retrieve, api_client, basic_setup):
        payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            borrowing=basic_setup["borrowing"],
            session_url="url",
            session_id="cs_test_123",
            money_to_pay=Decimal("20.00"),
        )
        mock_stripe_retrieve.return_value = MagicMock(payment_status="paid")

        response = api_client.get(
            reverse("payments:success") + "?session_id=cs_test_123"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Payment successful!"

        payment.refresh_from_db()
        assert payment.status == Payment.StatusChoices.PAID


@pytest.mark.django_db
class TestCreateStripeSessionLight:
    @patch("stripe.checkout.Session.create")
    def test_create_stripe_session_basic(self, mock_stripe_create, basic_setup):
        mock_stripe_create.return_value = MagicMock(
            url="https://checkout.stripe.com/test", id="cs_test_session"
        )

        payment = create_stripe_session(borrowing=basic_setup["borrowing"])

        assert payment is not None
        assert payment.money_to_pay == Decimal("20.00")
        assert payment.status == Payment.StatusChoices.PENDING
        assert payment.type == Payment.TypeChoices.PAYMENT
