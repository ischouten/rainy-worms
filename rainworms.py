import os
import logquicky
from flask import Flask, render_template, session, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit
from flask_session import Session
import flask_session
import time
import random, string
from datetime import datetime
import game_engine

log = logquicky.load("rainworms")

serve_dir = "ui/build/"

# Make socketIO use a supported flask session.
app = Flask(
    __name__, static_folder=f"{serve_dir}/static", template_folder=f"{serve_dir}"
)

games = {}
players = {}

app.config["SECRET_KEY"] = os.environ.get("SESSION_SECRET", "ShouldBeSecret")
app.config["SESSION_TYPE"] = "filesystem"
app.config["PERMANENT_SESSION_LIFETIME"] = 600
app.config["SESSION_FILE_THRESHOLD"] = 100
app.debug = "DEBUG" in os.environ

Session(app)

socketio = SocketIO(app, cors_allowed_origins="*", manage_session=False,)
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": ["http://localhost:3000"]}},
)


def randomword(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


@app.route("/status")
def provide_game_status():
    player = session.get("player")
    game_code = session.get("active_game")

    if player:
        log.info(f"Refreshing status for player: {player.name}")

    # Find out which game this player belongs to
    game = games.get(game_code)
    if not game:
        game = game_engine.Game(None, None)

    if not player:
        player = game_engine.Player(None)

    return jsonify({"playerInfo": player.__dict__, "gameInfo": game.__dict__})


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("register")
def handle_register(player_name):
    log.info(f"RX register: {player_name}")

    if player_name in players.keys():
        log.Warn(f"Player {player_name} is not unique. Not allowed to join.")
        return
    player = game_engine.Player(player_name)

    session["player"] = player
    log.info(f"Storing {player.name} into session")
    player.set_status("registered")

    emit("register", {"name": player.name, "status": player.status})
    log.info(f"Registered player: {player.name}")


@socketio.on("join")
def handle_join(join_code):

    log.info(f"Received join: {join_code}")
    log.info(f"Games: {games}")

    player = session.get("player")
    game = games.get(join_code)

    if not game:
        log.error(f"No game with code {join_code}")
        return

    log.info(f"Player joining game: {game.__dict__}")

    if game.players and player.name in game.players:
        log.error(
            f"Player {player.name} already exists. Not allowed to join this game."
        )
        # Todo: Handle message to frontend.
        return

    # Update the game info.
    game = games.get(join_code)

    if not game:
        log.error(f"No game with code {join_code}")
        return

    game.add_player(player)
    session["active_game"] = join_code

    socketio.emit("playerJoin", game.__dict__)


@socketio.on("createGame")
def handle_create(data):
    log.info(data)
    join_code = randomword(4)
    log.info(f"Create new game with gameCode: {join_code}")

    # Find out which player is making this request
    player = session.get("player")

    # Create the new game and register it to the games collection
    game = game_engine.Game(join_code, player)
    game.set_status("waiting")
    games[join_code] = game

    # Store the current game of the player into the session to allow refreshes
    session["active_game"] = join_code

    log.info(
        f"{player.name} created new game with code {game.joinCode}. There is now {len(games)} games."
    )

    emit("createGame", game.__dict__)


@socketio.on("resetUser")
def handle_reset(data):
    log.info(f"Received: {data}")
    session.clear()

    emit("resetPlayer")


@socketio.on("gameEvnt")
def handle_json(gameEvent):
    log.info(f"Received json: {gameEvent}")
    evnt = parse_game_event(gameEvent)
    socketio.emit("gameEvnt", evnt)


def parse_game_event(evnt):

    log.info(f"Format: {evnt}")
    game_code = session.get("game_code")

    if not game_code:
        return

    response = {
        "id": len(games[game_code][events]) + 1,
        "actor": session.get("player_name"),
        "action": evnt.get("action"),
    }

    if evnt.get("action") == "leaveGame":
        log.info("Clearing session")
        session.clear()

    log.info(f"Add: {evnt}")
    events.append(response)

    return response


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", debug=True)
