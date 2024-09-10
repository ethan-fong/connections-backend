from django.shortcuts import get_object_or_404
from django.db.utils import ProgrammingError
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import ConnectionsGame, Category, Word
from .serializers import ConnectionsGameSerializer, CategorySerializer, WordSerializer, SubmissionSerializer

class ConnectionsGameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ConnectionsGame.objects.all()
    serializer_class = ConnectionsGameSerializer
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

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class WordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer

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

        except ProgrammingError as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
