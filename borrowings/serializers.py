from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing
from payments.serializers import PaymentSerializer
from payments.services import create_stripe_session


class BorrowingReadSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        )

    def create(self, validated_data):
        borrowing = super().create(validated_data)
        request = self.context.get("request")
        create_stripe_session(borrowing, request=request)

        return borrowing
