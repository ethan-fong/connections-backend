from django.shortcuts import get_object_or_404
from django.db.utils import ProgrammingError
from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import ConnectionsGame, Category, Word
from .serializers import ConnectionsGameSerializer, CategorySerializer, WordSerializer, SubmissionSerializer

class ConnectionsGameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ConnectionsGame.objects.all()
    serializer_class = ConnectionsGameSerializer

    def retrieve(self, request, pk=None, game_code=None):
        if pk is None and game_code is None:
            # Handle the case where neither `pk` nor `game_code` is provided
            return Response({"error": "Either Game ID or Game Code is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if game_code:
                # Attempt to find the game by game code
                game = ConnectionsGame.objects.get(game_code=game_code)
            else:
                # Fallback to find by primary key
                game = ConnectionsGame.objects.get(pk=pk)
        except ConnectionsGame.DoesNotExist:
            return Response({"error": "Game not found"}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the game data
        serializer = ConnectionsGameSerializer(game)
        return Response(serializer.data)

    # Optionally, you may want to override the get_object method
    def get_object(self):
        # Override this method to handle both pk and game_code
        try:
            if self.kwargs.get('game_code'):
                return ConnectionsGame.objects.get(game_code=self.kwargs['game_code'])
            else:
                return super().get_object()
        except ConnectionsGame.DoesNotExist:
            raise Http404

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
