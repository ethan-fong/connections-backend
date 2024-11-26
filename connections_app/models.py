import random

from django.db import models

class ConnectionsGame(models.Model):
    title = models.CharField(max_length=255)
    game_code = models.CharField(max_length=4, unique=True)  # Ensure this field is unique
    created_at = models.DateTimeField(auto_now_add=True)
    # New field for syntax highlighting
    syntax_highlighting = models.CharField(max_length=20, choices=[
        ('python', 'Python'),
        ('java', 'Java'),
        ('c', 'C'),
        ('none', 'None')
    ], default='python')  # Default to 'python'
    author = models.CharField(max_length=255, default="Unknown Author")  # New author field
    num_categories = models.IntegerField()
    words_per_category = models.IntegerField()

class Category(models.Model):
    related_game = models.ForeignKey(ConnectionsGame, on_delete=models.CASCADE, related_name='categories')
    category = models.CharField(max_length=255)
    difficulty = models.IntegerField()
    explanation = models.TextField(default="No explanation provided")

class Word(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='words')
    word = models.CharField(max_length=255)

class Submission(models.Model):
    game = models.ForeignKey(ConnectionsGame, on_delete=models.CASCADE)
    guesses = models.JSONField()  # Store as JSON for easy storage of arrays
    time_taken = models.JSONField()  # Store array of time taken for each guess
    is_won = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
