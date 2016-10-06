"""models.py.

This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game').
"""

from protorpc import messages
from google.appengine.ext import ndb
from game_logic import get_secret_word


class Game(ndb.Model):
    """Game object."""

    secret_word = ndb.StringProperty(required=True)
    guessed_word = ndb.StringProperty(required=True)
    attempts_remaining = ndb.IntegerProperty(required=True, default=9)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    history = ndb.StringProperty(repeated=True)

    @classmethod
    def new_game(cls, user, attempts):
        """Create and return a new game."""
        secret_word = get_secret_word()

        guessed_word = '*' * len(secret_word)

        game = Game(user=user,
                    secret_word=secret_word,
                    guessed_word=guessed_word,
                    attempts_remaining=attempts)
        game.put()
        return game

    def to_form(self, message=""):
        """Return a form representation of the Game."""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.attempts_remaining = self.attempts_remaining
        form.guessed_word = self.guessed_word
        form.secret_word = self.secret_word
        form.game_over = self.game_over
        form.history = self.history
        form.message = message
        return form

    def to_history_form(self):
        """Return a form representation of the history of the game."""
        form = GameHistoryForm()
        form.urlsafe_key = self.key.urlsafe()
        form.history = self.history
        return form


class GameForm(messages.Message):
    """GameForm for outbound game state information."""

    urlsafe_key = messages.StringField(1, required=True)
    attempts_remaining = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)
    guessed_word = messages.StringField(6, required=True)
    secret_word = messages.StringField(8, required=True)
    history = messages.StringField(7, repeated=True)


class GameForms(messages.Message):
    """Return multiple GameForms."""

    items = messages.MessageField(GameForm, 1, repeated=True)


class NewGameForm(messages.Message):
    """Form to create a new game."""

    user_name = messages.StringField(1, required=True)
    attempts = messages.IntegerField(4, default=9)


class GameHistoryForm(messages.Message):
    """GameForm for outbound game history information."""

    urlsafe_key = messages.StringField(1, required=True)
    history = messages.StringField(2, repeated=True)


class MakeMoveForm(messages.Message):
    """Form to make a move in an existing game."""

    guess = messages.StringField(1, required=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message."""

    message = messages.StringField(1, required=True)
