from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile."""

    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    games_played = ndb.IntegerProperty(default=0)
    wins = ndb.IntegerProperty(default=0)

    @property
    def win_ratio(self):
        """Calculate the win ratio of a user."""
        if self.games_played > 0:
            return float(self.wins) / float(self.games_played)
        else:
            return float(0)

    def to_form(self):
        """Convert the user model to a user form."""
        form = UserForm()
        form.name = self.name
        form.email = self.email
        form.games_played = self.games_played
        form.wins = self.wins
        form.win_ratio = self.win_ratio
        return form

class UserForm(messages.Message):
    """User Form."""

    name = messages.StringField(1, required=True)
    email = messages.StringField(2)
    games_played = messages.IntegerField(3, default=0)
    wins = messages.IntegerField(4, default=0)
    win_ratio = messages.FloatField(5, default=0.0)


class UserForms(messages.Message):
    """Return multiple User Forms."""

    items = messages.MessageField(UserForm, 1, repeated=True)
