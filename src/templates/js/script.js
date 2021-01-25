var messages_div = document.getElementById("messages");
var form = document.getElementById("form");

function addMessage(message, side) {
	var message_div = document.createElement("div");
	message_div.classList.add("message");
	message_div.classList.add(side);

	if(message["type"] == "text"){
		message_div.innerHTML = "<p>" + message["content"] + "</p>";
	}

	messages_div.append(message_div);
	messages_div.scrollTop = messages_div.scrollHeight;
}

function textMessage(text) {
	return {
		"type": "text",
		"content": text
	};
}

function doWork(content) {
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "/message");
	xhr.setRequestHeader('Content-Type', 'application/json');
	xhr.addEventListener("load", (e) => {
		var messages = JSON.parse(xhr.responseText);
		for(var i = 0; i < messages.length; i++)
			addMessage(messages[i], "left");
	});
	xhr.send(JSON.stringify(content));
}

form.addEventListener("submit", (e) => {
	e.preventDefault();

	var messagebox = document.getElementById("messagebox");
	var content = messagebox.value;
	doWork(content);
	addMessage(textMessage(content), "right");
	messagebox.value = "";
});

addMessage(textMessage("Hi, I am trainbot!"), "left");
addMessage(textMessage("How can I help you?"), "left");
