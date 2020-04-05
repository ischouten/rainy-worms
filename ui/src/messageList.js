import React from "react";

class MessageList extends React.Component {
  render() {
    return (
      <ul className="message-list">
        {this.props.events.map((evt) => {
          return (
            <li key={evt.id}>
              <div>{evt.actor}</div>
              <div>{JSON.stringify(evt.action)}</div>
            </li>
          );
        })}
      </ul>
    );
  }
}

export default MessageList;
