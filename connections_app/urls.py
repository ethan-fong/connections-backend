from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    ConnectionsGameViewSet,
    ConnectionsGameByCodeViewSet,
    SubmissionViewSet,
    WordViewSet,
    CourseGamesViewSet,
    PublicUploadViewSet
)

from .admin import (
    UploadViewSet,
    AdminGameViewSet,
    AdminSubmissionsViewSet,
    PublishGameViewSet,
    AdminCourseViewSet,
    AssignGameToCourseViewSet
)

from .stats import (
    GuessDistributionView,
    AverageTimePerCategoryView,
    SubmissionCountView
)

api_router = DefaultRouter()
api_router.register(r'courses', CourseGamesViewSet, basename="course_games")
api_router.register(r'connectionsgames', ConnectionsGameViewSet)
api_router.register(r'upload', PublicUploadViewSet, basename='public_upload')
api_router.register(r'categories', CategoryViewSet)
api_router.register(r'words', WordViewSet)
api_router.register(r'submit-stats', SubmissionViewSet, basename='app_submit')
api_router.register(r'games/code/(?P<game_code>[^/.]+)', ConnectionsGameByCodeViewSet, basename='game-code-detail')

admin_router = DefaultRouter()
admin_router.register(r'create', UploadViewSet, basename='admin_create')
admin_router.register(r'games', AdminGameViewSet, basename='admin_games')
admin_router.register(r'listsubmissions', AdminSubmissionsViewSet, basename='admin_submissions')
admin_router.register(r'publish', PublishGameViewSet, basename='admin_publish')
admin_router.register(r'courses', AdminCourseViewSet, basename='admin_courses')
admin_router.register(r'assign', AssignGameToCourseViewSet, basename='admin_assign')

urlpatterns = [
    path('api/', include(api_router.urls)),
    path('admin-tools/', include(admin_router.urls)),
    path('stats/guessdist/<str:game_code>/', GuessDistributionView.as_view(), name='guess_distribution'),
    path('stats/timedist/<str:game_code>/', AverageTimePerCategoryView.as_view(), name='average_time_per_category'),
    path('stats/count/<str:game_code>/', SubmissionCountView.as_view(), name='submission_count'),
]