from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models

from library_service.settings import AUTH_USER_MODEL


class Book(models.Model):
    class CoverType(models.TextChoices):
        HARD = "HARD", "Hard"
        SOFT = "SOFT", "Soft"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        max_length=4,
        choices=CoverType.choices,
        default=CoverType.HARD,
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    def __str__(self):
        return f"{self.title} by {self.author}"


class User(AbstractUser):
    email = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.email}"


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrows",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrows",
    )

    def __str__(self):
        return (f"User {self.user.email} borrowed "
                f"{self.book.title} {self.borrow_date}")


class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"

    class PaymentType(models.TextChoices):
        PAYMENT = "PAYMENT", "Payment"
        FINE = "FINE", "Fine"

    status = models.CharField(
        max_length=7,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    type = models.CharField(
        max_length=7,
        choices=PaymentType.choices,
        default=PaymentType.PAYMENT,
    )
    borrowing = models.ForeignKey(
        Borrowing,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    session_url = models.URLField()
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    def __str__(self):
        return f"{self.type} - {self.status} (${self.money_to_pay})"
