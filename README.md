# Hangman

A backend API for the hangman game, built using Google App Engine, Google cloud endpoints, Google datastore and python 2. It allows users to play game, see rankings, scores and history of previous gamses.

To access the API, simply visit https://udacity-hangman.appspot.com\_ah/api/explorer and click on hangman API.

## License information

This project is part of the Udacity Full Stack Web Developper nano degree. It is not licensed.

## Setup instructions

Install google app engine and create an account and a new project.
Install python 2.7.10 on your machine.

Clone the github repository.
Update the value of application in the file `app.yaml` to an app ID that you have registered.

Run the application in the Local Development Server with the following `python` command on the command line.

`dev_appserver.py DIR`

where DIR is the path to the application folder containing the `app.yaml` file.

Browse the hangman API by visiting [localhost:8080/_ah/api/explorer](http://localhost:8080/_ah/api/explorer). 

 
##Game Description:

Hangman is a simple word guessing game. At the start of the game, the computer randomly selects a word (from a very small sample subset).

Each turn, the user has to guess a letter. If the letter is in the word, it is revealed. If not, the user has to guess again.

If the user hasn't guessed the word in a fixed ampount of attempts(9 by default), he loses the game.

Many different Hangman games can be played by many different Users at any given time. Each game can be retrieved or played by using the path parameter `urlsafe_game_key`.

After each game, a score is calculated as follows:
- 10 points for winning the game
- 5 additionnal points per attempts remaining at the end of the game
- 0 points if the player loses

It is possible to access user rankings, previous games and high scores.


##How to play the game

- Create a new user, using the create_user endpoint.
- Use create_game to create a game. Remember to copy the urlsafe_key property for later use.
- Use the make_move endpoint to male moves.
- Use cancel_game to cancel a game in progress. 
- Use get_game, along with the urlsafe_key, to continue an ongoing game.


##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name, attempts
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. Also adds a task to a task queue to update the average moves remaining
    for active games.
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.

 - **get_game_history**
    - Path: 'game/history/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameHistoryForm with current game history.
    - Description: Returns the current history of a game.

 - **cancel_game**
    - Path: 'game/cancel/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state and cancellation status.
    - Description: Cancels a game.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, guess
    - Returns: GameForm with new game state.
    - Description: Accepts a 'guess' and returns the updated state of the game.
    If this causes a game to end, a corresponding Score entity will be created.
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).

 - **get_highscores**
    - Path: 'highscores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database, ordered from highest to lowest.
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.

 - **get_user_games**
    - Path: 'games/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: GameForms. 
    - Description: Returns all of the current user's games
    Will raise a NotFoundException if the User does not exist.

 - **get_user_rankings**
    - Path: 'rankings'
    - Method: GET
    - Parameters: none
    - Returns: UserForms. 
    - Description: Returns users, ranked by their win/loss ratio
    
 - **get_active_game_count**
    - Path: 'games/active'
    - Method: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Gets the average number of attempts remaining for all games
    from a previously cached memcache key.

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    - Stores wins, number of games played, and win ratio
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
    
##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, attempts_remaining,
    game_over flag, message, user_name).
 - **GameForms**
    - Multiple GameForm container.
 - **GameHistoryForm**
    - representation of a Game's history (urlsafe_key, history).
 - **NewGameForm**
    - Used to create a new game (user_name, min, max, attempts)
 - **MakeMoveForm**
    - Inbound make move form (guess).
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, won flag,
    guesses).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.
 - **UserForm**
    - Representation of a user (name, email, games_played, wins, win_ratio).
  - **UserForms**
    - Multiple UserForm container.
