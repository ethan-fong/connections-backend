from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import ConnectionsGame, Category, Word
from .serializers import ConnectionsGameSerializer, CategorySerializer, WordSerializer, SubmissionSerializer
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import JSONParser

class ConnectionsGameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ConnectionsGame.objects.all()
    serializer_class = ConnectionsGameSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class WordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer

class AdminUploadViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    def create(self, request):
        try:
            # Parse the JSON file from the request
            json_file = request.FILES.get('json_file')
            data = JSONParser().parse(json_file)

            # Recursively update the database
            self.update_database(data)

            return Response({'status': 'success', 'message': 'Database updated successfully!'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update_database(self, data):
        # Implement your logic to update the database recursively using the data from the JSON file
        # You can access the models and serializers defined in your views.py file

        # Example:
        game = ConnectionsGame.objects.create(
            title=data['title'],
            author=data['author'],
            created_at=data['created_at'],
            num_categories=data['num_categories'],
            words_per_category=data['words_per_category']
        )

        for category_data in data['game']:
            category = Category.objects.create(
                related_game=game,
                category=category_data['category'],
                difficulty=category_data['difficulty'],
                explanation=category_data['explanation'],
                is_py_code=category_data['is_py_code']
            )

            for word in category_data['words']:
                Word.objects.create(
                    category=category,
                    word=word
                )

class GetgameViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        if pk is None:
            # Handle the case where no `pk` is provided
            return Response({"error": "Game ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            game = ConnectionsGame.objects.get(pk=pk)
        except ConnectionsGame.DoesNotExist:
            return Response({"error": "Game not found"}, status=status.HTTP_404_NOT_FOUND)
        # Serialize the game data
        serializer = ConnectionsGameSerializer(game)
        return Response(serializer.data)

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

            # Example: You could link this submission to a game if needed
            game_id = data.get('gameId')
            game = get_object_or_404(ConnectionsGame, id=game_id)

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