from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payments.views import (
    PaymentViewSet,
    payment_cancel_view,
    payment_success_view,
)

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path("payments/success/", payment_success_view, name="payment-success"),
    path("payments/cancel/", payment_cancel_view, name="payment-cancel"),
    path("", include(router.urls)),
]

app_name = "payments"
