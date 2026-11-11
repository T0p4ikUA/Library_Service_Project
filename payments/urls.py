from django.urls import path, include
from rest_framework.routers import DefaultRouter
from payments.views import (
    PaymentViewSet,
    payment_success_view,
    payment_cancel_view,
)

router = DefaultRouter()
router.register("payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path("payments/success/", payment_success_view, name="payment-success"),
    path("payments/cancel/", payment_cancel_view, name="payment-cancel"),
    path("", include(router.urls)),
]
