from flask import jsonify


class Player:
    def __init__(self, player_name: str):
        self.name: str = player_name
        self.status: str = "new"  # joining, joined

    def set_status(self, new_status: str):
        self.status = new_status


class Game:
    def __init__(self, join_code: str, player: Player):

        self.players: list = []
        self.host = None
        if player:
            self.players.append(player.name)
            self.host: str = player.name

        self.joinCode: str = join_code
        self.status: str = None
        self.events: list = []

    def add_player(self, player: Player):
        self.players.append(player.name)

    def set_status(self, new_status: str):
        self.status = new_status

    def start_game(self):
        self.status = "started"
        # Pick a turn for someone.
