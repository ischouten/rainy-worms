import React from "react";
import "./App.css";
import openSocket from "socket.io-client";
import MessageList from "./components/messageList";
import MenuBar from "./components/menuBar";
import PlayingField from "./components/playingField";

const defaultState = {
  playerInfo: {
    name: "",
    status: "new",
  },
  gameInfo: {
    status: "new",
    joinCode: null,
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

    this.socket.on("register", (e) => {
      this.setState({
        playerInfo: e,
      });
    });

    this.socket.on("playerJoin", (e) => {
      this.setState({
        gameInfo: e,
      });
    });

    this.socket.on("createGame", (e) => {
      console.log("RX: " + JSON.stringify(e));
      this.setState({
        gameInfo: e,
      });
    });

    this.socket.on("gameStarted", (e) => {
      console.log("RX: " + JSON.stringify(e));
      this.setState({
        gameInfo: e,
      });
    });

    this.socket.on("gameEvent", (e) => {
      console.log("RX: " + JSON.stringify(e));

      this.setState({
        gameInfo: e,
      });
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
          playerInfo: json.playerInfo,
          gameInfo: json.gameInfo,
        });
      });
  };

  handleNameChange = (e) => {
    let newPlayerName = this.state.playerInfo.name;
    newPlayerName = e.target.value;

    const prevState = this.state;
    prevState.playerInfo.name = newPlayerName;
    this.setState(prevState);
  };

  handleRegister = (e) => {
    e.preventDefault();

    const playerName = this.state.playerInfo.name;

    let newState = this.state.playerInfo;
    newState["status"] = "registering";
    this.socket.emit("register", playerName);
  };

  handleCreate = (e) => {
    e.preventDefault();
    this.socket.emit("createGame", { action: "createGame" });
    console.log("TX: Create game");
  };

  handleJoinGame = (e) => {
    e.preventDefault();
    console.log("TX: Join: " + this.state.gameInfo.joinCode);
    this.socket.emit("join", this.state.gameInfo.joinCode);
  };

  handleStartGame = (e) => {
    e.preventDefault();
    console.log("TX: Starting game");
    this.socket.emit("startGame");
  };

  handeJoinCodeChange = (e) => {
    e.preventDefault();
    console.log("Setting join code to " + e.target.value);
    let prevGameInfo = this.state.gameInfo;
    prevGameInfo["joinCode"] = e.target.value;
    this.setState({ gameInfo: prevGameInfo });
    console.log(JSON.stringify(this.state));
  };

  handleReset = (e) => {
    console.log("Resetting state");
    let newState = this.state.defaultState;
    this.setState(newState);
    this.socket.emit("resetUser", { action: "resetUser" });
    this.loadStatus();
  };

  handleTurn = (e) => {
    console.log(this.state.playerInfo.name + " rolled the dice...");
    var eventMsg = { action: "roll" };
    this.socket.emit("playerEvent", eventMsg);
    console.log("TX: " + JSON.stringify(eventMsg));
  };

  handleLeave = (e) => {
    this.socket.emit("gameEvnt", { action: "leaveGame" });
    console.log("TX: Leave Game");
    this.setState({ defaultState });
  };

  render() {
    return (
      <div className="App">
        <MenuBar player={this.state.playerInfo} />
        {this.state.playerInfo.status === "new" && (
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

        {this.state.playerInfo.status === "registered" &&
          !this.state.gameInfo.status && (
            <div>
              <button onClick={this.handleCreate}>Create new game</button>
              <form onSubmit={this.handleJoinGame}>
                <label>Game code:</label>
                <input
                  type="text"
                  value={this.state.joinCode}
                  onChange={this.handeJoinCodeChange}
                />
                <input type="submit" value="Join game" />
              </form>
            </div>
          )}

        {this.state.gameInfo.status === "waiting" && (
          <div>
            Game code: {this.state.gameInfo.joinCode}
            <br />
            Waiting for players to join...
            <br />
            <br />
            <div>
              Players:
              <ul>
                {this.state.gameInfo.players.map((playerName) => (
                  <li key={playerName}>{playerName}</li>
                ))}
              </ul>
            </div>
            <br />
            {this.state.playerInfo &&
              this.state.gameInfo.host === this.state.playerInfo.name && (
                <button onClick={this.handleStartGame}>Start</button>
              )}
          </div>
        )}

        {this.state.gameInfo.status === "started" && (
          <div>
            <MessageList id="console" events={this.state.gameInfo.events} />
            <PlayingField
              gameInfo={this.state.gameInfo}
              playerName={this.state.playerInfo.name}
              action={this.handleTurn}
            />
          </div>
        )}

        <div>
          <button onClick={this.handleReset}>Reset</button>
        </div>
      </div>
    );
  }
}
