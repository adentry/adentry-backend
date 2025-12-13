from rest_framework import viewsets, permissions
from .models.payment import PaymentMode, PaymentAccount
from .serializers import PaymentModeSerializer, PaymentAccountSerializer

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow read for everyone (if you want), but write only for owner.
    For PaymentMode admin will restrict creation; here we assume PaymentMode is admin-managed.
    """

    def has_object_permission(self, request, view, obj):
        # PaymentMode is not owner-specific; PaymentAccount belongs to a user (we didn't add user field in PaymentAccount — if you do, check)
        return True  # implement owner checks if PaymentAccount has user field


class PaymentModeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentMode.objects.filter(active=True)
    serializer_class = PaymentModeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PaymentAccountViewSet(viewsets.ModelViewSet):
    queryset = PaymentAccount.objects.all()
    serializer_class = PaymentAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # restrict accounts to ones owned by current user if PaymentAccount has user (we didn't add user FK here)
        # If you added user FK, use: return PaymentAccount.objects.filter(user=self.request.user)
        return PaymentAccount.objects.all()

    def perform_create(self, serializer):
        # If PaymentAccount has a user field, attach current user here:
        # serializer.save(user=self.request.user)
        serializer.save()

