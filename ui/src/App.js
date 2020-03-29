import React from "react";
import "./App.css";
import openSocket from "socket.io-client";

export default class App extends React.Component {
  constructor(props) {
    super(props);

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

    this.socket = openSocket(domain);
    this.socket.on("welcome", (msg) => {
      console.log(msg);
    });
  }

  sendMessage = () => {
    this.socket.emit("clickedButton", "The button was clicked.");
    console.log("Should send message");
  };

  render() {
    return (
      <div className="App">
        <button onClick={this.sendMessage}>Click me</button>
      </div>
    );
  }
}
