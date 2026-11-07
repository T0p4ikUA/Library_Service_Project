from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.serializers import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import(
    BorrowingReadSerializer,
    BorrowingCreateSerializer
)

class BorrowingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Borrowing.objects.all().select_related(
            "book",
            "user"
        )

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        user_id = self.request.query_params.get(
            "user_id"
        )
        is_active = self.request.query_params.get(
            "is_active"
        )

        if user_id and self.request.user.is_staff:
            queryset = queryset.filter(user_id=user_id)

        if is_active:
            is_active_bool = is_active.lower() == "true"
            if is_active_bool:
                queryset = queryset.filter(
                    actual_return_date__isnull=True
                )
            else:
                queryset = queryset.filter(
                    actual_return_date__isnull=False
                )
        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return BorrowingReadSerializer
        return BorrowingCreateSerializer

    def perform_create(self, serializer):
        book = serializer.validated_data["book"]

        with transaction.atomic():
            from books.models import Book
            plug = Book.objects.select_for_update().get(id=book.id)

            if plug.inventory < 1:
                raise ValidationError(
                    {"book": "There is no such book"}
                )

            plug.inventory = F("inventory") - 1
            plug.save()
            plug.refresh_from_db()

            borrowing = serializer.save(user=self.request.user)

        from borrowings.notifications import send_telegram_message
        message = (
            f"<b>New borrowing has been created!</b>\n\n"
            f"<b>User:</b> {borrowing.user.email}\n"
            f"<b>Title:</b> {borrowing.book.title}\n"
            f"<b>Expected return date:</b> {borrowing.expected_return_date}"
        )
        send_telegram_message(message)

    @action(
        detail=True,
        methods=["post"],
        url_path="return",
    )
    def return_book(self, request, pk):
        borrowing = self.get_object()

        if borrowing.actual_return_date is not None:
            return Response(
                {"error": "This book has been returned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            borrowing.actual_return_date = timezone.now().date()
            borrowing.save()

            from books.models import Book

            locked_book = Book.objects.select_for_update().get(id=borrowing.book.id)

            locked_book.inventory = F("inventory") + 1
            locked_book.save()
            locked_book.refresh_from_db()

        serializer = self.get_serializer(borrowing)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
