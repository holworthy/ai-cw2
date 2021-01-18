import flask
import time

import ticket_generator
import nlpu

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

def i_dont_understand():
	return "Sorry, I'm not sure I know what you mean. Can you try again?"

@app.route("/message", methods = ["POST"])
def message():
	msg = flask.request.get_json()
	return nlpu.process_message(msg)

app.run()
