from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    ConnectionsGameViewSet,
    SubmissionViewSet,
    WordViewSet
)

router = DefaultRouter()
router.register(r'connectionsgames', ConnectionsGameViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'words', WordViewSet)
router.register(r'submit-stats', SubmissionViewSet, basename='app_submit')

urlpatterns = [
    path('', include(router.urls)),  # Include router URLs
    path('games/code/<str:game_code>/', ConnectionsGameViewSet.as_view({'get': 'retrieve'}), name='game-code-detail'),
]