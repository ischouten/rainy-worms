import os
import logquicky
from flask import Flask, session, render_template, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit
import time
from datetime import datetime

log = logquicky.load("rainworms")

serve_dir = "ui/build/"

app = Flask(
    __name__, static_folder=f"{serve_dir}/static", template_folder=f"{serve_dir}"
)

events = []

app.secret_key = os.environ.get("SESSION_SECRET", "ShouldBeSecret")
app.debug = "DEBUG" in os.environ

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": ["http://localhost:3000"]}},
)


@app.route("/status")
def provide_game_status():
    return jsonify(events)


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("join")
def handle_join(playerName):
    log.info(f"Received join: {playerName}")
    session["playerName"] = playerName


@socketio.on("gameEvnt")
def handle_json(gameEvent):
    log.info(f"Received json: {gameEvent}")

    evnt = {
        "id": len(events) + 1,
        "actor": session.get("playerName"),
        "action": gameEvent,
    }
    events.append(evnt)

    send(evnt, json=True)
    socketio.emit("gameEvnt", evnt)


if __name__ == "__main__":
    socketio.run(app, debug=True)
