import json
import random

from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import ConnectionsGame, Category, Word, Submission, Course
from .serializers import SubmissionSerializer, ConnectionsGameSerializer, UploadSerializer, CourseSerializer
from rest_framework.decorators import action

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

class UploadViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = UploadSerializer
    parser_classes = [MultiPartParser]  # To handle file uploads via multipart

    # GET request to show the visual interface
    def list(self, request):
        return Response("Upload your connections game here! Only .json file uploads are supported.")

    # PUT request to handle the file upload
    def create(self, request):
        serializer = UploadSerializer(data=request.data)
        if serializer.is_valid():
            file_uploaded = request.FILES.get('file_uploaded')
            content_type = file_uploaded.content_type

            # Check if the uploaded file is JSON
            if content_type == 'application/json':
                try:
                    # Try to parse the uploaded file as JSON
                    json_data = json.load(file_uploaded)
                    
                    # Call the update_database function (you will need to implement this)
                    game_code = self.update_database(json_data)

                    return Response(
                        {'status': 'success', 'message': f'Database updated successfully! Your game code is: {game_code}'},
                        status=status.HTTP_201_CREATED
                    )
                except json.JSONDecodeError:
                    return Response({'status': 'error', 'message': 'Invalid JSON file.'}, status=status.HTTP_400_BAD_REQUEST)
                except ValidationError as e:
                    return Response({'status': 'error', 'message': f'Database error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({'status': 'error', 'message': 'Uploaded file must be a JSON file.'}, status=status.HTTP_400_BAD_REQUEST)

            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update_database(self, data) -> str:
        unique_game_code = self.generate_game_code()
        try:
            course_name = data['course'].strip().lower()
            course = Course.objects.get(name__iexact=course_name)
            game = ConnectionsGame.objects.create(
                title=data.get('title', 'untitled game'),
                game_code=unique_game_code,
                author=data.get('author', 'unknown author'),
                syntax_highlighting=data['syntax_highlighting'],
                num_categories=data['num_categories'],
                words_per_category=data['words_per_category'],
                course=course,
                published=True,
                related_info=data['related_info']  # Added related_info field
            )

            for category_data in data['game']:
                category = Category.objects.create(
                    related_game=game,
                    category=category_data['category'],
                    difficulty=category_data['difficulty'],
                    explanation=category_data['explanation']
                )

                for word in category_data['words']:
                    Word.objects.create(
                        category=category,
                        word=word
                    )
        except Exception as e:
            raise e
        return unique_game_code
    
    @staticmethod
    def generate_game_code() -> str:
        consonants = 'BCDFGHJKLMNPQRSTVWXYZ'  # All uppercase consonants
        while True:
            game_code = ''.join(random.choices(consonants, k=4))
            if not ConnectionsGame.objects.filter(game_code=game_code).exists():
                return game_code

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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list_games(self, request, course_id=None):
        try:
            course = Course.objects.get(id=course_id)
            games = ConnectionsGame.objects.filter(course=course)
            page = self.paginate_queryset(games)
            if page is not None:
                serializer = ConnectionsGameSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = ConnectionsGameSerializer(games, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({'status': 'error', 'message': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
