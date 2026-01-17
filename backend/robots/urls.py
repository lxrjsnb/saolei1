from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RiskEventViewSet, RobotComponentViewSet, RobotGroupViewSet, dashboard

router = DefaultRouter()
router.register(r"groups", RobotGroupViewSet, basename="robot-group")
router.register(r"components", RobotComponentViewSet, basename="robot-component")
router.register(r"risk-events", RiskEventViewSet, basename="risk-event")

urlpatterns = [
    path("dashboard/", dashboard, name="robots-dashboard"),
    path("", include(router.urls)),
]
