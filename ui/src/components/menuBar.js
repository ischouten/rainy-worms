import React from "react";

function menuBar(props) {
  return <div>You are: {props.player.name ? props.player.name : ""}</div>;
}

export default menuBar;
