from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payments.views import (
    PaymentViewSet,
    payment_cancel_view,
    payment_success_view,
)

router = DefaultRouter()
router.register("", PaymentViewSet, basename="payment")

urlpatterns = [
    path("success/", payment_success_view, name="success"),
    path("cancel/", payment_cancel_view, name="cancel"),
    path("", include(router.urls)),
]

app_name = "payments"
