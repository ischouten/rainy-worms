import os
import logquicky
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
import time
from datetime import datetime

REDIS_URL = os.environ.get("REDIS_URL", "")
REDIS_CHAN = "rainworms"

log = logquicky.load("rainworms")

serve_dir = "ui/build/"

app = Flask(
    __name__, static_folder=f"{serve_dir}/static", template_folder=f"{serve_dir}"
)

app.secret_key = os.environ.get("SESSION_SECRET", "ShouldBeSecret")
app.debug = "DEBUG" in os.environ

socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/")
def hello():
    return render_template("index.html")


@socketio.on("message")
def handle_message(msg):
    log.info(f"Received messsage: {msg}")


@socketio.on("clickedButton")
def handle_button(message):
    log.info(f"Someone clicked it! {message}")
    emit("welcome", "Welcome, you!")


@socketio.on("json")
def handle_json(json):
    log.info(f"Received json: {json}")
    send(json, json=True)


log.info("Hello!")

if __name__ == "__main__":
    socketio.run(app, debug=True)
