#!/usr/bin/env python

"""main.py

This file contains handlers that are called by taskqueue and/or
cronjobs.
"""

import webapp2
from google.appengine.api import mail, app_identity
from api import HangmanApi

from models import User, Game


class SendReminderEmail(webapp2.RequestHandler):
    """Request handler to send reminder emails."""

    def get(self):
        """Send a reminder email to each User with an email about games.

        Called every hour using a cron job
        """
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)
        for user in users:
            games = Game.query(Game.user == user.key, Game.game_over == False)
            if games.count() == 0:
                continue

            for game in games:
                subject = 'This is a reminder!'
                body = 'Hello {}, you have an unfinished game at {1}.appspot.com!'.format(user.name, app_id)
                # This will send test emails, the arguments to send_mail are:
                # from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                               user.email,
                               subject,
                               body)


class UpdateAverageMovesRemaining(webapp2.RequestHandler):
    """Request handler to get the average moves remaining."""

    def post(self):
        """Update game listing announcement in memcache."""
        HangmanApi._cache_average_attempts()
        self.response.set_status(204)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/cache_average_attempts', UpdateAverageMovesRemaining),
], debug=True)
