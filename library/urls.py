from django.urls import path, include
from rest_framework.routers import DefaultRouter

from library.views import (
    BookViewSet,

)

router = DefaultRouter()

router.register("books", BookViewSet, basename="book")

app_name = "library"

urlpatterns = [
    path("", include(router.urls)),
]