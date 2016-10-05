"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    games_played = ndb.IntegerProperty(default=0)
    wins = ndb.IntegerProperty(default=0)

    @property
    def win_ratio(self):
        if self.games_played > 0:
            return float(self.wins) / float(self.games_played)
        else:
            return float(0)

    def to_form(self):
        form = UserForm()
        form.name = self.name
        form.email = self.email
        form.games_played = self.games_played
        form.wins = self.wins
        form.win_ratio = self.win_ratio
        return form


class Game(ndb.Model):
    """Game object"""
    word = ndb.StringProperty(required=True)
    guessed_word = ndb.StringProperty(required=True)
    attempts_remaining = ndb.IntegerProperty(required=True, default=9)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    history = ndb.StringProperty(repeated=True)

    @classmethod
    def new_game(cls, user, attempts):
        """Creates and returns a new game"""

        # Sample word choice
        words = ['cat', 'dog', 'duck', 'hen', 'horse', 'Supercalifragilisticexpialidocious']
        word = random.choice(words)

        guessed_word = '*' * len(word)

        game = Game(user=user,
                    word=word,
                    guessed_word=guessed_word,
                    attempts_remaining=attempts)
        game.put()
        return game

    def to_form(self, message=""):
        """Return a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.attempts_remaining = self.attempts_remaining
        form.guessed_word = self.guessed_word
        form.game_over = self.game_over
        form.history = self.history
        form.message = message
        return form

    def to_history_form(self):
        """Return a GameForm representation of the Game"""
        form = GameHistoryForm()
        form.urlsafe_key = self.key.urlsafe()
        form.history = self.history
        return form

    def end_game(self, won=False):
        """End the game.

        If won is True, the player won. - if won is False, the player lost.
        """
        self.game_over = True
        self.put()

        # Calculate the score (ie the result) of the game
        if won:
            result = 10 + 5 * self.attempts_remaining
            user = self.user.get()
            user.wins += 1
            user.games_played += 1
            user.put()
        else:
            result = 0
            user = self.user.get()
            user.games_played += 1
            user.put()

        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=won,
                      score=result)
        score.put()


class Score(ndb.Model):
    """Score object."""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    score = ndb.IntegerProperty(required=True, default=0)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=str(self.date), score=self.score)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts_remaining = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)
    guessed_word = messages.StringField(6, required=True)
    history = messages.StringField(7, repeated=True)


class GameForms(messages.Message):
    """Return multiple GameForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    attempts = messages.IntegerField(4, default=9)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    guess = messages.StringField(1, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    score = messages.IntegerField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


class UserForm(messages.Message):
    """User Form"""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2)
    games_played = messages.IntegerField(3, default=0)
    wins = messages.IntegerField(4, default=0)
    win_ratio = messages.FloatField(5, default=0.0)


class UserForms(messages.Message):
    """Return multiple User Forms """
    items = messages.MessageField(UserForm, 1, repeated=True)


class GameHistoryForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    history = messages.StringField(2, repeated=True)
