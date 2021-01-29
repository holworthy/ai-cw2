import json
import time
import flask
import nlpu
import ticket_generator
from ticket_generator import Station
import re

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
	return json.dumps(nlpu.process_message(msg, ticket_request))

@app.route("/nearest_station", methods = ["POST"])
def nearest_station():
	msg = flask.request.get_json()

	stations = Station.get_stations()
	stations = [station for station in stations if station.get_postcode().startswith(re.findall("^[A-Z]{1,2}", msg)[0])]
	stations.sort(key = lambda x: int(re.findall("^[A-Z]{1,2}([0-9]{1,2})", x.get_postcode())[0]))

	for station in stations:
		if station.get_postcode() == msg:
			return station.get_name()

	for station in stations:
		if station.get_postcode() == msg.split()[0]:
			return station.get_name()

	return stations[0].get_name()

@app.route("/reset", methods = ["POST"])
def reset():
	ticket_request = nlpu.Ticket_Request()
	nlpu.state = "start"
	return ""

ticket_request = nlpu.Ticket_Request()
app.run()
