import random

from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import ConnectionsGame, Category, Word, Course
from .serializers import (
    CategorySerializer,
    ConnectionsGameSerializer,
    CourseSerializer,
    SubmissionSerializer,
    WordSerializer
)
from rest_framework.pagination import PageNumberPagination

class ConnectionsGamePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ConnectionsGameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ConnectionsGame.objects.all()
    serializer_class = ConnectionsGameSerializer
    pagination_class = ConnectionsGamePagination

class ConnectionsGameByCodeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConnectionsGameSerializer

    def get_queryset(self):
        game_code = self.kwargs.get('game_code')
        if game_code:
            return ConnectionsGame.objects.filter(game_code=game_code)
        else:
            return ConnectionsGame.objects.none()

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        game = get_object_or_404(queryset)
        serializer = self.get_serializer(game)
        return Response(serializer.data)

class CategoryPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CategoryPagination

class WordPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class WordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    pagination_class = WordPagination

class SubmissionViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for handling game submissions.
    """
    def create(self, request):
        try:
            data = request.data  # Data will already be parsed by DRF
            submitted_guesses = data.get('submittedGuesses', [])
            time_to_guess = data.get('timeToGuess', [])
            is_game_won = data.get('isGameWon', False)

            # Use game code to retrieve the game
            game_code = data.get('gameCode')  # Change from 'gameId' to 'gameCode'
            game = get_object_or_404(ConnectionsGame, game_code=game_code)  # Fetch game by game code

            # Save submission to the database using a serializer
            serializer = SubmissionSerializer(data={
                'game': game.id,
                'guesses': submitted_guesses,
                'time_taken': time_to_guess,
                'is_won': is_game_won
            })

            if serializer.is_valid():
                serializer.save()
                return Response({'status': 'success', 'message': 'Submission successful!'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class CoursePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePagination

    def get_queryset(self):
        return Course.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CourseGamesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CourseSerializer

    def get_queryset(self):
        return Course.objects.all()

    def list(self, request):
        courses = self.get_queryset()
        response_data = []

        for course in courses:
            course_data = CourseSerializer(course).data
            games = ConnectionsGame.objects.filter(course=course)
            course_data['games'] = ConnectionsGameSerializer(games, many=True).data
            response_data.append(course_data)

        return Response(response_data)
            
class PublicUploadViewSet(viewsets.ViewSet):
    def create(self, request):
        try:
            data = request.data  # Data will already be parsed by DRF

            # Recursively update the database
            self.update_database(data)

            # Recursively update the database with parsed data
            game_code = self.update_database(data)

            return Response({'status': 'success', 'message': f'Database updated successfully! Your game code is: {game_code}'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update_database(self, data) -> str:
        unique_game_code = self.generate_game_code()
        try:
            course_name = data.get('course', 'unassigned').strip().lower()
            course, _ = Course.objects.get_or_create(name__iexact=course_name)
            game = ConnectionsGame.objects.create(
                title=data['title'],
                game_code=unique_game_code,
                author=data['author'],
                syntax_highlighting=data['syntax_highlighting'],
                num_categories=data['num_categories'],
                words_per_category=data['words_per_category'],
                course=course,
                relevant_info=data.get('relevant_info', "")
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