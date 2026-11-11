"""
URL configurations for the borrowings app.
Exposes endpoints:
- GET /POST /api/borrowings/
- GET /PUT /DELETE /api/borrowings/{id}/
- POST /api/borrowings/{id}/return/
"""

from rest_framework.routers import DefaultRouter
from borrowings.views import BorrowingViewSet

router = DefaultRouter()
router.register("", BorrowingViewSet, basename="borrowing")

app_name = "borrowings"

urlpatterns = router.urls
