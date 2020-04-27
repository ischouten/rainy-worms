import React from "react";

class MessageList extends React.Component {
  render() {
    return (
      <ul className="message-list">
        {this.props.events.map((evt) => {
          return (
            <li key={evt.id}>
              {evt.actor}: {JSON.stringify(evt.action)} (
              {JSON.stringify(evt.result)})
            </li>
          );
        })}
      </ul>
    );
  }
}

export default MessageList;
