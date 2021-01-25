import json
import time
import flask
import nlpu
import ticket_generator

app = flask.Flask(__name__)

@app.route("/")
def index():
	return flask.send_from_directory("templates/", "index.html")

@app.route("/css/<stylesheet>")
def css(stylesheet):
	return flask.send_from_directory("templates/css/", stylesheet)

@app.route("/js/<script>")
def js(script):
	return flask.send_from_directory("templates/js/", script)

@app.route("/img/<img>")
def img(img):
	return flask.send_from_directory("templates/img/", img)

@app.route("/favicon.ico")
def favicon():
	return flask.send_from_directory("templates/img/", "icon.png")

def i_dont_understand():
	return "Sorry, I'm not sure I know what you mean. Can you try again?"

def text_message(text):
	return {"type": "text", "content": text}

def ticket_message(ticket):
	return {
		"type": "ticket",
		"from_station": ticket.from_station,
		"to_station": ticket.to_station,
		"leave_at": ticket.leave_at,
		"arrive_at": ticket.arrive_at,
		"travel_time": ticket.travel_time,
		"no_of_changes": ticket.no_changes,
		"price": ticket.price,
		"name": ticket.name,
		"provider": ticket.provider,
		"link": ticket.link
	}

@app.route("/message", methods = ["POST"])
def message():
	msg = flask.request.get_json()

	return json.dumps([text_message(nlpu.process_message(msg))])

app.run()
