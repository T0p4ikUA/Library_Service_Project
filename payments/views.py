from payments.models import Payment
from payments.serializers import PaymentSerializer
from rest_framework import viewsets, permissions

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
         queryset = Payment.objects.select_related("borrowing")
         if self.request.user.is_staff:
             return queryset
         return queryset.filter(borrowing__user=self.request.user)
