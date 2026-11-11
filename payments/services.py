import stripe
from django.conf import settings
from django.urls import reverse

from borrowings.models import Borrowing
from payments.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(
    borrowing: Borrowing,
    request=None,
    amount=None,
    payment_type=Payment.TypeChoices.PAYMENT
) -> Payment:
    if amount is not None:
        total_amount = amount
        product_name = f"Fine for overdue: {borrowing.book.title}"
    else:
        total_days = (borrowing.expected_return_date - borrowing.borrow_date).days
        total_amount = borrowing.book.daily_fee * max(total_days, 1)
        product_name = f"Borrowing {borrowing.book.title}"

    if request:
        success_url = (
                request.build_absolute_uri(reverse("payments:success"))
                + "?session_id={CHECKOUT_SESSION_ID}"
        )
        cancel_url = request.build_absolute_uri(reverse("payments:cancel"))
    else:
        success_url = "http://127.0.0.1:8000/api/payments/success/?session_id={CHECKOUT_SESSION_ID}"
        cancel_url = "http://127.0.0.1:8000/api/payments/cancel/"

    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": product_name,
                    },
                    "unit_amount": int(total_amount * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )

    payment = Payment.objects.create(
        status=Payment.StatusChoices.PENDING,
        type=payment_type,
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=total_amount,
    )

    return payment
