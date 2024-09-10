"""
URL configuration for connections_proj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from connections_app.admin import (
    AdminUploadViewSet,
    AdminGameViewSet,
    AdminSubmissionsViewSet,
    GuessDistributionView,
    AverageTimePerCategory,
    SubmissionCountView
)

admin_router=DefaultRouter()
admin_router.register(r'upload', AdminUploadViewSet, basename='admin_upload')
admin_router.register(r'games', AdminGameViewSet, basename='admin_games')
admin_router.register(r'listsubmissions', AdminSubmissionsViewSet, basename='admin_submissions')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-tools/', include(admin_router.urls)),
    path('api/', include('connections_app.urls')),
    path('guessdist/<int:gameid>/', GuessDistributionView.as_view()),
    path('timedist/<int:gameid>/', AverageTimePerCategory.as_view()),
    path('count/<int:gameid>/', SubmissionCountView.as_view())
]
