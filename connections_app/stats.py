import json

from collections import defaultdict

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ConnectionsGame, Category, Word, Submission

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
    
class AverageTimePerCategoryView(APIView):
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