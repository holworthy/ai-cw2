var messages_div = document.getElementById("messages");
function addMessage(message, side) {
	var message_p = document.createElement("div");
	message_p.classList.add(side);
	message_p.textContent = message;
	messages_div.append(message_p);
	messages_div.scrollTop = messages_div.scrollHeight;
}

var form = document.getElementById("form");
form.addEventListener("submit", (e) => {
	e.preventDefault();

	var messagebox = document.getElementById("messagebox");
	var message = messagebox.value;

	addMessage(message, "right");
	messagebox.value = "";

	var xhr = new XMLHttpRequest();
	xhr.open("POST", "/message");
	xhr.setRequestHeader('Content-Type', 'application/json');
	xhr.addEventListener("load", (e) => {
		addMessage(xhr.responseText, "left");
	});
	xhr.send(JSON.stringify(message));
});

addMessage("Hi, I am trainbot!", "left");
addMessage("How can I help you?", "left");
