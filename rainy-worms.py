import os
import logquicky
from flask import Flask, render_template, session, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_session import Session
import game_engine

log = logquicky.load("rainworms")

serve_dir = "ui/build/"

# Make socketIO use a supported flask session.
app = Flask(
    __name__, static_folder=f"{serve_dir}/static", template_folder=f"{serve_dir}"
)

app.config["SECRET_KEY"] = os.environ.get("SESSION_SECRET", "ShouldBeSecret")
app.config["SESSION_TYPE"] = "filesystem"
app.config["PERMANENT_SESSION_LIFETIME"] = 600
app.config["SESSION_FILE_THRESHOLD"] = 100
app.debug = "DEBUG" in os.environ

Session(app)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    manage_session=False,
)
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": ["http://localhost:3000"]}},
)

games_controller = game_engine.GamesController()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/status")
def provide_game_status():
    player = session.get("player")
    join_code = session.get("active_code")

    if player:
        log.info(f"Refreshing status for player: {player.name}")
    else:
        player = game_engine.Player(None)

    game = games_controller.get_game(join_code)

    return jsonify({"playerInfo": player.__dict__, "gameInfo": game.as_dict()})


@socketio.on("register")
def handle_register(player_name):
    log.info(f"RX register request: {player_name}")

    if games_controller.player_exists(player_name):
        log.Warn(f"Player {player_name} is not unique. Not allowed to join.")
        return

    # Register a new player
    player = game_engine.Player(player_name)

    # Store this player in his session
    player.set_status("registered")
    session["player"] = player

    # Notify other players
    emit("register", {"name": player.name, "status": player.status})
    log.info(f"Registered player: {player.name}")


@socketio.on("createGame")
def handle_create(data):
    log.info(data)

    # Store the current game of the player into the session to allow refreshes
    game = games_controller.create_game()
    log.info(f"The game: {game}")
    session["active_code"] = game.join_code

    emit("createGame", game.as_dict())


@socketio.on("join")
def handle_join(join_code):

    log.info(f"Received join: {join_code}")

    player = session.get("player")
    log.info(player)
    if not player:
        log.error("First register a player before joining.")
        return

    game = games_controller.get_game(join_code)
    if not game:
        log.error(f"No game with code {join_code}")
        return

    log.info(f"Player {player.name} joining game: {game.as_dict()}")

    game.add_player(player)
    session["active_code"] = join_code

    socketio.emit("playerJoin", game.as_dict())


@socketio.on("startGame")
def handle_start():
    player = session.get("player")

    active_code = session.get("active_code")
    game = games_controller.get_game(active_code)

    if not player or not game:
        log.error("Player or game does not exist.")
        return

    if game.host != player.name:
        log.error("Only the host can start a game.")

    game.start()

    log.info("RX start")
    socketio.emit("gameStarted", game.as_dict())


@socketio.on("resetUser")
def handle_reset(data):
    log.info(f"Received reset request: {data}")
    session.clear()

    emit("resetPlayer")
    # TODO: Notify other players if a player leaves.
    # socketio.emit("playerLeft", game.as_dict())


@socketio.on("playerEvent")
def handle_json(gameEvent):
    log.info(f"Received json: {gameEvent}")

    join_code = session.get("active_code")
    game = games_controller.get_game(join_code)
    player = session.get("player")

    game_event = game.parse_event(gameEvent, player)
    log.info(f"Parsed: {game_event}")

    socketio.emit("gameEvent", game.as_dict())


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", debug=True)
