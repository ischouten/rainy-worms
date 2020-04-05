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

log = logquicky.load("rainworms")

serve_dir = "ui/build/"

# Make socketIO use a supported flask session.
app = Flask(
    __name__, static_folder=f"{serve_dir}/static", template_folder=f"{serve_dir}"
)

games = {}
players = []

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
    player_name = session.get("player_name", "")
    game_code = session.get("game_code", "")

    if session.get("player_name", "") == "":
        inProgress = False
    else:
        inProgress = True

    return jsonify(
        {
            "gameInfo": games.get(game_code, {}),
            "playerInfo": {
                "name": session.get("player_name", ""),
                "registered": session.get("registered", False),
            },
        }
    )


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("register")
def handle_register(player_name):
    if player_name in players:
        log.Warn(f"Player {player_name} is not unique. Not allowed to join.")
        return

    log.info(f"Received register: {player_name}")
    session["player_name"] = player_name
    session["registered"] = True
    emit("register", {"name": player_name, "registered": True})


@socketio.on("join")
def handle_join(player_name):

    if player_name in players:
        log.Warn(f"Player {player_name} is not unique. Not allowed to join.")
        return
    log.info(f"Received join: {player_name}")
    session["player_name"] = player_name
    log.info(f"After join {session.get('player_name', '')}")


@socketio.on("createGame")
def handle_create(data):
    log.info(data)
    game_code = randomword(4)
    log.info(f"Create new game: {game_code}")

    game_info = {
        "gameCode": game_code,
        "players": [session.get("player_name")],
        "inProgress": False,
        "events": [],
    }

    games[game_code] = game_info
    session["game_code"] = game_code

    emit("createGame", game_info)


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
