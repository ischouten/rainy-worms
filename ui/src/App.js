import React from "react";
import "./App.css";
import openSocket from "socket.io-client";
import MessageList from "./messageList";

const defaultState = {
  playerName: "",
  gameEvents: [],
  inProgress: false,
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
        gameEvents: [...this.state.gameEvents, gameEvnt],
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
        console.log("Events: " + JSON.stringify(json));
        this.setState({
          playerName: json.playerName,
          inProgress: json.inProgress,
          gameEvents: json.events,
        });
      });
  };

  handleChange = (event) => {
    this.setState({ playerName: event.target.value });
  };

  handleJoin = (event) => {
    event.preventDefault();
    this.socket.emit("join", this.state.playerName);
    this.setState({ inProgress: true });
    console.log("TX: Join: " + this.state.playerName);
  };

  handleRoll = (event) => {
    event.preventDefault();
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
        {!this.state.inProgress && (
          <form onSubmit={this.handleJoin}>
            <label>
              Name:
              <input
                type="text"
                value={this.state.playerName}
                onChange={this.handleChange}
              />
            </label>
            <input type="submit" value="Join" />
          </form>
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
