from rest_framework import serializers
from .models import ConnectionsGame, Category, Word, Submission
from .models import Course
from django.contrib.auth import get_user_model

User = get_user_model()

class InstructorSerializer(serializers.ModelSerializer):
    """Serializer for displaying instructor details in the CourseSerializer."""
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]  # Adjust fields as needed

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ['word']

class CategorySerializer(serializers.ModelSerializer):
    words = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['category', 'words', 'difficulty', 'explanation']

    def get_words(self, obj):
        # Return list of words for the category
        return [word.word for word in obj.words.all()]

class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),  # Allows setting instructor via ID
        required=True  # Ensures instructor must be specified
    )
    class Meta:
        model = Course
        fields = ['id', 'name', 'instructor', 'description']  # Replace with actual fields from the Course model

class ConnectionsGameSerializer(serializers.ModelSerializer):
    game = CategorySerializer(many=True, source='categories')
    course = CourseSerializer()

    class Meta:
        model = ConnectionsGame
        fields = ['id',
                  'game_code',
                  'title',
                  'published',
                  'syntax_highlighting',
                  'created_at',
                  'author',
                  'max_mistakes',
                  'num_categories',
                  'words_per_category',
                  'course',
                  'relevant_info',
                  'game']

class SubmissionSerializer(serializers.ModelSerializer):
    game = serializers.PrimaryKeyRelatedField(queryset=ConnectionsGame.objects.all())

    class Meta:
        model = Submission
        fields = ['id', 'game', 'guesses', 'time_taken', 'is_won', 'submitted_at']

class UploadSerializer(serializers.Serializer):
    file_uploaded = serializers.FileField()
