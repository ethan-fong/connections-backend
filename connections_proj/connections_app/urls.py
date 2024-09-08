from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    ConnectionsGameViewSet,
    GetgameViewSet,
    SubmissionViewSet,
    WordViewSet
)

router = DefaultRouter()
router.register(r'connectionsgames', ConnectionsGameViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'words', WordViewSet)
router.register(r'getgame', GetgameViewSet, basename='connectionsjson')
router.register(r'submit', SubmissionViewSet, basename='app_analytics')


urlpatterns = [
    path('', include(router.urls)),  # Include router URLs
]