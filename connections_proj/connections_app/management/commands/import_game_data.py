import json
from django.core.management.base import BaseCommand
from connections_app.models import ConnectionsGame, Category, Word

class Command(BaseCommand):
    help = 'Load game data from a JSON file into the database'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']
        with open(json_file, 'r') as file:
            data = json.load(file)

        # Create ConnectionsGame
        game = ConnectionsGame.objects.create(
            title=data['title'],
            author=data['author'],
            created_at=data['created_at'],
            num_categories=data['num_categories'],
            words_per_category=data['words_per_category']
        )

        for category_data in data['game']:
            # Create Category
            category = Category.objects.create(
                related_game=game,
                category=category_data['category'],
                difficulty=category_data['difficulty'],
                explanation=category_data['explanation'],
                is_py_code=category_data['is_py_code']
            )

            # Create Words
            for word in category_data['words']:
                Word.objects.create(
                    category=category,
                    word=word
                )

        self.stdout.write(self.style.SUCCESS('Successfully imported game data'))