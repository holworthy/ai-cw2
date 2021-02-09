var messages_div = document.getElementById("messages");
var form = document.getElementById("form");
var messagebox = document.getElementById("messagebox");
var chatbot_img = document.getElementById("chatbot_img");

// adds a message to the screen
function addMessage(message, side) {
	var message_div = document.createElement("div");
	message_div.classList.add("message");
	message_div.classList.add(side);
	message_div.classList.add("hide");

	if(message["type"] == "text"){
		message_div.innerHTML = "<p>" + message["content"] + "</p>";
	}else if(message["type"] == "ticket"){
		let ticket = message["content"],
			from = ticket["from_station"],
			to = ticket["to_station"],
			leave_at = ticket["leave_at"],
			link = ticket["link"];
		message_div.innerHTML = "<p><b>" + from + "</b> to <b>" + to + "</b> leaving at <b>" + leave_at + "</b></p><p><a href=\"" + link + "\">Book Here</a></p>";
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

// magic
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

// add the initial messages to the screen queue
queue.push(textMessage("Hi, I am trainbot! 🚂"));
queue.push(textMessage("How can I help you?"));
// empty the queue to the screen
start_queue();

form.addEventListener("submit", (e) => {
	e.preventDefault();
	var content = messagebox.value;
	chatbot_img.src = "/img/Chatbot_Processing_2.gif";
	// send users message to server
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "/message");
	xhr.setRequestHeader('Content-Type', 'application/json');
	xhr.addEventListener("load", (e) => {
		// get server response
		var response = JSON.parse(xhr.responseText);
		var messages = response["message"];
		for(let i = 0; i < messages.length; i++){
			// add server messages to the queue of messages to be added to screen
			queue.push(messages[i]);
		}
		// start adding server messages to the screen one by one
		start_queue();
		var state = response["state"];
		if(state == "start" || state == "end"){
			setTimeout(()=>{chatbot_img.src = "/img/Chatbot_Happy.svg"}, 1000);
		}
		else if(state == "would_you_like_to_book" || state == prevstate){
			setTimeout(()=>{chatbot_img.src = "/img/Chatbot_Confused.svg"}, 1000);
		}
		else{
			setTimeout(()=>{chatbot_img.src = "/img/Chatbot_basic.svg"}, 1000);
		}
		prevstate = state;
	});
	xhr.send(JSON.stringify(content));

	// add users message to screen
	addMessage(textMessage(content), "right");
	messagebox.value = "";

	
});

// function locate() {
// 	navigator.geolocation.getCurrentPosition((e) => {
// 		var xhr = new XMLHttpRequest();
// 		xhr.addEventListener("load", (e) => {
// 			var xhr2 = new XMLHttpRequest();
// 			xhr2.open("POST", "/nearest_station");
// 			xhr2.setRequestHeader('Content-Type', 'application/json');
// 			xhr2.addEventListener("load", (e) => {
// 				messagebox.value = xhr2.response;
// 			});
// 			xhr2.send(JSON.stringify(JSON.parse(xhr.response).result[0].postcode));
// 		});
// 		xhr.open("GET", "https://api.postcodes.io/postcodes?lon=" + e.coords.longitude + "&lat=" + e.coords.latitude);
// 		xhr.send();
// 	});
// }

var prevstate = null;
var xhr = new XMLHttpRequest();
xhr.open("POST", "/reset");
xhr.send();
