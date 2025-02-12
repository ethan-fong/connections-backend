import random
from .models import ConnectionsGame

def generate_game_code() -> str:
    consonants = 'BCDFGHJKLMNPQRSTVWXYZ'  # All uppercase consonants
    while True:
        game_code = ''.join(random.choices(consonants, k=4))
        if not ConnectionsGame.objects.filter(game_code=game_code).exists():
            return game_code