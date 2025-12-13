from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentModeViewSet, PaymentAccountViewSet

router = DefaultRouter()
router.register("payment-modes", PaymentModeViewSet, basename="paymentmode")
router.register("payment-accounts", PaymentAccountViewSet, basename="paymentaccount")

urlpatterns = [
    path("api/", include(router.urls)),
]

