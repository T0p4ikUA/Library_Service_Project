import stripe
from django.conf import settings
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from payments.models import Payment
from payments.serializers import PaymentSerializer

stripe.api_key = settings.STRIPE_API_KEY


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Payment.objects.select_related("borrowing")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(borrowing__user=self.request.user)


@api_view(["GET"])
def payment_success_view(request):
    session_id = request.GET.get("session_id")
    if not session_id:
        return Response(
            {"error": "Session ID is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        payment = Payment.objects.filter(session_id=session_id).first()

        if not payment:
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if session.payment_status == "paid":
            payment.status = Payment.StatusChoices.PAID
            payment.save()
            return Response(
                {"message": "Payment successful!", "payment_id": payment.id},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"message": "Payment not completed yet"}, status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def payment_cancel_view(request):
    return Response(
        {
            "message": "Payment was canceled. You can complete it later("
            "session is active for 24h)."
        },
        status=status.HTTP_200_OK,
    )
