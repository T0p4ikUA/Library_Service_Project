import stripe
from django.conf import settings
from django.http import JsonResponse
from payments.models import Payment

stripe.api_key = settings.STRIPE_API_KEY


def stripe_success_view(request):
    session_id = request.GET.get("success_id")

    if not session_id:
        return JsonResponse({"error": "no session_id provided"}, status=400)
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            payment = Payment.objects.filter(session_id=session_id).first()
            if payment:
                payment.status = Payment.StatusChoices.PAID
                payment.save()

            return JsonResponse(
                {"status": "success", "message": "Payment was successful!"}
            )
        else:
            return JsonResponse(
                {"status": "pending", "message": "Payment is not completed yet"}
            )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
