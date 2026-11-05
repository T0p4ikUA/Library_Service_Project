from django.contrib import admin
from library.models import (
    Book,
    User,
    Borrowing,
    Payment,
)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "cover",
        "inventory",
        "daily_fee",
    ]
    search_fields = ["title", "author",]
    list_filter = ["cover",]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "first_name", "last_name",]
    search_fields = ["email", "first_name", "last_name",]


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = [
        "borrow_date",
        "expected_return_date",
        "actual_return_date",
        "book",
        "user",
    ]
    search_fields = ["user__email", "book__title"]
    autocomplete_fields = ["book", "user"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "status",
        "type",
        "borrowing",
        "session_url",
        "session_id",
        "money_to_pay",
    ]
    list_filter = ["status", "type"]
    autocomplete_fields = ["borrowing"]

