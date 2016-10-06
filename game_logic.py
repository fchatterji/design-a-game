import random


def find_all_indexes(word, letter):
    """Return the indexes of all occurrences of a letter in a string."""
    return [index for index, character in enumerate(word) if character == letter]


def get_secret_word():
    """Return a secret word for the game."""
    words = ['cat', 'dog', 'duck', 'hen', 'horse', 'Supercalifragilisticexpialidocious']
    return random.choice(words).lower()


def calculate_score(attempts_remaining, won=False):
    # Calculate the score of the game
    if won:
        score = 10 + 5 * attempts_remaining
    else:
        score = 0

    return score
    """Create and save a new score instance
    score = Score(user=self.user, date=date.today(), won=won,
                  score=score)
                  score.put()"""


def update_user(user, won=False):

    if won:
        user.wins += 1
        user.games_played += 1
        user.put()
    else:
        user.games_played += 1
        user.put()
