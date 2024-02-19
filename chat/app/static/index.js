let ws = new WebSocket('ws://' + window.location.host + '/ws/');

function showMessage(message) {
	let messages = $('#messages');
	let height = 0;
	let now = new Date().toLocaleTimeString("en-US", {hour12: false});

	messages.append($('<div>').html('[' + now + '] ' + message + '\n'));
	messages.find('div').each((i, value) => {
		height += parseInt($(this).height());
	});

	messages.animate({scrollTop: height});
}

ws.onmessage = event => {
	let data = JSON.parse(event.data);
	switch (data.action) {
		case "register":
			showMessage(data.username + " registered.");
			let oldContent = $("#registered-users").html();
			let newContent = data.username + ", " + oldContent;
			$("#registered-users").html(newContent);
			break;
		case "connect":
			showMessage(data.username + " connected.");
			break;
		case "disconnect":
			showMessage(data.username + " disconnected.");
			break;
		case "send":
			showMessage(data.username + ": " + data.text);
			break;
	}
}
ws.onclose = event => showMessage("The connection is broken.");
ws.onerror = error => console.log(error);

function sendMessage() {
	let input = $('#message-input');
	let val = $.trim(input.val());
	if (val) {
		ws.send(val);
		input.val("").focus();
	}
}

$('#send-message-button').click(sendMessage);
$('#message-input').keyup((e) => {
	if(e.keyCode == 13) {
		sendMessage();
	}
});
