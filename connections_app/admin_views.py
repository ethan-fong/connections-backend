from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import ConnectionsGame, Submission, Course
from .serializers import SubmissionSerializer, ConnectionsGameSerializer, CourseSerializer

User = get_user_model()

class AdminGameViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = ConnectionsGame.objects.all()
    serializer_class = ConnectionsGameSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        game_code = self.request.query_params.get('game_code', None)
        if game_code:
            queryset = queryset.filter(game_code=game_code)
        return queryset

    def destroy(self, request, *args, **kwargs):
        game_code = self.request.query_params.get('game_code', None)
        if game_code:
            try:
                game = ConnectionsGame.objects.get(game_code=game_code)
                game.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ConnectionsGame.DoesNotExist:
                return Response({'status': 'error', 'message': 'Game not found.'}, status=status.HTTP_404_NOT_FOUND)
        return super().destroy(request, *args, **kwargs)

class AdminSubmissionsViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

class PublishGameViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]
    
    def update(self, request, game_code=None, pk=None):
        try:
            game_code = game_code or pk
            game = ConnectionsGame.objects.get(game_code=game_code)
            game.published = not game.published
            game.save()
            return Response({'status': 'success', 'message': f'Game {game_code} publish status toggled to {game.published}'}, status=status.HTTP_200_OK)
        except ConnectionsGame.DoesNotExist:
            return Response({'status': 'error', 'message': 'Game not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class AdminCourseViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def create(self, request, *args, **kwargs):
        """Allow admins to create a course and specify an instructor."""
        instructor_id = request.data.get("instructor")

        if not instructor_id:
            return Response(
                {"status": "error", "message": "Instructor is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            instructor = User.objects.get(id=instructor_id)
        except User.DoesNotExist:
            return Response(
                {"status": "error", "message": "Instructor not found."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Assign the instructor before saving
        serializer.save(instructor=instructor)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Allow admin to delete a course."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list_games(self, request, course_id=None):
        """List all games associated with a course."""
        course = get_object_or_404(Course, id=course_id)
        games = ConnectionsGame.objects.filter(course=course)
        serializer = ConnectionsGameSerializer(games, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def list_instructor(self, request, course_id=None):
        """Retrieve the instructor of a course."""
        course = get_object_or_404(Course, id=course_id)
        instructor = course.instructor  # Since it's a ForeignKey, it returns a single user
        instructor_data = {
            'id': instructor.id,
            'username': instructor.username,
            'email': instructor.email,
            'full_name': f"{instructor.first_name} {instructor.last_name}".strip()
        }
        return Response(instructor_data, status=status.HTTP_200_OK)

class AssignGameToCourseViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    def update(self, request, pk=None):
        try:
            game_code = pk
            if not request.data:
                return Response({'status': 'error', 'message': 'No data provided.'}, status=status.HTTP_400_BAD_REQUEST)
            if isinstance(request.data, str):
                course_name = request.data.strip().lower()
            else:
                course_name = request.data.get('course') or request.data.get('name')
                if course_name:
                    course_name = course_name.strip().lower()

            if not course_name:
                return Response({'status': 'error', 'message': 'course_name is required.'}, status=status.HTTP_400_BAD_REQUEST)

            game = ConnectionsGame.objects.get(game_code=game_code)
            course = Course.objects.get(name__iexact=course_name)

            game.course = course
            game.save()

            serializer = ConnectionsGameSerializer(game)
            return Response({'status': 'success', 'message': f'Game {game_code} assigned to course {course_name}', 'game': serializer.data}, status=status.HTTP_200_OK)
        except ConnectionsGame.DoesNotExist:
            return Response({'status': 'error', 'message': 'Game not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Course.DoesNotExist:
            return Response({'status': 'error', 'message': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
