from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from books.models import Book
from borrowings.models import Borrowing


class BorrowingApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="password123", is_staff=False
        )
        self.client.force_authenticate(user=self.user)

        self.book = Book.objects.create(
            title="Python Testing",
            author="Author",
            cover=Book.CoverType.HARD,
            inventory=2,
            daily_fee=Decimal("1.50"),
        )
        self.borrowings_url = reverse("borrowings:borrowing-list")

    @patch("borrowings.serializers.create_stripe_session")
    @patch("borrowings.notifications.send_telegram_message")
    def test_create_borrowing_success(self, mock_telegram, mock_stripe):
        payload = {
            "book": self.book.id,
            "expected_return_date": str(date.today() + timedelta(days=5)),
        }
        response = self.client.post(self.borrowings_url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Borrowing.objects.count(), 1)

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 1)

    @patch("borrowings.serializers.create_stripe_session")
    @patch("borrowings.notifications.send_telegram_message")
    def test_cannot_borrow_when_inventory_zero(self, mock_telegram, mock_stripe):
        self.book.inventory = 0
        self.book.save()

        payload = {
            "book": self.book.id,
            "expected_return_date": str(date.today() + timedelta(days=5)),
        }
        response = self.client.post(self.borrowings_url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("book", response.data)

    @patch("borrowings.serializers.create_stripe_session")
    @patch("borrowings.notifications.send_telegram_message")
    def test_return_book(self, mock_telegram, mock_stripe):
        self.book.inventory = 1
        self.book.save()

        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=date.today() + timedelta(days=3),
        )

        return_url = reverse("borrowings:borrowing-return-book", args=[borrowing.id])
        response = self.client.post(return_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        borrowing.refresh_from_db()
        self.assertIsNotNone(borrowing.actual_return_date)

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 2)
