"""
URL configurations for the books app.
Exposes endpoints:
- GET /POST /api/books/
- GET /PUT /PATCH /DELETE /api/books/{id}/
"""


from django.urls import path, include
from rest_framework.routers import DefaultRouter

from books.views import (
    BookViewSet,

)

router = DefaultRouter()

router.register("books", BookViewSet, basename="book")

app_name = "books"

urlpatterns = [
    path("", include(router.urls)),
]