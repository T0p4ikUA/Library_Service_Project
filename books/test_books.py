from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from books.models import Book


class BookModelTests(TestCase):
    def test_book_str(self):
        book = Book.objects.create(
            title="Test Book",
            author="John Smitt",
            cover=Book.CoverType.HARD,
            inventory=10,
            daily_fee=Decimal("1.50"),
        )
        self.assertEqual(str(book), "Test Book by John Smitt")


class UnauthenticatedBookApiTests(APITestCase):
    def setUp(self):
        self.book_url = reverse("books:book-list")
        self.book = Book.objects.create(
            title="Book 1",
            author="Author 1",
            cover=Book.CoverType.SOFT,
            inventory=5,
            daily_fee=Decimal("2.00"),
        )

    def test_auth_required_for_creation(self):
        payload = {
            "title": "New Book",
            "author": "New Author",
            "cover": "HARD",
            "inventory": 3,
            "daily_fee": "1.00",
        }
        response = self.client.post(self.book_url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_books(self):
        response = self.client.get(self.book_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class AdminBookApiTests(APITestCase):
    def setUp(self):
        self.book_url = reverse("books:book-list")
        self.user = get_user_model().objects.create_user(
            email="admin@test.com", password="password123", is_staff=True
        )
        self.client.force_authenticate(user=self.user)

    def test_create_book(self):
        payload = {
            "title": "Admin Book",
            "author": "Admin Author",
            "cover": "HARD",
            "inventory": 8,
            "daily_fee": "3.50",
        }
        response = self.client.post(self.book_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        exists = Book.objects.filter(title=payload["title"]).exists()
        self.assertTrue(exists)

    def test_negative_daily_fee_cannot_be_created(self):
        payload = {
            "title": "Negative Price Book",
            "author": "Author",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": "-1.50",
        }
        response = self.client.post(self.book_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("daily_fee", response.data)

    def test_negative_daily_feet_validation(self):
        from django.core.exceptions import ValidationError

        book = Book(
            title="Bad Book",
            author="Author",
            cover=Book.CoverType.HARD,
            inventory=5,
            daily_fee=Decimal("-0.50"),
        )
        with self.assertRaises(ValidationError):
            book.full_clean()
