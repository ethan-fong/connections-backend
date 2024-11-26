from django.core.management.base import BaseCommand
from connections_app.models import ConnectionsGame, Category, Word 

class Command(BaseCommand):
    help = 'Remove a ConnectionsGame and its related categories and words from the database by ID'

    def add_arguments(self, parser):
        parser.add_argument('game_id', type=int, help='The ID of the ConnectionsGame to remove')

    def handle(self, *args, **kwargs):
        game_id = kwargs['game_id']
        try:
            # Fetch the ConnectionsGame instance
            game = ConnectionsGame.objects.get(pk=game_id)
            
            # Fetch and delete related words
            categories = Category.objects.filter(related_game=game)
            for category in categories:
                words = Word.objects.filter(category=category)
                words.delete()
                
            # Delete the categories
            categories.delete()
            
            # Finally, delete the ConnectionsGame
            game.delete()
            
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted ConnectionsGame with ID {game_id} and its related categories and words'))
        except ConnectionsGame.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'ConnectionsGame with ID {game_id} does not exist'))
