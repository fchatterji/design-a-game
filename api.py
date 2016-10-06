# -*- coding: utf-8 -*-`

"""api.py.

This file contains the hangman API. It defines the responses made
to API requests.
"""

import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache, taskqueue
import datetime

from game import (
    Game,
    StringMessage,
    NewGameForm,
    GameForm,
    MakeMoveForm,
    GameForms,
    GameHistoryForm
)

from score import (
    Score, 
    ScoreForms
)

from user import (
    User, 
    UserForm, 
    UserForms
)

from utils import get_by_urlsafe

from game_logic import (
    find_all_indexes, 
    calculate_score, 
    update_user
)

NEW_GAME_REQUEST = endpoints.ResourceContainer(
    NewGameForm
)

GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1)
)

MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1)
)

USER_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1),
    email=messages.StringField(2)
)

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'


@endpoints.api(name='hangman', version='v1')
class HangmanApi(remote.Service):
    """Game API."""

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=UserForm,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User.

        Args:
            request: The USER_REQUEST objects, which includes a users
                chosen name and an optional email.
        Returns:
            UserForm: a representation of the newly created user.
        Raises:
            endpoints.ConflictException: If the user already exists.
        """
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!'
            )

        user = User(name=request.user_name, email=request.email)
        user.put()

        return user.to_form()


    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Create a new game.

        Args:
            request: The NEW_GAME_REQUEST objects, which includes
            the name of the user and, optionnally, the number of
            allowed attempts
        Returns:
            GameForm: a representation of the created game
        Raises:
            endpoints.NotFoundException: If the user's name doesn't exist.
        """
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')

        game = Game.new_game(user.key, request.attempts)
        game.history.append('Game created')

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        taskqueue.add(url='/tasks/cache_average_attempts')
        return game.to_form('Good luck playing hangman!')


    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the state of a game.

        Args:
            request: The GET_GAME_REQUEST objects, which includes
            the unique key of the game.
        Returns:
            GameForm: a representation of the requested game
        Raises:
            endpoints.NotFoundException: If the game doesn't exist.
        """
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        if game:
            return game.to_form()
        else:
            raise endpoints.NotFoundException('Game not found!')


    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameHistoryForm,
                      path='game/history/{urlsafe_game_key}',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return the history of a game.

        Args:
            request: The GET_GAME_REQUEST object, which includes
            the unique key of the game.
        Returns:
            GameHistoryForm: a representation of the history of
            the requested game, as a list of strings detailing
            the flow of the game.
        Raises:
            endpoints.NotFoundException: If the game doesn't exist.
        """
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_history_form()
        else:
            raise endpoints.NotFoundException('Game not found!')


    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/cancel/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
        """Cancel a game.

        Args:
            request: The GET_GAME_REQUEST object, which includes
            the unique key of the game.
        Returns:
            GameForm: a representation of the requested game, cancelled.
        Raises:
            endpoints.NotFoundException: if the game doesn't exist.
            endpoints.ForbiddenException: if the game is already finished.
        """
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game and not game.game_over:
            game.history.append("game cancelled")
            game.put()
            return game.to_form('You have canceled the game')

        if game and game.game_over:
            raise endpoints.ForbiddenException('Illegal action:'
                                               'Game is already over.')
        else:
            raise endpoints.NotFoundException('Game not found!')


    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/move/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Make a move in the game.

        Args:
            request: MAKE_MOVE_REQUEST object, which includes
            the guess of the user. The guess mst include only letters.
            The user is allowed to try to guess the whole word directly.
        Returns:
            GameForm: a representation of the requested game, after the move.
        Raises:
            endpoints.ForbiddenException: if the game is already finished.
            endpoints.BadRequestException: if user doesn't input letters, has
            already tried the guess or enters nothing.
        """

        """ Input validation"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        if game.game_over:
            raise endpoints.ForbiddenException('Illegal action:'
                                               'Game is already over.')

        elif len(request.guess) == 0:
            raise endpoints.BadRequestException('Please enter a letter!')

        elif not(request.guess.isalpha()):
            raise endpoints.BadRequestException('Only letters are allowed :)')

        elif request.guess in game.guessed_word:
            raise endpoints.BadRequestException('You have already'
                                                ' tried this letter :)')

        """ Game flow"""
        guess_is_correct = False
        secret_word = game.secret_word
        guessed_word = game.guessed_word
        guess = request.guess.lower()

        """The user guesses the whole word correctly"""
        if guess == secret_word:
            game.guessed_word = secret_word
            score = calculate_score(game.attempts_remaining, True)
            score = Score(user=game.user, date=datetime.date.today(), won=True,
                          score=score)
            score.put()

            update_user(game.user.get(), True)
            game.history.append('Guessed {}, game won, this was'
                                ' the secret word!'.format(guess))
            game.game_over = True
            game.put()
            return game.to_form('You win!')


        positions = find_all_indexes(secret_word, guess)

        """ The user guesses one letter."""
        if positions:
            guess_is_correct = True

            for position in positions:
                game.guessed_word = (guessed_word[:position] +
                                     guess +
                                     guessed_word[position + 1:])

        else:
            guess_is_correct = False
            game.attempts_remaining -= 1

        if guessed_word == secret_word:
            score = calculate_score(game.attempts_remaining, True)
            score = Score(user=game.user, date=datetime.date.today(), won=True,
                          score=score)
            score.put()

            update_user(game.user.get(), True)

            game.history.append('Guessed: {}, game won. The secret'
                                'word was {}'.format(guess, secret_word))
            game.game_over = True
            game.put()
            return game.to_form('You win!')

        if game.attempts_remaining < 1:
            score = calculate_score(game.attempts_remaining, True)
            score = Score(user=game.user, date=datetime.date.today(), won=True,
                          score=score)
            score.put()

            update_user(game.user.get(), True)

            game.history.append('Guessed: {}, game won. The secret'
                                'word was {}'.format(guess, secret_word))
            game.game_over = True
            game.put()
            return game.to_form('No attempts remaining, you lost :(')
        else:
            game.history.append('Guessed: {}, which is {}. {} attempts '
                                'remaining'.format(guess,
                                                   guess_is_correct,
                                                   game.attempts_remaining))
            game.put()
            return game.to_form('play again!')


    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Get all the scores.

        Args:
            No args
        Returns:
            ScoreForms: a representation of all scores.
        """
        return ScoreForms(items=[score.to_form() for score in Score.query()])


    @endpoints.method(response_message=ScoreForms,
                      path='highscores',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """Get all the scores, in decreasing order.

        Args:
            No args
        Returns:
            ScoreForms: a representation of all scores, in decreasing order.
        """
        query = Score.query().order(-Score.score)
        items = [score.to_form() for score in query]
        return ScoreForms(items=items)


    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Get the scores for one user.

        Args:
            request: USER_REQUEST object, which includes a users
                chosen name and an optional email.
        Returns:
            ScoreForms: a representation of the scores for the requested user.
        Raises:
            endpoints.NotFoundException: if the user does't exist.
        """
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')

        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])


    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='games/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Get the games for one user.

        Args:
            request: USER_REQUEST object, which includes a users
                chosen name and an optional email.
        Returns:
            GameForms: a representation of the games for the requested user.
        Raises:
            endpoints.NotFoundException: if the user does't exist.
        """
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')

        games = Game.query(Game.user == user.key)
        return GameForms(items=[game.to_form() for game in games])


    @endpoints.method(response_message=UserForms,
                      path='rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Get the users, ranked by win/loss ratio.

        Args:
            No args.
        Returns:
            UserForms: a representation of users, ranked by
            their win/loss ratio.
        """
        users = User.query().fetch()
        users = sorted(users, key=lambda x: x.win_ratio, reverse=True)
        return UserForms(items=[user.to_form() for user in users])


    @endpoints.method(response_message=StringMessage,
                      path='games/average_attempts',
                      name='get_average_attempts_remaining',
                      http_method='GET')
    def get_average_attempts(self, request):
        """Get the average attemps remaining for all users.

        Args:
            No args.
        Returns:
            StringMessage: a string
        """
        return StringMessage(message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')


    @staticmethod
    def _cache_average_attempts():
        """Populate memcache with the average moves remaining of Games."""
        games = Game.query(Game.game_over == False).fetch()
        if games:
            count = len(games)
            total_attempts_remaining = sum([game.attempts_remaining for game in games])
            average = float(total_attempts_remaining) / count
            memcache.set(
                MEMCACHE_MOVES_REMAINING,
                'The average moves remaining is {:.2f}'.format(average))


api = endpoints.api_server([HangmanApi])
