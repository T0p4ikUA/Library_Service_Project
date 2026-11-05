from django.urls import path, include
from rest_framework.routers import DefaultRouter

from library.views import (
    BookViewSet,
    UserViewSet,
    BorrowingViewSet,
    PaymentViewSet,
)

router = DefaultRouter()

router.register("books", BookViewSet, basename="book")
router.register("users", UserViewSet, basename="user")
router.register("borrowings", BorrowingViewSet, basename="borrow")
router.register("payments", PaymentViewSet, basename="payment")

app_name = "library"

urlpatterns = [
    path("", include(router.urls)),
]