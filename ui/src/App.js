import React from "react";
import "./App.css";
import openSocket from "socket.io-client";
import MessageList from "./components/messageList";
import MenuBar from "./components/menuBar";

const defaultState = {
  playerInfo: {
    name: "",
    registered: false,
  },
  gameInfo: {
    gameCode: "",
    events: [],
    inProgress: false,
  },
};

var domain =
  window.location.protocol +
  "//" +
  window.location.hostname +
  ":" +
  window.location.port;

if (process.env.NODE_ENV === "development") {
  domain = window.location.protocol + "//" + window.location.hostname + ":5000";
  console.log("Connecting to " + domain);
}

export default class App extends React.Component {
  constructor(props) {
    super(props);

    this.state = defaultState;
  }

  componentDidMount = () => {
    this.socket = openSocket(domain);
    this.loadStatus();
    this.setState(defaultState);

    console.log("State: " + JSON.stringify(this.state));

    this.socket.on("gameEvnt", (gameEvnt) => {
      console.log(
        "RX: " + gameEvnt.id + ", action: " + JSON.stringify(gameEvnt.action)
      );
      this.setState({
        gameEvents: [...this.state.gameInfo.events, gameEvnt],
      });
    });

    this.socket.on("register", (e) => {
      console.log("RX: " + JSON.stringify(e));
      this.setState({
        playerInfo: e,
      });
      console.log("New state: " + JSON.stringify(this.state));
    });

    this.socket.on("createGame", (e) => {
      console.log("RX: " + JSON.stringify(e));
      this.setState({
        gameInfo: e,
      });
      console.log("New state: " + JSON.stringify(this.state));
    });
  };

  loadStatus = async () => {
    await fetch(domain + "/status", {
      headers: {
        Accept: "application/json",
      },
      credentials: "include",
    })
      .then((response) => response.json())
      .then((json) => {
        console.log("Loading status after refresh: \n" + JSON.stringify(json));
        this.setState({
          gameInfo: json.gameInfo,
          playerInfo: json.playerInfo,
        });
      });
  };

  handleNameChange = (e) => {
    let newState = this.state.playerInfo;
    newState["name"] = e.target.value;
    this.setState(newState);
  };

  handleRegister = (e) => {
    e.preventDefault();
    const playerName = this.state.playerInfo.name;
    console.log("Registering player: " + playerName);
    this.socket.emit("register", playerName);
  };

  handleCreate = (e) => {
    e.preventDefault();
    this.socket.emit("createGame", { action: "createGame" });
    console.log("TX: Create game");
  };

  handleJoin = (event) => {
    event.preventDefault();
    this.socket.emit("join", this.state.gameCode);
    console.log("TX: Join: " + this.state.gameCode);
  };

  handleRoll = (e) => {
    e.preventDefault();
    var eventMsg = { action: "roll" };
    this.socket.emit("gameEvnt", eventMsg);
    console.log("TX: " + JSON.stringify(eventMsg));
  };

  handleLeave = (event) => {
    this.socket.emit("gameEvnt", { action: "leaveGame" });
    console.log("TX: Leave Game");
    this.setState({ defaultState });
  };

  render() {
    return (
      <div className="App">
        <MenuBar player={this.state.playerInfo} />
        {!this.state.playerInfo.registered && (
          <form onSubmit={this.handleRegister}>
            <label>
              Name:
              <input
                type="text"
                value={this.state.playerName}
                onChange={this.handleNameChange}
              />
            </label>
            <input type="submit" value="Register" />
          </form>
        )}

        {this.state.playerInfo.registered && !this.state.gameInfo.gameCode && (
          <div>
            <button onClick={this.handleCreate}>Create new game</button>
            <form onSubmit={this.handleJoinGame}>
              <label>Game code:</label>
              <input
                type="text"
                value={this.state.gameCode}
                onChange={this.handeGameCodeChange}
              />
            </form>
            <input type="submit" value="Join game" />
          </div>
        )}

        {this.state.gameInfo.gameCode && (
          <div>
            Game code: {this.state.gameInfo.gameCode}
            <br />
            Waiting for players to join...
            <div>Players: {this.state.gameInfo.players}</div>
            <br />
            Start game.
          </div>
        )}

        {this.state.inProgress && (
          <div>
            <MessageList id="console" events={this.state.gameEvents} />
            <button onClick={this.handleRoll}>Roll</button>
            <button onClick={this.handleLeave}>Leave</button>
          </div>
        )}
      </div>
    );
  }
}
