import os
import logquicky
import redis
import gevent
from flask import Flask, render_template
from flask_sockets import Sockets

REDIS_URL = os.environ.get("REDIS_URL", "")
REDIS_CHAN = "rainworms"

log = logquicky.load("rainworms")

app = Flask(__name__)
app.debug = "DEBUG" in os.environ

sockets = Sockets(app)
redis = redis.from_url(REDIS_URL)


class GameBackend(object):
    """ Interface for registering and updaing WebSocket clients. """

    def __init__(self):
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN)

    def __iter_data(self):
        for message in self.pubusb.listen():
            data = message.get("data")
            if message["type"] == "message":
                log.info(f"Sending messsage: {data}")
                yield data

    def register(self, client):
        """ Register a WebSocket connection for Redis updates """
        self.clients.append(client)

    def send(self, client, data):
        """ Send given data to the registered client.
        Automatically discards invalid connections. """

        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        """ Listens for new messages in Redis and sends them to clients. """

        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        """ Maintains Redis subscription in the background. """
        gevent.spawn(self.run)


@app.route("/")
def hello():
    return render_template("index.html")


@sockets.route("/submit")
def inbox(ws):
    """ Receives incoming messages, inserts them into Redis. """
    while not ws.closed:
        # Sleep to prevent *constant* context-switches
        gevent.sleep(0.1)
        message = ws.receive()

        if message:
            log.info(f"Inserting message: {message}")
            redis.public(REDIS_CHAN, message)


@sockets.route("receive")
def outbox(ws):
    """ Sends outgoing messages via GameBackend. """

    games.register(ws)
    while not ws.closed:
        # Context switch while `GameBackend.start` is running in the background.
        gevent.sleep(0.1)


if __name__ == "__main__":
    log.info("Hello!")

    games = GameBackend()
    games.start()
