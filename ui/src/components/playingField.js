import React from "react";

function PlayingField(props) {
  let playerName = props.playerName;
  let onTurn = props.gameInfo.onTurn;

  return (
    <div>
      It's {onTurn}' turn... <br />
      {onTurn === playerName && <button onClick={props.action}>Roll</button>}
    </div>
  );
}

export default PlayingField;
