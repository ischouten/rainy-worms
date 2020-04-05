import React from "react";

function menuBar(props) {
  console.log(props);
  return <div>You are: {props.player.name ? props.player.name : "Noone"}</div>;
}

export default menuBar;
