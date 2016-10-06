from protorpc import messages
from google.appengine.ext import ndb

class Score(ndb.Model):
    """Score object."""

    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    score = ndb.IntegerProperty(required=True, default=0)

    def to_form(self):
        """Return a form representation of the score."""
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=str(self.date), score=self.score)

class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information."""

    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    score = messages.IntegerField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms."""

    items = messages.MessageField(ScoreForm, 1, repeated=True)
