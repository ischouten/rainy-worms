// Support TLS-specific URLs, when appropriate.
if (window.location.protocol == "https:") {
  var ws_scheme = "wss://";
} else {
  var ws_scheme = "ws://";
}

var inbox = new ReconnectingWebSocket(ws_scheme + location.host + "/receive");
var outbox = new ReconnectingWebSocket(ws_scheme + location.host + "/submit");

inbox.onmessage = function(message) {
  var data = JSON.parse(message.data);

  $("#messages").append(
    $("<span />")
      .text(data.handle)
      .html() +
      $("<span />")
        .text(data.text)
        .html()
  );
};

$("#input-form").on("submit", function(event) {
  console.log("Test");
  event.preventDefault();
  var handle = $("#input-handle")[0].value;
  var text = $("#input-text")[0].value;
  outbox.send(JSON.stringify({ handle: handle, text: text }));
  $("#input-text")[0].value = "";
});
