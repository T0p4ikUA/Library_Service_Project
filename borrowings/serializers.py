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

    def validate(self, data):
        borrow_date = data.get("borrow_date")
        expected_return_date = data.get("expected_return_date")

        if borrow_date and expected_return_date and expected_return_date < borrow_date:
            raise serializers.ValidationError(
                {
                    "expected_return_date": "Expected return date is before borrow date",
                }
            )
        return data
