import json

from collections import defaultdict
from typing import List

from django.contrib import admin
from django.db.utils import ProgrammingError
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import ConnectionsGame, Category, Word, Submission
from .serializers import SubmissionSerializer, ConnectionsGameSerializer

# Register your models here.
class AdminUploadViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    def create(self, request):
        try:
            data = request.data  # Data will already be parsed by DRF

            # Recursively update the database
            self.update_database(data)

            return Response({'status': 'success', 'message': 'Database updated successfully!'}, status=status.HTTP_200_OK)

        except ProgrammingError as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update_database(self, data):
        try:
            # Implement your logic to update the database recursively using the data from the JSON request
            # You can access the models and serializers defined in your views.py file

            # Example:
            game = ConnectionsGame.objects.using('admin').create(
                title=data['title'],
                author=data['author'],
                created_at=data['created_at'],
                num_categories=data['num_categories'],
                words_per_category=data['words_per_category']
            )

            for category_data in data['game']:
                category = Category.objects.using('admin').create(
                    related_game=game,
                    category=category_data['category'],
                    difficulty=category_data['difficulty'],
                    explanation=category_data['explanation'],
                    is_py_code=category_data['is_py_code']
                )

                for word in category_data['words']:
                    Word.objects.using('admin').create(
                        category=category,
                        word=word
                    )
        except ProgrammingError as e:
            raise e

class AdminGameViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = ConnectionsGame.objects.all()
    serializer_class = ConnectionsGameSerializer

class AdminSubmissionsViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

class GuessDistributionView(APIView):
    def get(self, request, gameid: int, *args, **kwargs):
        submissions = Submission.objects.filter(game=gameid)  # Fetch submissions for the specified game ID
        if not submissions:
            return Response({'status': 'error', 'message': 'Submissions not found for this game'}, status=status.HTTP_400_BAD_REQUEST)
        #print(f"submissions: {submissions}")
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
    def get(self, request, gameid: int, *args, **kwargs):
        submissions = Submission.objects.filter(game=gameid)  # Fetch submissions for the specified game ID
        if not submissions:
            return Response({'status': 'error', 'message': 'Submissions not found for this game'}, status=status.HTTP_400_BAD_REQUEST)
        res = []
        ConnectionsGame.objects.get(id=gameid)
        categories_by_id = list(Category.objects.filter(related_game_id=gameid).values_list('pk', flat=True))
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
        json_data = json.dumps(convert_dict(guess_distribution))
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
    def get(self, request, gameid:int, *args, **kwargs):
        submissions = Submission.objects.filter(game=gameid).count()
        wins = Submission.objects.filter(game=gameid).filter(is_won=True).count()
        return Response({'submission_count': submissions, 'wins': wins}, status=status.HTTP_200_OK)
