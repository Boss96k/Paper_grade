from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()
# Viewsets will be registered here in Phase 2+ (e.g. PredictionViewSet, RecommendationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
