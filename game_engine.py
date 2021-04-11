from flask import session
import logquicky
import random
import string

log = logquicky.load("rainworms")


class GamesController:
    def __init__(self):
        self.games = {}
        self.players = {}

    def get_game(self, join_code):
        game = self.games.get(join_code)
        if not game:
            game = Game(None, None)

        return game

    def player_exists(self, player_name: str) -> bool:
        if player_name in self.players.keys():
            return True
        return False

    def create_game(self):
        # Find out which player is making this request
        player = session.get("player")

        if not player:
            log.error("cannot create game without registering as player first.")
            return

        join_code = self.__create_join_code(4)

        log.info(f"Creating new game with gameCode: {join_code}")

        # Create the new game and register it to the games collection
        game = Game(join_code, player)
        game.set_status("waiting")

        self.games[join_code] = game

        log.info(
            f"{player.name} created new game with code {game.join_code}. There is now {len(self.games)} games."
        )
        return game

    def __create_join_code(self, length):
        letters = string.ascii_lowercase
        return "".join(random.choice(letters) for i in range(length))


class Player:
    def __init__(self, player_name: str):
        self.name: str = player_name
        self.status: str = "new"  # joining, joined

    def __repr__(self):
        return f"{self.name}"

    def set_status(self, new_status: str):
        self.status = new_status


class Game:
    def __init__(self, join_code: str, player: Player):

        self.players: list = []
        self.host = None
        if player:
            self.players.append(player.name)
            self.host: str = player.name

        self.join_code: str = join_code
        self.status: str = None
        self.events: list = []
        self.on_turn: str = None

    def __repr__(self):
        return f"{self.join_code} with players: {self.players}"

    def as_dict(self):
        return {
            "joinCode": self.join_code,
            "status": self.status,
            "events": self.events,
            "onTurn": self.on_turn,
            "host": self.host,
            "players": self.players,
        }

    def add_player(self, player: Player):
        log.info(f"Adding player {player.name}")
        self.players.append(player.name)
        log.info(f"Players: {self.players}")

    def set_status(self, new_status: str):
        self.status = new_status

    def start(self):
        self.status = "started"

        # Pick a turn for someone.
        self.update_on_turn_player()
        return

    def update_on_turn_player(self):
        if not self.on_turn:
            log.info(f"Noone had the turn. Picking random player from {self.players}")

            # Randomize the player list so that its not in the order of joining
            random.shuffle(self.players)
            log.info(f"Shuffled players: {self.players}")
            self.on_turn = random.choice(self.players)

        else:
            index = self.players.index(self.on_turn)

            self.on_turn = (
                self.players[0]
                if (index + 1 == len(self.players))
                else self.players[index + 1]
            )
        log.info(f"Player {self.on_turn} has the turn")

        return

    def parse_event(self, game_event, player: Player):

        log.info(f"Event: {game_event} from {player}")

        if not player.name == self.on_turn:
            log.warning(f"Event came in but it's not {player.name}'s turn")
            return

        action = game_event.get("action")
        result = None
        if action == "roll":
            result = self.__roll_dice(7)

        parsed_event = {
            "id": len(self.events) + 1,
            "actor": player.name,
            "action": game_event.get("action"),
            "result": result,
        }

        log.info(f"Add: {game_event}")
        self.events.append(parsed_event)

        self.update_on_turn_player()
        return

    def __roll_dice(self, amount: int) -> list:

        dice_options = [1, 2, 3, 4, 5, 6]
        result = [random.choice(dice_options) for i in range(amount)]

        return result
