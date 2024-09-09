from django.contrib import admin
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from django.db.utils import ProgrammingError
from rest_framework.response import Response
from .models import ConnectionsGame, Category, Word, Submission
from .serializers import SubmissionSerializer, ConnectionsGameSerializer
from rest_framework import viewsets

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
