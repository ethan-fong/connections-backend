import json
import random

from collections import defaultdict
from typing import List

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import ConnectionsGame, Category, Word, Submission
from .serializers import SubmissionSerializer, ConnectionsGameSerializer, UploadSerializer

class AdminUploadViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

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
            game = ConnectionsGame.objects.create(
                title=data['title'],
                game_code=unique_game_code,
                author=data['author'],
                syntax_highlighting=data['syntax_highlighting'],
                created_at=data['created_at'],
                num_categories=data['num_categories'],
                words_per_category=data['words_per_category']
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

class AdminGameViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = ConnectionsGame.objects.all()
    serializer_class = ConnectionsGameSerializer

class AdminSubmissionsViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

class GuessDistributionView(APIView):
    def get(self, request, game_code: str, *args, **kwargs):
        try:
            game = ConnectionsGame.objects.get(game_code=game_code)
        except ConnectionsGame.DoesNotExist:
            return Response({'status': 'error', 'message': 'Game not found for this code'}, status=status.HTTP_404_NOT_FOUND)

        # Fetch submissions for the specified game
        submissions = Submission.objects.filter(game=game)
        if not submissions:
            return Response({'status': 'error', 'message': 'Submissions not found for this game'}, status=status.HTTP_400_BAD_REQUEST)

        guess_distribution = self.get_guess_distribution(submissions)

        def convert_dict(d):
            return {str(k): v for k, v in d.items()}

        # Serialize to JSON
        json_data = json.dumps(convert_dict(guess_distribution))
        return Response(json_data)
    
    @staticmethod
    def get_guess_distribution(submissions):
        guess_distribution = defaultdict(int)
        
        for submission in submissions:
            guesses = submission.guesses
            for guess_group in guesses:
                guess_distribution[tuple(sorted(guess_group))] += 1
        return guess_distribution
    
class AverageTimePerCategory(APIView):
    def get(self, request, game_code: str, *args, **kwargs):
        try:
            # Fetch the game using the game code
            game = ConnectionsGame.objects.get(game_code=game_code)
        except ConnectionsGame.DoesNotExist:
            return Response({'status': 'error', 'message': 'Game not found for this code'}, status=status.HTTP_404_NOT_FOUND)

        # Fetch submissions for the specified game
        submissions = Submission.objects.filter(game=game)
        if not submissions:
            return Response({'status': 'error', 'message': 'Submissions not found for this game'}, status=status.HTTP_400_BAD_REQUEST)

        res = []
        categories_by_id = list(Category.objects.filter(related_game=game).values_list('pk', flat=True))
        for category in categories_by_id:
            # Fetch all words related to this category
            res.append(sorted(list(
                Word.objects.filter(category=category).values_list('word', flat=True)
            )))
        
        guess_distribution = self.get_guess_time_distribution(submissions, res)

        def convert_dict(d):
            return {str(k): v for k, v in d.items()}

        # Convert the dictionary
        json_out = {}
        json_out["guess distribution"] = convert_dict(guess_distribution)

        # Serialize to JSON
        json_data = json.dumps(json_out)  # Use json_out instead of guess_distribution
        return Response(json_data)

    @staticmethod
    def get_guess_time_distribution(submissions, correct_categories):
        # Dictionary to store total time and count of samples for each guess group
        guess_distribution = defaultdict(lambda: {'total_time': 0, 'count': 0})
        
        for submission in submissions:
            guesses = submission.guesses
            for guess_group in guesses:
                # Convert guess_group to a tuple and sort it for consistency
                sorted_group = sorted(guess_group)
                if sorted_group in correct_categories:
                    # Get the index of the guess group in the list
                    index = guesses.index(guess_group)
                    # Get the time taken for the current guess group
                    time_value = submission.time_taken[index]
                    # Update total time and count in the distribution
                    guess_distribution[tuple(sorted_group)]['total_time'] += time_value
                    guess_distribution[tuple(sorted_group)]['count'] += 1

        # Calculate average time for each guess group
        average_distribution = {}
        for group, values in guess_distribution.items():
            if values['count'] > 0:
                average_time = round(values['total_time'] / values['count'], 2)
            else:
                average_time = 0
            average_distribution[group] = (average_time, values['count'])
        return average_distribution

class SubmissionCountView(APIView):
    def get(self, request, game_code: str, *args, **kwargs):
        try:
            # Fetch the game using the game code
            game = ConnectionsGame.objects.get(game_code=game_code)
        except ConnectionsGame.DoesNotExist:
            return Response({'status': 'error', 'message': 'Game not found for this code'}, status=status.HTTP_404_NOT_FOUND)

        # Count submissions for the specified game
        submissions_count = Submission.objects.filter(game=game).count()
        wins_count = Submission.objects.filter(game=game, is_won=True).count()

        return Response({'submission_count': submissions_count, 'wins': wins_count}, status=status.HTTP_200_OK)

class UploadViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
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
            game = ConnectionsGame.objects.create(
                title=data.get('title', 'untitled game'),
                game_code=unique_game_code,
                author=data.get('author', 'unknown author'),
                syntax_highlighting=data['syntax_highlighting'],
                created_at=timezone.now(),
                num_categories=data['num_categories'],
                words_per_category=data['words_per_category']
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
