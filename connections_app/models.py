from django.db import models

# Create your models here.
class ConnectionsGame(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=255, default="Unknown Author")  # New author field
    num_categories = models.IntegerField()
    words_per_category = models.IntegerField()

class Category(models.Model):
    related_game = models.ForeignKey(ConnectionsGame, on_delete=models.CASCADE, related_name='categories')
    category = models.CharField(max_length=255)
    difficulty = models.IntegerField()
    explanation = models.TextField(default="No explanation provided")
    is_py_code = models.JSONField(default=list)  # New field to store code snippets as a list

class Word(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='words')
    word = models.CharField(max_length=255)

class Submission(models.Model):
    game = models.ForeignKey(ConnectionsGame, on_delete=models.CASCADE)
    guesses = models.JSONField()  # Store as JSON for easy storage of arrays
    time_taken = models.JSONField()  # Store array of time taken for each guess
    is_won = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
