var messages_div = document.getElementById("messages");
var form = document.getElementById("form");
var messagebox = document.getElementById("messagebox");

var queue = [];

function addMessage(message, side) {
	var message_div = document.createElement("div");
	message_div.classList.add("message");
	message_div.classList.add(side);
	message_div.classList.add("hide");

	if(message["type"] == "text"){
		message_div.innerHTML = "<p>" + message["content"] + "</p>";
	}

	messages_div.append(message_div);
	messages_div.scrollTop = messages_div.scrollHeight;
	message_div.classList.remove("hide");
}

function textMessage(text) {
	return {
		"type": "text",
		"content": text
	};
}

var queue = [];
var queue_interval = null;
function start_queue(){
	if(queue_interval == null){
		queue_interval = setInterval(() => {
			if(queue.length > 0){
				addMessage(queue.shift(), "left");
			}else{
				clearInterval(queue_interval);
				queue_interval = null;
			}
		}, 1000);
	}
}

queue.push(textMessage("Hi, I am trainbot! 🚂"));
queue.push(textMessage("How can I help you?"));
start_queue();

function doWork(content) {
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "/message");
	xhr.setRequestHeader('Content-Type', 'application/json');
	xhr.addEventListener("load", (e) => {
		var messages = JSON.parse(xhr.responseText);
		for(let i = 0; i < messages.length; i++){
			queue.push(messages[i]);
		}
		start_queue();
	});
	xhr.send(JSON.stringify(content));
}

form.addEventListener("submit", (e) => {
	e.preventDefault();
	var content = messagebox.value;
	doWork(content);
	addMessage(textMessage(content), "right");
	messagebox.value = "";
});

function locate() {
	navigator.geolocation.getCurrentPosition((e) => {
		var xhr = new XMLHttpRequest();
		xhr.addEventListener("load", (e) => {
			var xhr2 = new XMLHttpRequest();
			xhr2.open("POST", "/nearest_station");
			xhr2.setRequestHeader('Content-Type', 'application/json');
			xhr2.addEventListener("load", (e) => {
				messagebox.value = xhr2.response;
			});
			xhr2.send(JSON.stringify(JSON.parse(xhr.response).result[0].postcode));
		});
		xhr.open("GET", "https://api.postcodes.io/postcodes?lon=" + e.coords.longitude + "&lat=" + e.coords.latitude);
		xhr.send();
	});
}
