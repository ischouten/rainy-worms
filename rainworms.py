import os
import logquicky
from flask import Flask, render_template, session, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit
from flask_session import Session
import time
from datetime import datetime

log = logquicky.load("rainworms")

serve_dir = "ui/build/"

app = Flask(
    __name__, static_folder=f"{serve_dir}/static", template_folder=f"{serve_dir}"
)

events = []
players = []

app.config["SECRET_KEY"] = os.environ.get("SESSION_SECRET", "ShouldBeSecret")
app.config["SESSION_TYPE"] = "filesystem"
app.debug = "DEBUG" in os.environ

# Make socketIO use a supported flask session.
Session(app)

socketio = SocketIO(app, cors_allowed_origins="*", manage_session=False,)
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": ["http://localhost:3000"]}},
)


@app.route("/status")
def provide_game_status():
    if session.get("playerName", "") == "":
        inProgress = False
    else:
        inProgress = True

    return jsonify(
        {
            "inProgress": inProgress,
            "playerName": session.get("playerName", ""),
            "events": events,
        }
    )


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("join")
def handle_join(playerName):

    if playerName in players:
        log.Warn(f"Player {playerName} is not unique. Not allowed to join.")
        return
    log.info(f"Received join: {playerName}")
    session["playerName"] = playerName
    log.info(f"After join {session.get('playerName', '')}")


@socketio.on("gameEvnt")
def handle_json(gameEvent):
    log.info(f"Received json: {gameEvent}")

    evnt = format_response(gameEvent)

    # send(evnt, json=True)
    socketio.emit("gameEvnt", evnt)


def format_response(evnt):

    log.info(f"Format: {evnt}")
    response = {
        "id": len(events) + 1,
        "actor": session.get("playerName"),
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
