from django.contrib.auth import get_user
from django.db.models import Model
from django.http import HttpRequest
from django.http import JsonResponse
from django.views import View
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import ConnectionsGame
from .serializers import ConnectionsGameSerializer

class IsCourseOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow the instructor of the course or admin users to access it.
    """
    def has_object_permission(self, request: HttpRequest, view: View, obj: Model) -> bool:
        """Grant permission if the user is an admin or the instructor of the related course."""
        print("Request user:", request.user)
        print("Is superuser:", request.user.is_superuser)
        print("Object course instructor:", getattr(obj, 'course', None).instructor if hasattr(obj, 'course') else 'No course attribute')
        
        if request.user.is_superuser:
            return True  # Admins get full access

        # Check if obj has a course and if the user is the instructor of that course
        has_permission = hasattr(obj, "course") and obj.course.instructor == request.user
        print("Has permission:", has_permission)
        return has_permission

class InstructorGameViewSet(ModelViewSet):
    permission_classes = []
    queryset = ConnectionsGame.objects.all()
    serializer_class = ConnectionsGameSerializer

    def get_queryset(self):
        """Limit queryset so instructors only see games related to their courses."""
        if self.request.user.is_superuser:
            return ConnectionsGame.objects.all()  # Admins see all games
        return ConnectionsGame.objects.filter(course__instructor=self.request.user)  # Only instructor's games

    def destroy(self, request, *args, **kwargs):
        """Ensure the user has permission to delete the game."""
        instance = self.get_object()
        print("Request user:", request.user)
        print("Instance course instructor:", instance.course.instructor)
        if request.user != instance.course.instructor and not request.user.is_superuser:
            print("Permission denied for user:", request.user)
            return Response(
                {"status": "error", "message": "You do not have permission to delete this game."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().destroy(request, *args, **kwargs)

def check_authenticated(request):
    user = get_user(request)
    if user.is_authenticated:
        return JsonResponse({'authenticated': True, 'username': user.username})
    else:
        return JsonResponse({'authenticated': False}, status=401)