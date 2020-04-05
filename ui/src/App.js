import React from "react";
import "./App.css";
import openSocket from "socket.io-client";
import MessageList from "./messageList";

export default class App extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      playerName: "",
      gameEvents: [],
    };

    var domain =
      window.location.protocol +
      "//" +
      window.location.hostname +
      ":" +
      window.location.port;

    if (process.env.NODE_ENV === "development") {
      domain =
        window.location.protocol + "//" + window.location.hostname + ":5000";
      console.log("Connecting to " + domain);
    }

    this.loadStatus(domain);

    this.socket = openSocket(domain);

    this.socket.on("gameEvnt", (gameEvnt) => {
      console.log(
        "RX: " + gameEvnt.id + ", action: " + JSON.stringify(gameEvnt.action)
      );
      this.setState({
        gameEvents: [...this.state.gameEvents, gameEvnt],
      });
    });
  }

  loadStatus = async (domain) => {
    await fetch(domain + "/status", {
      headers: {
        Accept: "application/json",
      },
      credentials: "include",
    })
      .then((response) => response.json())
      .then((json) => {
        console.log("Events: " + JSON.stringify(json));
        this.setState({ gameEvents: json });
      });
  };

  handleChange = (event) => {
    this.setState({ playerName: event.target.value });
  };

  handleSubmit = (event) => {
    event.preventDefault();
    this.socket.emit("join", this.state.playerName);
    console.log("TX: Join: " + this.state.playerName);
  };

  handleRoll = (event) => {
    event.preventDefault();
    var eventMsg = { action: "roll" };
    this.socket.emit("gameEvnt", eventMsg);
    console.log("TX: " + JSON.stringify(eventMsg));
  };

  render() {
    return (
      <div className="App">
        <form onSubmit={this.handleSubmit}>
          <label>
            Name:
            <input
              type="text"
              value={this.state.playerName}
              onChange={this.handleChange}
            />
          </label>
          <input type="submit" value="Submit" />
        </form>
        <button onClick={this.handleRoll}>Roll</button>
        <MessageList id="console" events={this.state.gameEvents} />
      </div>
    );
  }
}
