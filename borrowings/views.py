from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.serializers import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from books.models import Book
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
        user_id = self.request.query_params.get(
            "user_id"
        )
        is_active = self.request.query_params.get(
            "is_active"
        )

        if user_id:
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

        with (transaction.atomic()):
            from books.models import Book
            plug = Book.objects.select_for_update(
            ).get(id=book.id)

            if plug.inventory < 1:
                raise ValidationError(
                    {"book": "There is no such book"}
                )

            plug.inventory = F("inventory") - 1
            plug.save()
            plug.refresh_from_db()

            serializer.save(uesr=self.request.user)

    @action(
        detail=True,
        methods=["post"],
        url_path="return",
    )
    def return_book(self, request, pk):
        borrowing = self.get_object()

        if borrowing.actual_return_date is not None:
            return Response(
                {"error":"This book has been returned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with (transaction.atomic()):
            borrowing.actual_return_date = timezone.now(
            ).date()
            borrowing.save()

            book = borrowing.book
            book.inventory = F("inventory") + 1
            book.save()
            book.refresh_from_db()
        serializer = self.get_serializer(borrowing)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
