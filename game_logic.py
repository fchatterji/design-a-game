import random
import datetime

from score import Score 


def find_all_indexes(word, letter):
    """Return the indexes of all occurrences of a letter in a string."""
    return [index for index, character in enumerate(word) if character == letter]


def get_secret_word():
    """Return a secret word for the game."""
    words = ['cat', 'dog', 'duck', 'hen', 'horse', 'Supercalifragilisticexpialidocious']
    return random.choice(words).lower()


def end_game_and_save(user, game, won=False):
    # create and save the score
    score = Score(user=game.user,
                  date=datetime.date.today(),
                  won=won,
                  score=calculate_score(game.attempts_remaining, won=won))

    score.put()

    # update and save the user
    update_user_statistics(user, won=won)
    user.put()

    # update and save the game
    game.game_over = True
    game.put()


def calculate_score(attempts_remaining, won=False):
    # Calculate the score of the game
    if won:
        score = 10 + 5 * attempts_remaining
    else:
        score = 0

    return score


def update_user_statistics(user, won=False):
    # Update the statistics (wins, games played) of a user
    if won:
        user.wins += 1
        user.games_played += 1
    else:
        user.games_played += 1
